#!/usr/bin/env python3
"""
Fusion Existing Browser Multi-Trade Auto-Fill
============================================

Ziel:
- Verbindet sich mit BEREITS LAUFENDEM Chrome (Bitpanda Fusion Session schon eingeloggt)
- Sucht automatisch den Fusion / Bitpanda Tab
- Lädt automatisch die NEUSTE Datei: TODAY_ONLY_trades_*.csv (Semikolon getrennt)
- Trägt ALLE Trades nacheinander ein (Open -> BUY, Close -> SELL)
- Wählt Limit Order, füllt Menge & Limit Preis
- SENDET NICHT automatisch (letzter Klick bleibt bei Ihnen)
- Zwischen Trades optional automatische Weiterfahrt (konfigurierbar)

Verwendung:
  python fusion_existing_all_trades_auto.py

Voraussetzungen:
  1. Chrome läuft bereits MIT Ihrer eingeloggten Bitpanda Fusion Session
  2. (Optimal) Chrome wurde mit --remote-debugging-port=9222 gestartet
     Falls nicht, startet das Skript eine Debug-Instanz und verbindet sich
  3. Datei(en) TODAY_ONLY_trades_*.csv existieren im gleichen Ordner

Hinweis Sicherheit:
  Der Versand der Orders erfolgt NICHT automatisch. Sie prüfen & senden selbst.

Erstellt: 12. August 2025
"""
import os, re, sys, glob, time, math, traceback, importlib
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
import pandas as pd  # hinzugefügt

# --- Konfiguration / Defaults (über ENV überschreibbar) -----------------
def _env_flag(*names, default='0'):
    for n in names:
        v = os.getenv(n)
        if v is not None:
            return v
    return default

# Unterstützung sowohl ohne als auch mit FUSION_ Prefix
AUTO_CONTINUE = _env_flag('AUTO_CONTINUE','FUSION_AUTO_CONTINUE', default='1') not in ('0','false','False')
WAIT_BETWEEN = float(_env_flag('WAIT_BETWEEN','FUSION_WAIT','FUSION_WAIT_BETWEEN', default='2.5'))
AUTO_SUBMIT = _env_flag('AUTO_SUBMIT','FUSION_AUTO_SUBMIT', default='0') in ('1','true','True')
USE_REALTIME_LIMIT = _env_flag('USE_REALTIME_LIMIT','FUSION_REALTIME_LIMIT', default='1') in ('1','true','True')
PORTFOLIO_CHECK = _env_flag('PORTFOLIO_CHECK','FUSION_PORTFOLIO_CHECK', default='1') in ('1','true','True')
DEBUG_MODE = _env_flag('DEBUG_MODE','FUSION_DEBUG', default='0') in ('1','true','True')
MAX_WAIT = float(_env_flag('MAX_WAIT','FUSION_MAX_WAIT', default='15'))
DEEP_INPUT_DEBUG = _env_flag('DEEP_INPUT_DEBUG','FUSION_DEEP_INPUT_DEBUG', default='0') in ('1','true','True')
MIN_INPUT_COUNT = int(_env_flag('MIN_INPUT_COUNT','FUSION_MIN_INPUTS', default='1'))  # Mindestanzahl Input-Felder bevor gefüllt wird
AGGRESSIVE_IFRAME_SCAN = _env_flag('AGGRESSIVE_IFRAME_SCAN','FUSION_AGGRESSIVE_IFRAME', default='1') in ('1','true','True')
SLOW_KEYSTROKES = _env_flag('SLOW_KEYSTROKES','FUSION_SLOW_KEYS', default='0') in ('1','true','True')
ORDER_FRAME_KEYWORDS = _env_flag('ORDER_FRAME_KEYWORDS','FUSION_ORDER_FRAME_KEYS', default='menge,amount,preis,price,limit,kaufen,verkaufen')
STRICT_FIELD_MATCH = _env_flag('STRICT_FIELD_MATCH','FUSION_STRICT_FIELD_MATCH', default='1') in ('1','true','True')
WAIT_FOR_CLICK = _env_flag('WAIT_FOR_CLICK','FUSION_WAIT_FOR_CLICK', default='1') in ('1','true','True')
PRICE_COMMIT_VERIFY = _env_flag('PRICE_COMMIT_VERIFY','FUSION_PRICE_COMMIT_VERIFY', default='0') in ('1','true','True')  # optional strenge Verifikation
TAB_NAV = _env_flag('TAB_NAV','FUSION_TAB_NAV','USE_TAB_NAV', default='1') in ('1','true','True')  # Verwende explizite TAB Sequenz Navigation
USE_MAX_BUTTON = _env_flag('USE_MAX_BUTTON','FUSION_USE_MAX', default='1') in ('1','true','True')
USE_BPS_BUTTONS = _env_flag('USE_BPS_BUTTONS','FUSION_USE_BPS', default='1') in ('1','true','True')
PAPER_MODE = _env_flag('PAPER_MODE','FUSION_PAPER_MODE', default='0') in ('1','true','True')  # Paper: kein finaler Review Klick, Reset statt Absenden
SAFE_PREVIEW_MODE = _env_flag('SAFE_PREVIEW_MODE','FUSION_SAFE_PREVIEW_MODE', default='0') in ('1','true','True')  # Nur anzeigen, niemals Review klicken
# Zusatzschutz: Bei SELL muss ein Bestätigungstext eingegeben werden (standard aktiv)
FORCE_SELL_TYPING = _env_flag('FORCE_SELL_TYPING','FUSION_FORCE_SELL_TYPING', default='1') in ('1','true','True')
INCLUDE_LAST_DAYS = int(_env_flag('INCLUDE_LAST_DAYS','FUSION_INCLUDE_LAST_DAYS', default='0'))  # 0 = nur heute, 1 = heute + gestern, ...
LOG_SKIPPED_TRADES = _env_flag('LOG_SKIPPED_TRADES','FUSION_LOG_SKIPPED_TRADES', default='0') in ('1','true','True')
TRADES_FILE = _env_flag('TRADES_FILE','FUSION_TRADES_FILE', default='').strip()  # explizit bestimmte Datei statt auto newest
DUMP_FILTER_DEBUG = _env_flag('DUMP_FILTER_DEBUG','FUSION_DUMP_FILTER_DEBUG', default='0') in ('1','true','True')
if INCLUDE_LAST_DAYS != 0:
    # Strikte Vorgabe: nur aktueller Tag erlaubt
    print("ℹ️ INCLUDE_LAST_DAYS überschrieben auf 0 (Policy: nur heutiger Tag)")
    INCLUDE_LAST_DAYS = 0
BACKTEST_MODE = _env_flag('BACKTEST_MODE','FUSION_BACKTEST_MODE','FUSION_MODE', default='0').lower() in ('1','true','backtest')

# ---- Benutzer-Schnell-Overrides (einfach True/False setzen, None = ignorieren) ----
USER_OVERRIDES = {
    # 'AUTO_CONTINUE': False,
    # 'WAIT_FOR_CLICK': True,
    # 'SAFE_PREVIEW_MODE': True,   # Aktivieren um JEDE Order nur vorzufüllen
    # 'PAPER_MODE': True,          # Verhindert versehentliche Live-Aktionen
    # 'DISABLE_SELLS': True,       # Komplett alle SELLs blockieren
}
for k,v in list(USER_OVERRIDES.items()):
    if v is None: continue
    if k in globals():
        globals()[k] = v

# --- Sicherheits-Flags gegen unbeabsichtigte Verkäufe ---
DISABLE_SELLS = _env_flag('DISABLE_SELLS','FUSION_DISABLE_SELLS', default='0') in ('1','true','True')
SELL_CONFIRM = _env_flag('SELL_CONFIRM','FUSION_SELL_CONFIRM', default='1') in ('1','true','True')  # standard: Schutz an
SELL_WHITELIST = set([s.strip().upper() for s in _env_flag('SELL_WHITELIST','FUSION_SELL_WHITELIST', default='').split(',') if s.strip()])  # leere => kein Filter
MAX_SELL_FRACTION = float(_env_flag('MAX_SELL_FRACTION','FUSION_MAX_SELL_FRACTION', default='1.0'))  # 1.0 = alles erlaubt
STRICT_SELL_PRICE_PROTECT = float(_env_flag('STRICT_SELL_PRICE_PROTECT','FUSION_STRICT_SELL_PRICE_PROTECT', default='0'))  # z.B. 0.05 => Preis max 5% unter Markt
STRICT_EUR_ONLY = _env_flag('STRICT_EUR_ONLY','FUSION_STRICT_EUR_ONLY', default='1') in ('1','true','True')  # Erzwinge ausschließlich *-EUR Paare

# Asset Rundungsregeln (kann bei Bedarf erweitert werden)
ASSET_DECIMALS = {
    'BTC': 6,
    'ETH': 5,
    'SOL': 4,
    'DOGE': 0,
    'XRP': 1,
    'ADA': 1,
    'DOT': 2,
}

# Hilfsfunktion: Hole initialCapitalLong und order_round_factor aus crypto_tickers
def compute_buy_quantity(pair: str, limit_price: float) -> float:
    try:
        base = pair.split('-')[0].upper()
        # dynamischer Import ohne Caching-Effekte (falls Datei bearbeitet)
        spec = importlib.util.spec_from_file_location('crypto_tickers', os.path.join(os.path.dirname(__file__), 'crypto_tickers.py'))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
        else:
            import crypto_tickers as mod  # fallback
        cfg = getattr(mod, 'CRYPTO_TICKERS', getattr(mod, 'crypto_tickers', None))
        if cfg is None:
            # Datei definiert evtl. direkt ein Dict
            # Versuche top-level Variablen zu inspizieren
            cfg = {k:v for k,v in mod.__dict__.items() if isinstance(v, dict) and k.lower().startswith(base.lower())}
        # Standardstruktur: Dict keyed by 'BTC-EUR'
        entry = cfg.get(pair) if isinstance(cfg, dict) else None
        if not entry and isinstance(cfg, dict):
            # evt. key ohne EUR
            entry = cfg.get(base)
        initial_cap = None
        round_factor = None
        if entry and isinstance(entry, dict):
            initial_cap = entry.get('initialCapitalLong') or entry.get('initial_capital') or entry.get('initialCapital')
            round_factor = entry.get('order_round_factor') or entry.get('orderRoundFactor')
        if initial_cap is None:
            initial_cap = 1000.0
        if round_factor is None:
            # fallback heuristik pro asset
            rf_map = {'BTC':0.001,'ETH':0.01,'SOL':0.1,'DOGE':10.0,'XRP':10.0,'ADA':10.0,'DOT':0.1}
            round_factor = rf_map.get(base, 0.001)
        qty = initial_cap / max(float(limit_price), 1e-9)
        # Rundung auf round_factor (Down)
        try:
            if round_factor >= 1:
                qty = math.floor(qty / round_factor) * round_factor
            else:
                steps = math.floor(qty / round_factor)
                qty = steps * round_factor
        except Exception:
            pass
        # Abschließende Dezimalrundung via ASSET_DECIMALS
        qty = round_asset_amount(base, qty)
        return qty
    except Exception as e:
        if DEBUG_MODE:
            print(f"⚠️ compute_buy_quantity Fehler: {e}")
        return 0.0

def round_asset_amount(symbol: str, amount: float) -> float:
    try:
        d = ASSET_DECIMALS.get(symbol.upper(), 6)
        q = Decimal(str(amount)).quantize(Decimal('1.' + ('0'*d)), rounding=ROUND_DOWN)
        return float(q)
    except Exception:
        return float(amount)

# Datei-Suche: ausschließlich TODAY_ONLY Dateien (saubere Vorgabe)
def find_latest_today_file(prefix: str = "TODAY_ONLY_trades_"):
    files = glob.glob(f"{prefix}*.csv")
    if not files:
        # alternative einfache Namen zulassen
        files = glob.glob("TODAY_ONLY*.csv")
    if not files:
        return None
    def extract_ts(fn):
        m = re.search(r"_(\d{8}_\d{6})", fn)
        if m:
            try:
                return datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
            except Exception:
                return datetime.min
        return datetime.fromtimestamp(os.path.getmtime(fn))
    files.sort(key=extract_ts, reverse=True)
    return files[0]

# --- Selenium Installation / Imports -------------------------------------------------

def ensure_selenium():
    global By, WebDriverWait, EC, Keys
    try:
        from selenium import webdriver  # noqa
        from selenium.webdriver.common.by import By as _By
        from selenium.webdriver.support.ui import WebDriverWait as _WW
        from selenium.webdriver.support import expected_conditions as _EC
        from selenium.webdriver.common.keys import Keys as _Keys
        By, WebDriverWait, EC, Keys = _By, _WW, _EC, _Keys
        return True
    except ImportError:
        print('📦 Installiere selenium...')
        os.system(f"{sys.executable} -m pip install --quiet selenium")
        try:
            from selenium import webdriver  # noqa
            from selenium.webdriver.common.by import By as _By
            from selenium.webdriver.support.ui import WebDriverWait as _WW
            from selenium.webdriver.support import expected_conditions as _EC
            from selenium.webdriver.common.keys import Keys as _Keys
            By, WebDriverWait, EC, Keys = _By, _WW, _EC, _Keys
            print('✅ Selenium installiert')
            return True
        except Exception:
            print('❌ Selenium Installation fehlgeschlagen')
            return False

# --- CSV / Trade Loader bleibt unverändert bis auf bereits vorhandene Änderungen ...existing code...

class TradeLoader:
    REQUIRED_COLUMNS = [
        'Date','Ticker','Quantity','Price','Order Type','Limit Price','Open/Close','Realtime Price Bitpanda'
    ]

    def __init__(self):
        self.trades = []
        self.source_file = None
    def load(self):
        """Lädt die neueste TODAY_ONLY_trades_*.csv, filtert nur HEUTE & erlaubte Ticker.
        Rückgabe: True bei Erfolg, sonst False."""
        self.source_file = TRADES_FILE if TRADES_FILE else find_latest_today_file()
        if TRADES_FILE and self.source_file and not os.path.basename(self.source_file).upper().startswith('TODAY_ONLY'):
            print(f"⚠️ Angegebene Datei '{self.source_file}' ist keine TODAY_ONLY_* Datei – nur heutige Zeilen werden trotzdem gefiltert.")
        if not self.source_file:
            print("❌ Keine TODAY_ONLY_trades_*.csv Datei gefunden")
            return False
        print(f"📄 Lade Trades aus: {self.source_file}")
        try:
            df = pd.read_csv(self.source_file, delimiter=';')
        except Exception as e:
            print(f"❌ CSV Ladefehler: {e}")
            return False
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            print(f"❌ Fehlende Spalten: {missing}")
            return False
        if df.empty:
            print("❌ Datei enthält keine Zeilen")
            return False
        if DUMP_FILTER_DEBUG:
            print(f"ℹ️ Spalten: {list(df.columns)} | Zeilen: {len(df)}")
            try:
                print(df.head(3))
            except Exception:
                pass
        self.trades.clear()
        today = datetime.now().date()
        cutoff = today - pd.Timedelta(days=INCLUDE_LAST_DAYS)
        # Normalisierte Listen für Skip-Logging
        # erlaubte Ticker Liste aus crypto_tickers laden
        try:
            from crypto_tickers import crypto_tickers as _ct_cfg
            allowed_pairs = {k.upper() for k in _ct_cfg.keys()}
        except Exception:
            allowed_pairs = set()
        if DUMP_FILTER_DEBUG:
            print(f"ℹ️ Erlaubte Ticker (importiert): {sorted(list(allowed_pairs))[:20]}{' ...' if len(allowed_pairs)>20 else ''}")
        skip_stats = {
            'date_range':0,
            'date_unparseable':0,
            'not_allowed':0,
            'not_eur':0,
            'other':0
        }
        for idx, row in df.iterrows():
            try:
                action = 'BUY' if str(row['Open/Close']).strip().lower() == 'open' else 'SELL'
                quantity = float(row['Quantity'])
                limit_price = float(row['Limit Price'])
                realtime_price = None
                try:
                    realtime_price = float(row.get('Realtime Price Bitpanda', float('nan')))
                except Exception:
                    pass
                order_value = quantity * limit_price
                pair = str(row['Ticker']).strip()
                # Normalisierung: Unterstriche -> Bindestrich
                pair = pair.replace('_','-')
                # Früher Skip wenn kein EUR oder USD enthalten
                if STRICT_EUR_ONLY and ('USD' in pair.upper()):
                    skip_stats['not_eur'] += 1
                    if LOG_SKIPPED_TRADES or DUMP_FILTER_DEBUG:
                        print(f"   ⏭️ Skip {pair} (USD erkannt – STRICT_EUR_ONLY aktiv) -> {row.to_dict()}")
                    continue
                # Robust Date Parse
                date_field_raw = str(row['Date']).strip()
                date_norm = None
                try:
                    # Entferne Zeit falls vorhanden
                    core = date_field_raw.split('T')[0].strip()
                    # Ersetze mögliche '.' durch '-'
                    if '.' in core and core.count('.')==2:
                        # dd.mm.yyyy -> yyyy-mm-dd
                        parts = core.split('.')
                        if len(parts)==3:
                            core = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    date_norm = pd.to_datetime(core).date()
                except Exception:
                    skip_stats['date_unparseable'] += 1
                    if LOG_SKIPPED_TRADES or DUMP_FILTER_DEBUG:
                        print(f"   ⏭️ Skip Zeile {idx} (Datum unparsebar: {date_field_raw}) -> {row.to_dict()}")
                    continue
                if not BACKTEST_MODE:
                    # Strikter heutiger Tag
                    if date_norm != today:
                        skip_stats['date_range'] += 1
                        if LOG_SKIPPED_TRADES or DUMP_FILTER_DEBUG:
                            print(f"   ⏭️ Skip {pair} (Datum {date_norm} != heute {today}) -> {row.to_dict()}")
                        continue
                # Filter: Nur erlaubte Ticker falls Liste vorhanden
                if allowed_pairs and pair.upper() not in allowed_pairs:
                    skip_stats['not_allowed'] += 1
                    if LOG_SKIPPED_TRADES or DUMP_FILTER_DEBUG:
                        print(f"   ⏭️ Skip {pair} (nicht in erlaubten Ticker-Liste) -> {row.to_dict()}")
                    continue
                # Filter: Nur EUR Paare (USD versehentliche) -> skip
                if not pair.upper().endswith('-EUR'):
                    skip_stats['not_eur'] += 1
                    if LOG_SKIPPED_TRADES or DUMP_FILTER_DEBUG:
                        print(f"   ⏭️ Skip {pair} (Nicht -EUR / möglicher Fehl-Ticker) -> {row.to_dict()}")
                    continue
                trade = {
                    'id': idx + 1,
                    'pair': pair,
                    'crypto': pair.split('-')[0],
                    'action': action,
                    'quantity': quantity,
                    'limit_price': limit_price,
                    'realtime_price': realtime_price,
                    'order_value': order_value,
                    'date': date_norm,
                    'raw': row.to_dict()
                }
                self.trades.append(trade)
            except Exception as e:
                skip_stats['other'] += 1
                print(f"⚠️ Zeile {idx} übersprungen: {e}")
        if not self.trades:
            print("❌ Keine gültigen Trades extrahiert")
            if DUMP_FILTER_DEBUG:
                print(f"📊 Skip-Statistik: {skip_stats}")
            return False
        if DUMP_FILTER_DEBUG:
            print(f"📊 Skip-Statistik: {skip_stats}")
        if BACKTEST_MODE:
            print(f"✅ {len(self.trades)} Backtest-Trades geladen (alle Daten, Datumsfilter deaktiviert)")
        else:
            print(f"✅ {len(self.trades)} Trades (nur heute) geladen (Open => BUY, Close => SELL)")
        total_buy = sum(t['order_value'] for t in self.trades if t['action']=='BUY')
        total_sell = sum(t['order_value'] for t in self.trades if t['action']=='SELL')
        print(f"   🟢 BUY Gesamt:  €{total_buy:,.2f}".replace(',', ' '))
        print(f"   🔴 SELL Gesamt: €{total_sell:,.2f}".replace(',', ' '))
        print(f"   💵 Netto:       €{(total_sell-total_buy):,.2f}".replace(',', ' '))
        return True

# ---------------------------------------------------------------------------
# Browser Attachment & Automation
# ---------------------------------------------------------------------------
class FusionExistingAutomation:
    def __init__(self, auto_continue=True, wait_between=2.5, auto_submit=False):
        # Laufsteuerung
        self.auto_continue = auto_continue
        self.wait_between = wait_between
        self.auto_submit = auto_submit
        # Selenium / Zustand
        self.driver = None
        self.attached = False
        self.cached_holdings = {}  # symbol -> available qty
        self._page_initialized = False
        self._last_pair = None
        self._last_qty_element = None
        self._last_price_element = None
        # Safe Preview Steuerflags
        self.abort_all = False   # q -> sofortiger Gesamtabbruch
        self.skip_rest = False   # s -> keine weiteren Trades mehr

    def attach_or_start_debug_chrome(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print('🔗 Verbinde mit laufendem Chrome/Edge (Port 9222)...')
        def build_options(remove_exclude=False):
            o = Options()
            o.add_experimental_option('debuggerAddress','127.0.0.1:9222')
            if not remove_exclude:
                try:
                    o.add_experimental_option('excludeSwitches',["enable-automation"])  # kann bei manchen Versionen Fehler werfen
                except Exception:
                    pass
            o.add_argument('--disable-blink-features=AutomationControlled')
            return o
        # 1. Versuch mit excludeSwitches
        for attempt in (0,1):
            try:
                options = build_options(remove_exclude = (attempt==1))
                self.driver = webdriver.Chrome(options=options)
                self.attached = True
                print('✅ Verbindung hergestellt')
                return True
            except Exception as e:
                print(f'⚠️ Attach Versuch {attempt+1} fehlgeschlagen: {e}')
        # Versuche Edge (falls Nutzer Edge benutzt)
        try:
            from selenium.webdriver.edge.options import Options as EdgeOptions
            eo = EdgeOptions()
            eo.add_experimental_option('debuggerAddress','127.0.0.1:9222')
            self.driver = webdriver.Edge(options=eo)
            self.attached = True
            print('✅ Verbindung über Edge hergestellt')
            return True
        except Exception:
            pass
        print('➡️ Starte neue Chrome Debug Instanz (Login evtl. nötig)...')
        if sys.platform.startswith('win'):
            os.system('start "FusionDebug" chrome --remote-debugging-port=9222 --user-data-dir="%TEMP%\\fusion_debug_profile"')
        else:
            os.system('google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/fusion_debug_profile &')
        time.sleep(5)
        for attempt in (0,1):
            try:
                options = build_options(remove_exclude = (attempt==1))
                self.driver = webdriver.Chrome(options=options)
                self.attached = True
                print('✅ Neue Debug Instanz verbunden (bitte einloggen).')
                return True
            except Exception as e:
                print(f'⚠️ Neuer Attach Versuch {attempt+1} fehlgeschlagen: {e}')
        print('❌ Keine Verbindung möglich')
        return False

    # --- Hilfen ----------------------------------------------------------
    def _wait(self, condition_fn, timeout=None, interval=0.4, desc=''):  # einfache Poll-Wait
        timeout = timeout or MAX_WAIT
        start = time.time()
        while time.time() - start < timeout:
            try:
                if condition_fn():
                    return True
            except Exception:
                pass
            time.sleep(interval)
        if desc:
            print(f'   ⏱️ Timeout: {desc}')
        return False

    def dump_debug(self, label):
        if not DEBUG_MODE or not self.driver:
            return
        try:
            fn = f'fusion_debug_{label}_{int(time.time())}.html'
            with open(fn,'w',encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f'   🐞 Debug HTML gespeichert: {fn}')
        except Exception:
            pass

    def find_fusion_tab(self):  # erweitern: falls kein Tab -> navigiere
        print('🔍 Suche Fusion / Bitpanda Tab...')
        found = False
        for handle in self.driver.window_handles:
            try:
                self.driver.switch_to.window(handle)
                url = (self.driver.current_url or '').lower()
                title = (self.driver.title or '').lower()
                if any(k in url for k in ['fusion','bitpanda']) or any(k in title for k in ['fusion','bitpanda']):
                    found = True
                    print(f'✅ Tab: {self.driver.title}')
                    break
            except Exception:
                continue
        if not found:
            print('⚠️ Kein Tab gefunden – navigiere direkt zu Fusion...')
            try:
                self.driver.get('https://web.bitpanda.com/fusion')
                time.sleep(5)
                found = True
            except Exception:
                pass
        if not found:
            input('➡️ Bitte Fusion manuell öffnen und ENTER drücken...')
        return True

    def switch_into_relevant_iframe(self):
        # Versuche iFrame (falls Order UI in iframe) – heuristik
        switched = False
        try:
            frames = self.driver.find_elements(By.TAG_NAME,'iframe')
            for i, fr in enumerate(frames):
                try:
                    src = (fr.get_attribute('src') or '').lower()
                    if any(k in src for k in ['fusion','trade','order','exchange']):
                        self.driver.switch_to.frame(fr)
                        print(f'   🔄 In iframe gewechselt ({i}) src~{src[:40]}')
                        return True
                except Exception:
                    continue
            if AGGRESSIVE_IFRAME_SCAN:
                # Tiefensuche: wechsle nacheinander in jedes Frame und prüfe auf bekannte Keywords im Body
                for i, fr in enumerate(frames):
                    try:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(fr)
                        bodytxt = ''
                        try:
                            bodytxt = (self.driver.find_element(By.TAG_NAME,'body').text or '')[:800].lower()
                        except Exception:
                            pass
                        if any(k in bodytxt for k in ['menge','amount','limit','preis','price','kaufen','verkaufen']):
                            print(f"   🔄 Aggressiv in iframe ({i}) aufgrund Texttreffer")
                            switched = True
                            return True
                    except Exception:
                        continue
                # falls nichts blieb: wieder zurück zum main content
                self.driver.switch_to.default_content()
        except Exception:
            pass
        return switched

    # ---- Neuer Kontext-Finder für Order-Form anstelle blindem Chart-iFrame Betreten ----
    def locate_order_context(self):
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass
        try:
            keywords = [k.strip().lower() for k in ORDER_FRAME_KEYWORDS.split(',') if k.strip()]
        except Exception:
            keywords = ['menge','amount','preis','price','limit','kaufen','verkaufen']
        best = {'score': -1, 'index': None, 'reason': 'default'}
        frames = []
        try:
            frames = self.driver.find_elements(By.TAG_NAME,'iframe')
        except Exception:
            pass
        # Prüfe zuerst Default Content
        try:
            body_txt = ''
            try:
                body_txt = (self.driver.find_element(By.TAG_NAME,'body').text or '')[:3000].lower()
            except Exception:
                pass
            score = sum(3 for k in keywords if k in body_txt)
            # Inputs count
            try:
                in_count = len(self.driver.find_elements(By.TAG_NAME,'input'))
            except Exception:
                in_count = 0
            score += in_count
            # Bonus wenn Buttons Kaufen / Verkaufen vorhanden
            if re.search(r'kaufen|verkaufen|buy|sell', body_txt):
                score += 5
            best = {'score': score, 'index': None, 'reason': f'default inputs={in_count}'}
        except Exception:
            pass
        # Jetzt Frames scoren
        for i, fr in enumerate(frames):
            try:
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame(fr)
                # Erkennung TradingView Frame -> überspringen
                is_chart = False
                try:
                    # Schnelle Heuristik: base href auf tradingview / class chart-page
                    is_chart = 'charting_library' in (fr.get_attribute('src') or '').lower()
                    if not is_chart:
                        html_snip = (self.driver.page_source or '')[:1000].lower()
                        if 'tradingview' in html_snip or 'chart-page' in html_snip:
                            is_chart = True
                except Exception:
                    pass
                if is_chart:
                    if DEBUG_MODE:
                        print(f"   🔎 Frame {i} als TradingView erkannt – übersprungen")
                    continue
                body_txt = ''
                try:
                    body_txt = (self.driver.find_element(By.TAG_NAME,'body').text or '')[:4000].lower()
                except Exception:
                    pass
                input_count = len(self.driver.find_elements(By.TAG_NAME,'input'))
                ce_count = len(self.driver.find_elements(By.XPATH, '//*[@contenteditable="true"]'))
                kw_hits = sum(3 for k in keywords if k in body_txt)
                score = kw_hits + input_count + ce_count
                if re.search(r'kaufen|verkaufen|buy|sell', body_txt):
                    score += 5
                if score > best['score']:
                    best = {'score': score, 'index': i, 'reason': f'kw={kw_hits} inputs={input_count} ce={ce_count}'}
                if DEBUG_MODE:
                    print(f"   🧪 Frame {i} score={score} details kw={kw_hits} inputs={input_count} ce={ce_count}")
            except Exception:
                continue
        # Anwenden der besten Wahl
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass
        if best['index'] is not None and best['score'] >= 1:
            try:
                self.driver.switch_to.frame(frames[best['index']])
                print(f"   🔄 Order-Kontext gewechselt -> Frame {best['index']} ({best['reason']}, score={best['score']})")
                return True
            except Exception as e:
                print(f"   ⚠️ Wechsel zu Frame {best['index']} misslungen: {e}")
                return False
        else:
            # Default Content bleibt
            if DEBUG_MODE:
                print(f"   🧷 Bleibe im Default Content (score={best['score']}, reason={best.get('reason')})")
            return True

    def ensure_trade_page(self, trade):
        # Lade die Seite nur EINMAL (verhindert ständiges Reset / Restart)
        base = 'https://web.bitpanda.com/fusion'
        if not self._page_initialized:
            try:
                cur = (self.driver.current_url or '').lower()
            except Exception:
                cur = ''
            if 'bitpanda' not in cur or 'fusion' not in cur:
                try:
                    self.driver.get(base)
                    time.sleep(4)
                except Exception:
                    pass
            self._page_initialized = True
        # Kein Reload pro Pair – wir wählen nur das Symbol im UI
        self._last_pair = trade.get('pair')
        # Statt blindem iframe Wechsel: gezielt Order-Kontext bestimmen (richtigen Order-Form Kontext wählen)
        try:
            self.locate_order_context()
        except Exception:
            if DEBUG_MODE:
                print("   ⚠️ locate_order_context() Aufruf fehlgeschlagen")

    # --- Klick & Eingabe Utilities erweitern ----------------------------
    def _try_click_selectors(self, selectors, description, required=False):
        from selenium.common.exceptions import StaleElementReferenceException
        for sel in selectors:
            try:
                el = None
                if sel.startswith('//'):
                    el = self.driver.find_element(By.XPATH, sel)
                else:
                    el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if not el.is_displayed():
                    continue
                try:
                    el.click()
                except Exception:
                    self.driver.execute_script('arguments[0].click();', el)
                print(f'   ✅ {description} via {sel}')
                return True
            except StaleElementReferenceException:
                time.sleep(0.2); continue
            except Exception:
                continue
        if required:
            print(f'   ⚠️ {description} nicht gefunden')
            self.dump_debug(description.replace(' ','_'))
        return False

    def js_fill(self, el, value):
        try:
            self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", el, str(value))
            return True
        except Exception:
            return False

    # Einheitlicher Setter (auch für contenteditable / Shadow Elemente)
    def _set_element_value(self, el, value):
        try:
            tag = el.tag_name.lower()
        except Exception:
            tag = 'input'
        if tag == 'input':
            try:
                el.click()
            except Exception:
                pass
            try:
                el.clear()
            except Exception:
                pass
            try:
                el.send_keys(Keys.CONTROL,'a'); el.send_keys(str(value)); return True
            except Exception:
                pass
            return self.js_fill(el, value)
        # contenteditable oder anderes Element
        try:
            self.driver.execute_script("try{arguments[0].focus();}catch(e){}; arguments[0].innerText=arguments[1]; arguments[0].textContent=arguments[1]; arguments[0].dispatchEvent(new Event('input',{bubbles:true})); arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", el, str(value))
            return True
        except Exception:
            return False

    # --- Feld Identifikation (Menge vs. Preis) --------------------------
    def _identify_order_fields(self):
        """Versucht Menge (qty) und Limit/Preis Felder stabil zu identifizieren.
        Markiert gefundene Felder mit data-auto-tag Attribut zur Wiederverwendung.
        Rückgabe: dict qty=<webelement|None>, price=<webelement|None>"""
        script = r"""
        const OUT={qty:null, price:null, debug:[]};
        function lower(x){ return (x==null?'':String(x)).toLowerCase(); }
        function safePrevText(el){ try{ const p=el.previousElementSibling; if(!p) return ''; return (p.innerText||''); }catch(e){ return ''; } }
        function attr(el, name){ try{ return el.getAttribute(name)||''; }catch(e){ return ''; } }
        function score(el){
           let s={qty:0, price:0, total:0};
           const meta = [attr(el,'placeholder'), attr(el,'aria-label'), attr(el,'name'), attr(el,'id'), el.className||'', el.innerText||'', attr(el,'data-testid')].join(' ').toLowerCase();
           const prevTxt = lower(safePrevText(el));
           const parentTxt = lower((()=>{try{ return el.parentElement ? (el.parentElement.innerText||'').slice(0,80):'';}catch(e){return ''}})());
           const full = meta+' '+prevTxt+' '+parentTxt;
           const qtyTokens=['menge','anzahl','amount','qty','quantity','größe','size','volumen','vol','qty'];
           const priceTokens=['preis','price','limit','px','orderpx','limitpreis'];
           qtyTokens.forEach(t=>{ if(full.includes(t)) s.qty+=3; });
           priceTokens.forEach(t=>{ if(full.includes(t)) s.price+=3; });
           if(/orderqty/.test(full)) s.qty+=5;
           if(/orderpx|limitprice|limitpreis/.test(full)) s.price+=6;
           if(/suche|search/.test(full)){ s.qty-=5; s.price-=5; }
           const im = lower(attr(el,'inputmode')+' '+attr(el,'type'));
           if(/decimal|numeric|number/.test(im)){ s.qty+=1; s.price+=1; }
           if((el.className||'').length>60){ s.qty-=1; s.price-=1; }
           try { const rect = el.getBoundingClientRect(); if(rect.top>300){ s.price+=0.5; } } catch(e){}
           s.total = s.qty + s.price;
           return s;
        }
        const rawInputs=[...document.querySelectorAll('input')];
        const extraCE=[...document.querySelectorAll('[contenteditable="true"]')];
        const rawAll=[...rawInputs, ...extraCE];
        const candidates=rawAll.filter(i=>!i.disabled && i.type!=='hidden' && i.offsetParent && !/checkbox|radio|range|color|file|button|submit/i.test((i.type||'')));
        const scored=candidates.map(el=>{ const s=score(el); return {el,s}; });
        scored.sort((a,b)=> b.s.total - a.s.total);
        let bestQty=null, bestPrice=null;
        for(const c of scored){ if(!bestQty || c.s.qty > bestQty.s.qty){ bestQty=c; } }
        for(const c of scored){ if(!bestPrice || c.s.price > bestPrice.s.price){ bestPrice=c; } }
        if(!bestPrice || bestPrice.s.price < 2){
            const pxCand = candidates.find(i=>/(orderpx|limitprice|limitpreis)/i.test(i.id+i.name+i.className));
            if(pxCand){ bestPrice = {el:pxCand, s:score(pxCand)}; }
        }
        if(bestQty && bestPrice && bestQty.el===bestPrice.el){
            if(bestQty.s.qty >= bestPrice.s.price){ bestPrice=null; } else { bestQty=null; }
        }
        OUT.debug.push('candidates=' + scored.length);
        scored.slice(0,6).forEach(c=>{
            const id = c.el.id||''; const nm=c.el.name||''; const cls=(c.el.className||'').split(' ').slice(0,3).join('.');
            OUT.debug.push(`id:${id}|name:${nm}|cls:${cls}|qty:${c.s.qty}|price:${c.s.price}|sum:${c.s.total}`);
        });
        if(bestQty && bestQty.s.qty>0){ bestQty.el.setAttribute('data-auto-tag','qty'); OUT.qty=bestQty.el; OUT.debug.push('chosen_qty='+(bestQty.el.id||bestQty.el.name||bestQty.el.className)); }
        if(bestPrice && bestPrice.s.price>0){ bestPrice.el.setAttribute('data-auto-tag','price'); OUT.price=bestPrice.el; OUT.debug.push('chosen_price='+(bestPrice.el.id||bestPrice.el.name||bestPrice.el.className)); }
        return OUT;
        """
        qty_el = price_el = None
        try:
            res = self.driver.execute_script(script)
            if DEBUG_MODE and res and res.get('debug'):
                print('   🧮 Feld-Heuristik:', res.get('debug'))
            if res and res.get('qty'):
                try:
                    qty_el = self.driver.find_element(By.CSS_SELECTOR, '[data-auto-tag="qty"]')
                except Exception:
                    qty_el = None
            if res and res.get('price'):
                try:
                    price_el = self.driver.find_element(By.CSS_SELECTOR, '[data-auto-tag="price"]')
                except Exception:
                    price_el = None
        except Exception as e:
            if DEBUG_MODE:
                print(f'   ⚠️ Feld-Heuristik Fehler: {e}')
        return {'qty': qty_el, 'price': price_el}

    # ---- Shadow DOM & Deep Input Fallback (korrekt auf Klassenebene) ---------
    def _deep_find_and_fill(self, value, description):
        script = r"""
        const val = arguments[0];
        const mode = arguments[1]; // 'qty' oder 'price'
        const excludeId = arguments[2];
        function collect(root){
          let inputs=[]; try { root.querySelectorAll('input').forEach(i=>inputs.push(i)); } catch(e){}
          if(root.shadowRoot){ try { root.shadowRoot.querySelectorAll('input').forEach(i=>inputs.push(i)); } catch(e){} }
          root.querySelectorAll('*').forEach(el=>{ if(el.shadowRoot){ try{ el.shadowRoot.querySelectorAll('input').forEach(i=>inputs.push(i)); }catch(e){} } });
          return inputs; }
        const all = collect(document);
        const qtyRx = /(orderqty|menge|amount|qty|quantity|größe|size)/i;
        const priceRx = /(limitprice|orderpx|price|limit|preis)/i;
        let chosen=null;
        for(const i of all){
           if(i.disabled) continue;
           if(excludeId && (i.id===excludeId)) continue;
           const meta=((i.placeholder||'')+" "+(i.name||'')+" "+(i.id||'')+" "+(i.className||'')).toLowerCase();
           if(mode==='qty' && qtyRx.test(meta)){ chosen=i; break; }
           if(mode==='price' && priceRx.test(meta)){ chosen=i; break; }
        }
        if(!chosen){ // fallback: numeric / empty
           for(const i of all){ if(i.disabled) continue; if(excludeId && i.id===excludeId) continue; if(!i.value){ chosen=i; break; } }
        }
        if(chosen){
           try{chosen.focus();}catch(e){};
           try{const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set; setter.call(chosen, val);}catch(e){chosen.value=val;}
           ['keydown','keyup','input','change','blur'].forEach(ev=>{try{chosen.dispatchEvent(new Event(ev,{bubbles:true}));}catch(e){}});
           return {filled:true, id:chosen.id||'', name:chosen.name||'', cls:chosen.className||'', total:all.length};
        }
        return {filled:false,total:all.length};
        """
        try:
            mode = 'qty' if 'Menge' in description or 'Amount' in description else 'price'
            exclude = None
            if mode=='price' and self._last_qty_element is not None:
                try:
                    exclude = self._last_qty_element.get_attribute('id') or ''
                except Exception:
                    exclude = None
            res = self.driver.execute_script(script, str(value), mode, exclude)
            if res and res.get('filled'):
                tag = res.get('id') or res.get('name') or res.get('cls') or '?'
                print(f"   ✅ {description} (Deep ShadowDOM) gesetzt via {tag} (inputs={res.get('total')})")
                # Speichere Referenz für spätere Ausschlüsse
                try:
                    if mode=='qty':
                        self._last_qty_element = self.driver.find_element(By.ID, res.get('id')) if res.get('id') else None
                    else:
                        self._last_price_element = self.driver.find_element(By.ID, res.get('id')) if res.get('id') else None
                except Exception:
                    pass
                return True
            else:
                if DEEP_INPUT_DEBUG:
                    print(f"   🔍 Deep ShadowDOM Scan: {res}")
        except Exception as e:
            if DEEP_INPUT_DEBUG:
                print(f"   ⚠️ ShadowDOM Fallback Fehler: {e}")
        return False

    def _try_fill_input(self, selectors, value, description):
        for sel in selectors:
            try:
                if sel.startswith('//'):
                    el = self.driver.find_element(By.XPATH, sel)
                else:
                    el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if not el.is_displayed() or not el.is_enabled():
                    continue
                try:
                    el.click(); el.clear();
                    el.send_keys(Keys.CONTROL, 'a'); el.send_keys(str(value))
                except Exception:
                    if not self.js_fill(el, value):
                        continue
                print(f'   ✅ {description} gesetzt: {value}')
                return True
            except Exception:
                continue
        # JS globale Suche fallback
        try:
            script = """
            const val = arguments[0];
            let filled=false; 
            document.querySelectorAll('input').forEach(i=>{const ph=(i.placeholder||'').toLowerCase();
              if(/menge|amount|qty|quantity|preis|price|limit/.test(ph)) {try{i.value=val; i.dispatchEvent(new Event('input',{bubbles:true})); filled=true;}catch(e){} }
            });
            return filled;"""
            if self.driver.execute_script(script, str(value)):
                print(f'   ✅ {description} per JS-Mass-Fallback gesetzt: {value}')
                return True
        except Exception:
            pass
        print(f'   ⚠️ {description} nicht automatisch gesetzt')
        # Versuche Shadow DOM Deep Scan
        if self._deep_find_and_fill(value, description):
            return True
        self.dump_debug(description.replace(' ','_'))
        return False

    # --- Neuer universeller JS-Filler für auch contenteditable / role Felder ---
    def _js_smart_fill(self, qty, price):
        script = r"""
        const qty = arguments[0];
        const price = arguments[1];
        const debug = arguments[2];
        const OUT = {qty:false, price:false, scanned:0, cand:0, same:false};
        const NUM_RX = /(\d)/;
        const els = [];
        const qTerms = /(menge|amount|qty|quant|größe|size)/i;
        const pTerms = /(limitprice|orderpx|limit|preis|price)/i;
        function pushAll(nodes){ nodes.forEach(n=>els.push(n)); }
        pushAll([...document.querySelectorAll('input')]);
        pushAll([...document.querySelectorAll('[contenteditable="true"]')]);
        pushAll([...document.querySelectorAll('[role="spinbutton"],[role="textbox"],[aria-label]')]);
        OUT.scanned = els.length;
        function setVal(el, val){
          try{
            if(el.tagName==='INPUT'){
              el.focus(); el.value = val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return true;
            }else{
              el.focus();
              // contenteditable oder div
              el.innerText = val; el.textContent = val;
              el.dispatchEvent(new Event('input',{bubbles:true}));
              el.dispatchEvent(new Event('change',{bubbles:true}));
              return true;
            }
          }catch(e){return false;}
        }
        // Erst label-basierte Zuordnung
        let qtyEl=null, priceEl=null;
        for(const el of els){
          if(el.offsetParent===null) continue;
          const meta = ((el.getAttribute('placeholder')||'')+' '+(el.getAttribute('aria-label')||'')+' '+(el.getAttribute('name')||'')+' '+(el.getAttribute('id')||'')+' '+(el.className||'')+' '+(el.innerText||'')).toLowerCase();
          if(!qtyEl && qTerms.test(meta)) qtyEl = el;
          if(!priceEl && pTerms.test(meta)) priceEl = el;
        }
        // Falls nicht gefunden: heuristik nach Position: erst numerische dann zweite numerische
        const numericCandidates = els.filter(e=>e.offsetParent && /(input|div|span)/i.test(e.tagName));
        function isLikelyNumeric(el){
           const t=(el.getAttribute('inputmode')||'').toLowerCase();
           if(t.includes('decimal')||t.includes('numeric')) return true;
           const cls=(el.className||'').toLowerCase();
           if(/amount|price|limit|qty|quant/.test(cls)) return true;
           const ph=(el.getAttribute('placeholder')||'').toLowerCase();
           if(/\d|price|limit|menge|amount|qty|quant|preis/.test(ph)) return true;
           return false;
        }
        if(!qtyEl){
          for(const el of numericCandidates){ if(isLikelyNumeric(el)){ qtyEl=el; break; } }
        }
        if(!priceEl){
          let count=0; for(const el of numericCandidates){ if(isLikelyNumeric(el)){ count++; if(count===2){ priceEl=el; break;} } }
        }
        if(qtyEl){ if(setVal(qtyEl, qty)) OUT.qty=true; }
        if(priceEl){ if(priceEl===qtyEl) OUT.same=true; else if(setVal(priceEl, price)) OUT.price=true; }
        if(!OUT.price && !OUT.same && priceEl===null){
          const alt = document.querySelector('#LimitPrice, #OrderPx');
          if(alt && alt!==qtyEl){ if(setVal(alt, price)){ OUT.price=true; } }
        }
        OUT.cand = numericCandidates.length;
        return OUT;
        """
        try:
            res = self.driver.execute_script(script, str(qty), str(price), DEEP_INPUT_DEBUG)
            if res and (res.get('qty') or res.get('price')):
                msg = f"   ✅ SmartFill Ergebnis: qty={res.get('qty')} price={res.get('price')} sameField={res.get('same')} scanned={res.get('scanned')} cand={res.get('cand')}"
                if res.get('same'):
                    msg += "  ⚠️ Gleiches Feld erkannt – Preis NICHT gesetzt"
                print(msg)
                return res.get('qty'), res.get('price')
            if DEEP_INPUT_DEBUG:
                print(f"   🔍 SmartFill keine Treffer: {res}")
        except Exception as e:
            if DEEP_INPUT_DEBUG:
                print(f"   ⚠️ SmartFill Fehler: {e}")
        return False, False

    def _simulate_keystrokes(self, element, text):
        if not SLOW_KEYSTROKES:
            try:
                element.clear()
            except Exception:
                pass
            try:
                element.send_keys(Keys.CONTROL,'a')
            except Exception:
                pass
            try:
                element.send_keys(str(text))
                return True
            except Exception:
                return False
        try:
            # langsamer, Zeichen für Zeichen
            try:
                element.clear()
            except Exception:
                pass
            for ch in str(text):
                element.send_keys(ch)
                time.sleep(0.05)
            return True
        except Exception:
            return False

    # --- Portfolio & Preis (bestehende Methoden leicht angepasst bleiben) ...existing code...

    def choose_side(self, action):
        side = action.upper()
        print(f'➡️ Seite {side} wählen ...')
        selectors = [
            f"//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'kaufen' if side=='BUY' else 'verkaufen'}')]",
            f"//button[contains(text(), '{side}')]",
            f"//span[contains(text(), '{side}')]//parent::button",
            f"//div[contains(text(), '{side}')]",
            f"//button[contains(@class,'{side.lower()}')]",
        ]
        self._try_click_selectors(selectors, f'Seite {side}', required=False)
        # Fallback: Tabs mit role
        tab_selectors = [
            f"//*[@role='tab' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'kaufen' if side=='BUY' else 'verkaufen'}')]",
            f"//*[@role='tab' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'buy' if side=='BUY' else 'sell'}')]",
        ]
        self._try_click_selectors(tab_selectors, f'Seite {side} (Tab)', required=False)

    def _is_side_active(self, side):
        side = side.upper()
        try:
            active_candidates = [
                "//*[@aria-selected='true']",
                "//*[contains(@class,'active')]",
                "//*[@data-state='active']",
                "//*[@role='tab' and @aria-selected='true']",
                "//*[@role='radio' and (@aria-checked='true' or @data-state='checked')]",
                "//*[@aria-pressed='true']",
                "//button[@data-state='on']",
            ]
            for xp in active_candidates:
                try:
                    els = self.driver.find_elements(By.XPATH, xp)
                    for el in els:
                        txt = (el.text or '').lower()
                        if side=='BUY' and any(k in txt for k in ['kauf','buy']):
                            return True
                        if side=='SELL' and any(k in txt for k in ['verkauf','sell']):
                            return True
                except Exception:
                    continue
            # Heuristik: Button mit Klasse buy/sell + ausgewählter Stil (z.B. aria-pressed fehlt)
            try:
                heuristic = self.driver.find_elements(By.XPATH, "//button[contains(@class,'buy') or contains(@class,'sell')]")
                for b in heuristic:
                    if not b.is_displayed():
                        continue
                    cls = (b.get_attribute('class') or '').lower()
                    aria = (b.get_attribute('aria-pressed') or '').lower()
                    txt = (b.text or '').lower()
                    if side=='BUY' and ('buy' in cls or 'kauf' in txt):
                        # Wenn SELL Button ebenfalls sichtbar und unterschiedlich -> wir akzeptieren
                        return True
                    if side=='SELL' and ('sell' in cls or 'verkauf' in txt):
                        return True
            except Exception:
                pass
        except Exception:
            pass
        return False

    def ensure_side(self, side):
        # Wiederholtes Anklicken bis aktiv oder max Versuche
        for attempt in range(3):
            if self._is_side_active(side):
                if DEBUG_MODE:
                    print(f"   🟢 Seite {side} aktiv (Versuch {attempt})")
                return True
            self.choose_side(side)
            extra = [
                f"//*[@role='tab' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'kaufen' if side=='BUY' else 'verkaufen'}')]",
                f"//*[@role='tab' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'buy' if side=='BUY' else 'sell'}')]",
                f"//*[@role='radio' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'kaufen' if side=='BUY' else 'verkaufen'}')]",
                f"//*[@role='radio' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{'buy' if side=='BUY' else 'sell'}')]",
            ]
            self._try_click_selectors(extra, f'Seite {side} (role Fallback)', required=False)
            time.sleep(0.2)
        if not self._is_side_active(side):
            # JS heuristische Suche & Klick als letzter Versuch
            try:
                side_js = """
                const target=arguments[0];
                const kw= target==='BUY' ? ['kauf','buy'] : ['verkauf','sell'];
                const cands=[...document.querySelectorAll('button,[role=tab],[role=radio]')];
                // Debug Sammeln
                let dbg=[];
                for(const el of cands){
                  const t=((el.innerText||'')+' '+(el.getAttribute('aria-label')||'')).toLowerCase();
                  const attrs={pressed:el.getAttribute('aria-pressed'),selected:el.getAttribute('aria-selected'),checked:el.getAttribute('aria-checked'),cls:el.className};
                  dbg.push(t+JSON.stringify(attrs).slice(0,60));
                  if(kw.some(k=>t.includes(k))){ try{el.click(); return true;}catch(e){ try{el.dispatchEvent(new Event('click',{bubbles:true})); return true;}catch(e2){}} }
                }
                return false;"""
                if self.driver.execute_script(side_js, side):
                    time.sleep(0.15)
                    if self._is_side_active(side):
                        print(f"   ✅ Seite {side} aktiviert (JS Fallback)")
                        return True
            except Exception:
                pass
            # Aggressiver letzter Versuch: alle Buttons mit Text klicken
            try:
                labels = ['kaufen','buy'] if side=='BUY' else ['verkaufen','sell']
                btns = self.driver.find_elements(By.XPATH, "//button")
                for b in btns:
                    try:
                        if not b.is_displayed(): continue
                        t=(b.text or '').lower()
                        if any(lb in t for lb in labels):
                            try:
                                b.click(); time.sleep(0.15)
                            except Exception:
                                self.driver.execute_script('arguments[0].click();', b); time.sleep(0.15)
                            if self._is_side_active(side):
                                print(f"   ✅ Seite {side} aktiviert (Button Scan)")
                                return True
                    except Exception:
                        continue
            except Exception:
                pass
            print(f"   ⚠️ Seite {side} konnte nicht bestätigt werden – bitte prüfen")
            return False
        return True

    # ================= TAB NAVIGATION =====================
    def _send_tab(self, times=1, delay=0.08):
        for _ in range(times):
            try:
                self.driver.switch_to.active_element.send_keys(Keys.TAB)
            except Exception:
                # fallback JS
                try:
                    self.driver.execute_script("document.activeElement && document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'Tab',bubbles:true}));")
                except Exception:
                    pass
            time.sleep(delay)

    def _active_meta(self):
        try:
            el = self.driver.switch_to.active_element
            if el is None:
                return None, {}
            meta = {
                'tag': el.tag_name.lower() if hasattr(el,'tag_name') else '',
                'id': el.get_attribute('id') or '',
                'name': el.get_attribute('name') or '',
                'cls': el.get_attribute('class') or '',
                'role': el.get_attribute('role') or '',
                'placeholder': el.get_attribute('placeholder') or '',
                'text': ''
            }
            try:
                meta['text'] = (el.text or '')[:60]
            except Exception:
                pass
            return el, meta
        except Exception:
            return None, {}

    def _is_active_pair_element(self):
        el, m = self._active_meta()
        if not el: return False
        txt = (m.get('text','') + ' ' + m.get('placeholder','') + ' ' + m.get('id','')).upper()
        return any(k in txt for k in ['EUR','USDT','USD']) and len(txt)<40

    def _is_active_side(self):
        el, m = self._active_meta()
        if not el: return False
        t = (m.get('text','') + ' ' + m.get('placeholder','') + ' ' + m.get('cls','')).lower()
        return any(k in t for k in ['kaufen','verkaufen','buy','sell'])

    def _is_active_strategy(self):
        el, m = self._active_meta()
        if not el: return False
        t = (m.get('text','') + ' ' + m.get('placeholder','') + ' ' + m.get('id','') + ' ' + m.get('cls','')).lower()
        return any(k in t for k in ['market','limit']) or m.get('role') in ('combobox','listbox')

    def _is_active_qty(self):
        el, m = self._active_meta();
        if not el: return False
        meta = (m.get('id','') + ' ' + m.get('name','') + ' ' + m.get('placeholder','') + ' ' + m.get('cls','')).lower()
        return any(k in meta for k in ['orderqty','menge','amount','qty','quantity'])

    def _is_active_price(self):
        el, m = self._active_meta();
        if not el: return False
        meta = (m.get('id','') + ' ' + m.get('name','') + ' ' + m.get('placeholder','') + ' ' + m.get('cls','')).lower()
        return any(k in meta for k in ['limitprice','orderpx','price','limit'])

    def _try_type(self, text):
        el, _ = self._active_meta()
        if not el: return False
        try:
            el.clear()
        except Exception:
            pass
        try:
            el.send_keys(Keys.CONTROL,'a'); el.send_keys(str(text))
            return True
        except Exception:
            try:
                self.js_fill(el, text); return True
            except Exception:
                return False

    def _click_element_with_text(self, pattern):
        xp = f"//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{pattern.lower()}')][@role='button' or self::button or contains(@class,'button')]"
        try:
            els = self.driver.find_elements(By.XPATH, xp)
            for el in els:
                if not el.is_displayed():
                    continue
                try:
                    el.click(); return True
                except Exception:
                    self.driver.execute_script('arguments[0].click();', el); return True
        except Exception:
            pass
        return False

    def navigate_via_tab_sequence(self, trade):
        """Versucht strikt via TAB Reihenfolge zu navigieren wie vom Nutzer beschrieben.
        Reihenfolge: Pair klicken -> Symbol suchen -> ENTER -> TAB zu BUY/SELL -> TAB Strategie -> 'limit' tippen -> ENTER -> TAB Menge -> Menge -> TAB Preis -> Preis.
        Gibt dict mit gesetzten Flags zurück."""
        result = { 'pair': False, 'side': False, 'strategy': False, 'qty': False, 'price': False }
        base = trade['crypto'].upper(); pair = trade['pair'].upper()
        # 1 Pair anklicken / öffnen
        try:
            # a) Versuche sichtbaren Pair-Indikator (enthält aktuelles Pair oder 'EUR')
            pair_clicked=False
            current_pair_txt_candidates = self.driver.find_elements(By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'eur') and (self::button or @role='button' or contains(@class,'pair'))][1]")
            for el in current_pair_txt_candidates:
                try:
                    if not el.is_displayed(): continue
                    el.click(); pair_clicked=True; break
                except Exception:
                    try:
                        self.driver.execute_script('arguments[0].click();', el); pair_clicked=True; break
                    except Exception: continue
            # b) Falls nicht geklickt: suche generisch nach symbol-contained element
            if not pair_clicked:
                search_patterns = [pair, base+'-EUR', base+' EUR']
                for pat in search_patterns:
                    if pair_clicked: break
                    xp = f"//*[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'{pat}')]"
                    try:
                        els = self.driver.find_elements(By.XPATH, xp)
                        for el in els:
                            if not el.is_displayed(): continue
                            t=(el.text or '').strip()
                            if len(t)>50: continue
                            try:
                                el.click(); pair_clicked=True; break
                            except Exception:
                                self.driver.execute_script('arguments[0].click();', el); pair_clicked=True; break
                    except Exception:
                        continue
            # c) Downshift Inputs direkt nutzen falls vorhanden (auch ohne vorherigen Klick)
            ds_inputs=[e for e in self.driver.find_elements(By.XPATH, "//input[starts-with(@id,'downshift-')]") if e.is_displayed()]
            # Erster downshift mit placeholder oder leer wird als pair search probiert
            for ds in ds_inputs:
                try:
                    ph=(ds.get_attribute('placeholder') or '').lower()
                    val=(ds.get_attribute('value') or '')
                    if any(k in ph for k in ['suche','search']) or not val or len(val)<=6:
                        ds.click(); ds.clear(); ds.send_keys(Keys.CONTROL,'a'); ds.send_keys(base)
                        time.sleep(0.4)
                        ds.send_keys(Keys.ENTER)
                        time.sleep(0.25)
                        if (self.get_current_pair() or '').upper()==pair:
                            result['pair']=True
                            break
                except Exception:
                    continue
            # d) Klassisches Suchfeld falls nach Klick sichtbar
            if not result['pair']:
                try:
                    search_inp=None
                    for sel in ["//input[@type='search']","//input[contains(@placeholder,'Suche') or contains(@placeholder,'Search')]"]:
                        try:
                            si=self.driver.find_element(By.XPATH, sel)
                            if si.is_displayed(): search_inp=si; break
                        except Exception: continue
                    if search_inp:
                        try:
                            search_inp.click(); search_inp.clear(); search_inp.send_keys(Keys.CONTROL,'a'); search_inp.send_keys(base)
                            time.sleep(0.35); search_inp.send_keys(Keys.ENTER); time.sleep(0.25)
                            if (self.get_current_pair() or '').upper()==pair:
                                result['pair']=True
                        except Exception: pass
                except Exception: pass
        except Exception:
            if DEBUG_MODE:
                print('   ⚠️ Pair TAB Navigation Fehler (Phase 1)')
        # 2 TABs bis Side
        for _ in range(10):
            if self._is_side_active(trade['action']):
                result['side'] = True; break
            self._send_tab(1)
        # Klick falls noch nicht aktiv
        if not result['side']:
            self.ensure_side(trade['action'])
            result['side'] = self._is_side_active(trade['action'])
        # 3 TABs bis Strategie (combobox / Market / Limit)
        for _ in range(8):
            if self._is_active_strategy():
                # Tippe 'limit'
                self._try_type('limit'); time.sleep(0.25)
                try:
                    self.driver.switch_to.active_element.send_keys(Keys.ENTER)
                except Exception: pass
                time.sleep(0.2)
                result['strategy'] = True
                break
            self._send_tab(1)
        if not result['strategy']:
            self.ensure_limit_strategy_with_search()
            result['strategy'] = True  # wir akzeptieren heuristische Aktivierung
        # 4 TAB bis Menge
        for _ in range(10):
            if self._is_active_qty():
                if self._try_type(round_asset_amount(trade['crypto'], trade['quantity'])):
                    result['qty'] = True
                self._send_tab(1)  # weiter zum Preis
                break
            self._send_tab(1)
        # 5 Preis setzen wenn aktiv
        if not result['qty']:
            # Falls Menge nicht erkannt wurde, fallback später in fill_quantity_and_price
            pass
        if self._is_active_price():
            self._try_type(trade['limit_price']); result['price'] = True
        else:
            # scanne nach LimitPrice input und fokussiere
            try:
                lp = self.driver.find_element(By.XPATH, "//input[@id='LimitPrice' or contains(@id,'LimitPrice')]")
                if lp.is_displayed():
                    try:
                        lp.click(); self._try_type(trade['limit_price']); result['price']=True
                    except Exception:
                        pass
            except Exception:
                pass
        if DEBUG_MODE:
            print(f"   🧭 TAB-Sequenz Ergebnis: {result}")
        return result

    def select_order_type(self, order_type):
        print(f'📑 Ordertyp {order_type} wählen ...')
        if order_type.lower() == 'limit':
            selectors = [
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
                "//span[contains(text(),'Limit')]",
                "//div[contains(text(),'Limit')]",
                "//button[contains(@class,'limit')]"
            ]
        else:
            selectors = [
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'market')]",
                "//span[contains(text(),'Market')]",
                "//div[contains(text(),'Market')]"
            ]
        self._try_click_selectors(selectors, f'Ordertyp {order_type}', required=False)

    # Neuer robuster Weg: Strategie-Dropdown öffnen und explizit "Limit" wählen
    def ensure_limit_strategy(self):
        # 1. Prüfen ob bereits Limit aktiv ist (mehrere mögliche Markierungen ODER LimitPrice Feld sichtbar)
        try:
            active_xpath_candidates = [
                "//*[contains(@class,'active')][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
                "//*[@aria-selected='true' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
                "//*[@data-state='active' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
                "//button[contains(@class,'selected')][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]"
            ]
            for xp in active_xpath_candidates:
                try:
                    els = self.driver.find_elements(By.XPATH, xp)
                    for el in els:
                        if el.is_displayed():
                            if DEBUG_MODE:
                                print('   🔁 Limit Strategie bereits aktiv (erkannt)')
                            return True
                except Exception:
                    continue
            # Sichtbares LimitPrice Feld als heuristische Bestätigung
            try:
                lp = self.driver.find_elements(By.XPATH, "//input[@id='LimitPrice' or contains(@id,'LimitPrice')]")
                for l in lp:
                    if l.is_displayed():
                        if DEBUG_MODE:
                            print('   🔁 Limit Strategie aktiv (LimitPrice Feld sichtbar)')
                        return True
            except Exception:
                pass
        except Exception:
            pass
        # 2. Versuche alle bekannten Trigger zu öffnen (Dropdown / Toggle / Combobox)
        trigger_selectors = [
            # Buttons oder Container die Market oder Limit anzeigen
            "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'market')]",
            "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
            "//div[contains(@class,'order-type') or contains(@class,'strategy')][.//span]",
            "//span[contains(text(),'Market') or contains(text(),'Limit')]/ancestor::button[1]",
            "//*[@role='tab' and (contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'market') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit'))]",
            "//*[@role='combobox' and (contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'market') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit'))]",
        ]
        opened = False
        for sel in trigger_selectors:
            try:
                el = self.driver.find_element(By.XPATH, sel)
                if not el.is_displayed():
                    continue
                try:
                    el.click(); opened = True
                except Exception:
                    self.driver.execute_script('arguments[0].click();', el); opened = True
                if opened:
                    if DEBUG_MODE:
                        print(f"   🔓 Strategie-Trigger geöffnet via {sel}")
                    time.sleep(0.15)
                    break
            except Exception:
                continue
        if not opened:
            # Fallback auf frühere Logik (klick direkt auf Limit falls vorhanden)
            self.select_order_type('limit')
        time.sleep(0.1)
        # 3. Optionen durchsuchen und Limit wählen
        limit_option_selectors = [
            "//li[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
            "//*[@role='option' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
            "//button[contains(@class,'limit') and (contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit'))]",
            "//span[contains(text(),'Limit')]/ancestor::*[self::li or self::button or self::div][1]",
        ]
        chosen = False
        for sel in limit_option_selectors:
            try:
                el = self.driver.find_element(By.XPATH, sel)
                if not el.is_displayed():
                    continue
                try:
                    el.click(); chosen = True
                except Exception:
                    self.driver.execute_script('arguments[0].click();', el); chosen = True
                if chosen:
                    if DEBUG_MODE:
                        print(f"   ✅ Limit Strategie gewählt via {sel}")
                    break
            except Exception:
                continue
        # 4. Falls noch nicht gewählt: versuche innerhalb eines Tab Panels (Market/Limit Tabs)
        if not chosen:
            tab_like = [
                "//div[contains(@class,'tabs')]//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
                "//div[contains(@class,'tab')]//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]",
            ]
            self._try_click_selectors(tab_like, 'Limit Tab (Fallback)', required=False)
        # 5. Abschließende Prüfung
        try:
            verify = self.driver.find_elements(By.XPATH, "//*[contains(@class,'active') or @aria-selected='true' or @data-state='active'][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]")
            for v in verify:
                if v.is_displayed():
                    return True
        except Exception:
            pass
        # Nicht kritisch fatal – wir fahren fort, aber Hinweis ausgeben
        print('   ⚠️ Limit Strategie konnte nicht eindeutig bestätigt werden (bitte prüfen)')
        return False

    def ensure_limit_strategy_with_search(self):
        """Erweiterter Fallback: Falls Limit nicht aktiv, versuche innerhalb eines ggf. geöffneten Dropdowns ein Suchfeld mit 'Limit' zu füllen."""
        if self.ensure_limit_strategy():
            return True
        # Versuche ein Kombinations-/Suchfeld zu identifizieren
        try:
            combo_inputs = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder,'Suche') or contains(@placeholder,'Search') or @role='combobox']")
            for ci in combo_inputs:
                if not ci.is_displayed():
                    continue
                try:
                    ci.click(); ci.clear(); ci.send_keys(Keys.CONTROL,'a'); ci.send_keys('Limit')
                    time.sleep(0.3)
                except Exception:
                    continue
                # Klicke jetzt Option
                if self._try_click_selectors(["//li[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit')]"], 'Limit Such-Option', required=False):
                    return True
        except Exception:
            pass
        return False

    def _find_price_field_direct(self):
        # Direkte gezielte Suche nach Preisfeld (vor heuristik) – gibt Element oder None
        direct_xpaths = [
            "//input[@id='LimitPrice' or @name='LimitPrice']",
            "//input[contains(@id,'Limit') and not(@type='hidden')]",
            "//input[contains(@name,'limit') or contains(@name,'price')]",
            "//input[contains(@class,'limit') or contains(@class,'price')]",
            "//*[@contenteditable='true' and (contains(@id,'limit') or contains(@id,'price') or contains(@class,'limit') or contains(@class,'price'))]",
        ]
        for xp in direct_xpaths:
            try:
                el = self.driver.find_element(By.XPATH, xp)
                if el.is_displayed():
                    return el
            except Exception:
                continue
        return None

    # ---- Aktuelles Handelspaar erkennen ----------------------------------
    def get_current_pair(self):
        """Versucht das aktuell ausgewählte Paar z.B. BTC-EUR aus UI zu lesen.
        Rückgabe: STRING oder None."""
        patterns = [
            r"([A-Z]{2,6})[-/ ]?(EUR|USDT|USD|EUR)"  # Basis-Pattern
        ]
        # Mehrere potentielle Container durchsuchen
        candidate_xpaths = [
            "//div[contains(@class,'pair')][.//*[contains(text(),'EUR')]]",
            "//header//*[contains(text(),'EUR')]",
            "//button[contains(@class,'pair') or contains(@class,'asset')][contains(.,'EUR')]",
            "//h1[contains(.,'EUR')]",
            "//span[contains(@class,'pair') and contains(.,'EUR')]",
            "//div[contains(@class,'asset') and contains(.,'EUR')]",
        ]
        texts = []
        for xp in candidate_xpaths:
            try:
                els = self.driver.find_elements(By.XPATH, xp)
                for e in els:
                    if not e.is_displayed():
                        continue
                    t = (e.text or '').strip().upper()
                    if t and t not in texts:
                        texts.append(t)
            except Exception:
                continue
        # Fallback: gesamter Body Ausschnitt
        if not texts:
            try:
                body_txt = (self.driver.find_element(By.TAG_NAME,'body').text or '')[:400].upper()
                texts.append(body_txt)
            except Exception:
                pass
        for txt in texts:
            for pat in patterns:
                m = re.search(pat, txt)
                if m:
                    return f"{m.group(1)}-{m.group(2)}"
        return None

    def _force_pair_switch(self, base, target_pair):
        """Aggressiver letztes Mittel Paarwechsel (Downshift, JS Textknoten, direkte Iteration)."""
        changed=False
        # Downshift Inputs
        try:
            ds_inputs=[e for e in self.driver.find_elements(By.XPATH, "//input[starts-with(@id,'downshift-')]") if e.is_displayed()]
            for inp in ds_inputs:
                try:
                    inp.click(); time.sleep(0.05)
                    inp.clear(); inp.send_keys(Keys.CONTROL,'a'); inp.send_keys(base)
                    time.sleep(0.35)
                    list_opts=self.driver.find_elements(By.XPATH, f"//li[.//span[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'{base}')]]")
                    for li in list_opts:
                        if not li.is_displayed(): continue
                        if 'EUR' in (li.text or ''):
                            try:
                                li.click(); changed=True; break
                            except Exception:
                                self.driver.execute_script('arguments[0].click();', li); changed=True; break
                    if changed: break
                except Exception:
                    continue
        except Exception:
            pass
        if changed:
            return True
        # JS Textsuche
        js = r"""
        const sym=arguments[0]; const target=arguments[1];
        function visible(el){try{const r=el.getBoundingClientRect(); return r.width>4 && r.height>4 && el.offsetParent;}catch(e){return false}}
        const rx=new RegExp('^'+sym+'[- ]?(EUR|USDT|USD)$','i');
        let best=null, bestLen=1e9;
        const walker=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
        while(walker.nextNode()){
          const t=walker.currentNode.textContent.trim(); if(!t||t.length>24) continue; if(!rx.test(t)) continue;
          const el=walker.currentNode.parentElement; if(!el||!visible(el)) continue;
          const norm=t.toUpperCase().replace(/\s+/g,''); if(norm!==target) continue;
          const l=el.outerHTML?el.outerHTML.length:9999; if(l<bestLen){ best=el; bestLen=l; }
        }
        if(best){ try{best.click(); return true;}catch(e){ try{best.dispatchEvent(new Event('click',{bubbles:true})); return true;}catch(e2){}} }
        return false;"""
        try:
            if self.driver.execute_script(js, base, target_pair.replace('-', '')):
                return True
        except Exception:
            pass
        # Direkte Iteration über Buttons/Spans
        try:
            els=self.driver.find_elements(By.XPATH, "//button|//span|//div")
            tgt=target_pair.replace('-', '')
            for e in els:
                try:
                    if not e.is_displayed(): continue
                    t=(e.text or '').strip().upper().replace(' ','')
                    if t==tgt:
                        try:
                            e.click(); return True
                        except Exception:
                            self.driver.execute_script('arguments[0].click();', e); return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def select_pair(self, trade):
        # Verbesserte Auswahl-Logik: prüft zunächst aktuelles Paar, dann versucht mehrstufigen Wechsel
        target_pair = trade['pair'].upper()
        base = trade['crypto'].upper()
        print(f'📌 Wähle Paar {target_pair} ...')
        current = None
        try:
            current = self.get_current_pair()
        except Exception:
            current = None
        if current and current == target_pair:
            if DEBUG_MODE:
                print(f"   🔁 Paar bereits aktiv: {current}")
            return
        # 1. Versuchen: Direkt klickbare Elemente mit vollständigem Paar
        direct_pair_selectors = [
            f"//span[translate(normalize-space(text()),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{target_pair}']",
            f"//div[translate(normalize-space(text()),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{target_pair}']",
            f"//button[.//span[translate(normalize-space(text()),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{target_pair}']]",
        ]
        if self._try_click_selectors(direct_pair_selectors, 'Direktes Paar', required=False):
            time.sleep(0.2)
            if self.get_current_pair() == target_pair:
                print('   ✅ Paar gewechselt (direkt)')
                return
        # 2. Öffne ggf. Pair/Asset Auswahl (Klick auf aktuell sichtbares Paar oder Asset-Header)
        open_panel_triggers = [
            "//button[contains(@class,'pair') or contains(@class,'asset')]",
            "//div[contains(@class,'pair')][@role='button']",
            "//div[contains(@class,'asset-selector')]",
            "//header//*[contains(@class,'pair') or contains(@class,'asset')]",
        ]
        self._try_click_selectors(open_panel_triggers, 'Paar-Auswahl öffnen', required=False)
        time.sleep(0.15)
        # 3. Suchfeld finden / öffnen (ggf. Such-Icon betätigen)
        search_icon_triggers = [
            "//button[contains(@aria-label,'Suche') or contains(@aria-label,'Search')]",
            "//button//*[local-name()='svg' and (contains(@class,'search') or contains(@aria-label,'search'))]",
            "//div[contains(@class,'search')]//button",
        ]
        # Falls kein Suchfeld sichtbar -> versuche Icon
        def _search_input_visible():
            try:
                si = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder,'Suche') or contains(@placeholder,'Search')]")
                return any(e.is_displayed() for e in si)
            except Exception:
                return False
        if not _search_input_visible():
            self._try_click_selectors(search_icon_triggers, 'Suchfeld Trigger', required=False)
            time.sleep(0.15)
        # 4. Suchfeld ausfüllen
        search_inputs = [
            "//input[contains(@placeholder,'Suche') or contains(@placeholder,'Search')]",
            "//input[contains(@class,'search')]",
            "//input[@type='search']",
        ]
        search_used = False
        for sel in search_inputs:
            try:
                el = self.driver.find_element(By.XPATH, sel)
                if el.is_displayed():
                    try:
                        el.click(); el.clear(); el.send_keys(Keys.CONTROL,'a'); el.send_keys(base)
                        search_used = True
                        time.sleep(0.35)
                        break
                    except Exception:
                        pass
            except Exception:
                continue
        # 5. Ergebniszeilen klicken
        if search_used:
            result_row_selectors = [
                f"//tr[.//span[translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{base}']]",
                f"//li[.//span[translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{base}']]",
                f"//div[contains(@class,'list')]//span[translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{base}']",
                f"//span[translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{base}']",
            ]
            self._try_click_selectors(result_row_selectors, f'Suchergebnis {base}', required=False)
            time.sleep(0.25)
        # 6. Fallback: erneut direkt nach BASE Symbol suchen (ohne Suchfeld)
        if self.get_current_pair() != target_pair:
            base_direct = [
                f"//span[text()='{base}']",
                f"//button//span[text()='{base}']",
                f"//div[text()='{base}']",
            ]
            self._try_click_selectors(base_direct, f'Basis {base} (Fallback)', required=False)
            time.sleep(0.2)
        # 7. Abschlussprüfung
        final_pair = self.get_current_pair()
        if final_pair != target_pair:
            if self._force_pair_switch(base, target_pair):
                time.sleep(0.3)
                final_pair = self.get_current_pair()
        if final_pair == target_pair:
            print('   ✅ Paar gewechselt')
        else:
            print(f"   ⚠️ Paar NICHT gewechselt (aktuell={final_pair}) – bitte manuell prüfen")

    def review_and_submit_order(self):
        if PAPER_MODE:
            # Statt Review -> Reset / Abbrechen Button
            selectors_reset = [
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'reset')]",
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'zurücksetzen')]",
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'clear')]",
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'abbrechen')]",
            ]
            clicked = self._try_click_selectors(selectors_reset, 'Reset Button (Paper)', required=False)
            if clicked:
                print('   🔄 Paper Mode: Order zurückgesetzt (nur Anzeige).')
            return
        # Real Mode: normaler Review + optional Submit
        # SELL Doppelschutz: Nur wenn keine manuellen Klick-Wartezeiten aktiv sind
        if FORCE_SELL_TYPING and not WAIT_FOR_CLICK and not SAFE_PREVIEW_MODE:
            try:
                # Prüfen ob SELL Seite aktiv ist
                if self._is_side_active('SELL'):
                    confirm = input("❗ Sicherheitsabfrage SELL: tippe exakt 'SELL' um Review zu ermöglichen (ENTER = Abbruch): ").strip().upper()
                    if confirm != 'SELL':
                        print('🛑 SELL Review abgebrochen (Tipptest fehlgeschlagen)')
                        return
            except KeyboardInterrupt:
                raise
            except Exception:
                print('⚠️ Eingabeproblem – SELL Sicherheit greift, Abbruch dieser Order')
                return
        selectors_review = [
            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'review')]",
            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'prüfen')]",
        ]
        self._try_click_selectors(selectors_review, 'Review Button', required=False)
        if self.auto_submit:
            selectors_send = [
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'confirm')]",
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'bestätigen')]",
                "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'senden')]",
            ]
            self._try_click_selectors(selectors_send, 'Finaler Senden Button', required=False)

    # --- Portfolio & Preis Helfer (wieder eingefügt) --------------------
    def fetch_current_price_dom(self, crypto):
        selectors = [
            "//span[contains(@class,'price')][contains(.,'.')][1]",
            "//div[contains(@class,'price')][contains(.,'.')][1]",
            "//span[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'eur')][contains(.,'.')]",
        ]
        for sel in selectors:
            try:
                el = self.driver.find_element(By.XPATH, sel)
                raw = el.text.strip()
                txt = raw.replace('\u202f',' ').replace('€','').replace('EUR','').replace(',','').strip()
                m = re.search(r"(\d+\.?\d+)", txt)
                if m:
                    return float(m.group(1))
            except Exception:
                continue
        return None

    def fetch_portfolio_holdings(self):
        if self.cached_holdings:
            return self.cached_holdings
        holdings = {}
        row_selectors = ["//table//tr", "//div[contains(@class,'portfolio')]//tr"]
        for sel in row_selectors:
            try:
                rows = self.driver.find_elements(By.XPATH, sel)
                for r in rows:
                    txt = r.text.strip()
                    if not txt:
                        continue
                    parts = re.split(r"[\n\s]+", txt)
                    for i,p in enumerate(parts):
                        if re.fullmatch(r"[A-Z]{2,6}", p):
                            for j in range(i+1, min(i+6, len(parts))):
                                num = parts[j].replace(',','.')
                                if re.match(r"^\d+(\.\d+)?$", num):
                                    try:
                                        q = float(num)
                                        holdings[p] = q
                                        break
                                    except Exception:
                                        pass
                            break
            except Exception:
                continue
        if holdings:
            self.cached_holdings = holdings
        return holdings

    def adjust_trade_for_portfolio(self, trade):
        if trade['action'] != 'SELL':
            return trade
        if not PORTFOLIO_CHECK:
            return trade
        holdings = self.fetch_portfolio_holdings()
        avail = holdings.get(trade['crypto'].upper())
        if avail is None:
            print(f"   ℹ️ Bestand für {trade['crypto']} nicht gefunden")
            return trade
        if avail <= 0:
            print(f"   🚫 Kein Bestand für {trade['crypto']} – Trade übersprungen")
            trade['skip'] = True
            return trade
        if trade['quantity'] > avail:
            print(f"   ✂️ SELL Menge reduziert {trade['quantity']} -> {avail}")
            trade['quantity'] = avail
        return trade

    def override_limit_with_realtime(self, trade):
        if not USE_REALTIME_LIMIT:
            return trade
        dom_price = self.fetch_current_price_dom(trade['crypto'])
        chosen = None
        if dom_price and dom_price > 0:
            chosen = dom_price
        elif trade.get('realtime_price') and math.isfinite(trade['realtime_price'] or float('nan')):
            chosen = trade['realtime_price']
        if chosen:
            old = trade['limit_price']
            trade['limit_price'] = chosen
            if abs(old - chosen) > 1e-9:
                print(f"   🔄 Limit Preis ersetzt: {old} -> {chosen}")
        return trade

    def fill_quantity_and_price(self, trade):
        trade['quantity'] = round_asset_amount(trade['crypto'], trade['quantity'])
        qty = trade['quantity']; limit_price = trade['limit_price']
        print(f'⚖️ Menge {qty} & Limit {limit_price} ...')
        skip_qty = trade.get('qty_via_button')
        skip_price = trade.get('price_via_bps')
        # Warten auf Inputs
        def inputs_ready():
            try:
                count = len(self.driver.find_elements(By.XPATH, "//input"))
                if DEEP_INPUT_DEBUG and count:
                    try:
                        els = self.driver.find_elements(By.XPATH, "//input")[:10]
                        meta = []
                        for e in els:
                            meta.append((e.get_attribute('placeholder') or '') + '|' + (e.get_attribute('name') or '') + '|' + (e.get_attribute('class') or '') )
                        print(f"   🔍 Inputs gefunden ({count}): {meta}")
                    except Exception:
                        pass
                return count >= MIN_INPUT_COUNT
            except Exception:
                return False
        self._wait(inputs_ready, timeout=8, desc='Inputs erscheinen nicht')
        try:
            if len(self.driver.find_elements(By.XPATH, "//input")) < MIN_INPUT_COUNT:
                self.switch_into_relevant_iframe()
        except Exception:
            pass
        qty_selectors = [
            "//input[contains(@placeholder,'Menge') or contains(@placeholder,'Amount') or contains(@placeholder,'Quant')]",
            "//input[contains(@name,'amount') or contains(@name,'quant')]",
            "//input[contains(@id,'amount') or contains(@id,'quant')]",
            "//input[contains(@class,'amount') or contains(@class,'quant')]",
            ".amount-input input", ".quantity-input input"
        ]
        price_selectors = [
            "//input[contains(@placeholder,'Limit') or contains(@placeholder,'Preis') or contains(@placeholder,'Price')]",
            "//input[contains(@name,'price') or contains(@name,'limit')]",
            "//input[contains(@id,'price') or contains(@id,'limit')]",
            "//input[contains(@class,'price') or contains(@class,'limit')]",
            ".price-input input", ".limit-price-input input"
        ]
        got_qty = bool(skip_qty)
        got_price = bool(skip_price)
        # Spinbuttons
        def _collect_spinbuttons():
            try:
                return [c for c in self.driver.find_elements(By.XPATH, "//*[@role='spinbutton']") if c.is_displayed()]
            except Exception:
                return []
        def _classify_spin(cands):
            q=p=None
            for c in cands:
                meta=((c.get_attribute('aria-label') or '')+' '+(c.get_attribute('class') or '')+' '+(c.text or '')).lower()
                if q is None and re.search(r'menge|amount|qty|quantity|größe|size', meta): q=c
                elif p is None and re.search(r'limit|preis|price|orderpx', meta): p=c
            if (not q or not p) and len(cands)==2:
                if not q: q=cands[0]
                if not p: p=cands[1]
            return q,p
        def _set_spin(el, value):
            if not el or skip_qty and skip_price: return False
            try: el.click()
            except Exception: pass
            try:
                self.driver.execute_script("if(arguments[0].setAttribute){arguments[0].setAttribute('aria-valuenow', arguments[1]);} if(arguments[0].value!==undefined){arguments[0].value=arguments[1];} arguments[0].dispatchEvent(new Event('input',{bubbles:true})); arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", el, str(value))
            except Exception: pass
            try: el.send_keys(Keys.CONTROL,'a'); el.send_keys(str(value))
            except Exception: pass
            try:
                raw=el.get_attribute('value') or el.get_attribute('aria-valuenow') or ''
                if raw and re.search(r"(\d+\.?\d*)", raw):
                    return True
            except Exception: pass
            return False
        spins=_collect_spinbuttons()
        if spins and DEEP_INPUT_DEBUG:
            print(f"   🔍 Spinbuttons gefunden: {len(spins)}")
        if spins:
            sbq,sbp=_classify_spin(spins)
            if sbq and not got_qty and _set_spin(sbq, qty):
                print('   ✅ Menge (Spinbutton) gesetzt'); got_qty=True
            if sbp and not got_price and _set_spin(sbp, limit_price):
                print('   ✅ Limit (Spinbutton) gesetzt'); got_price=True
        price_direct = None if skip_price else self._find_price_field_direct()
        fields = {'qty':None,'price':None} if (skip_qty and skip_price) else self._identify_order_fields()
        if (not skip_qty) and fields.get('qty') and not got_qty:
            try:
                fields['qty'].click(); fields['qty'].clear()
            except Exception: pass
            if self._set_element_value(fields['qty'], qty):
                print('   ✅ Menge erkannt & gesetzt (Heuristik)'); got_qty=True
        price_candidate = None if skip_price else (price_direct or fields.get('price'))
        if price_candidate and not got_price:
            try:
                price_candidate.click(); price_candidate.clear()
            except Exception: pass
            if self._set_element_value(price_candidate, limit_price):
                print('   ✅ Limit erkannt & gesetzt (Direkt/Heuristik)'); got_price=True
        if (not skip_price) and got_qty and not got_price and not fields.get('price'):
            try:
                fields['qty'].send_keys(Keys.TAB); time.sleep(0.15)
                active=self.driver.switch_to.active_element
                meta=(active.get_attribute('placeholder') or '') + ' ' + (active.get_attribute('id') or '') + ' ' + (active.get_attribute('name') or '') + ' ' + (active.get_attribute('class') or '')
                if re.search(r'price|limit|preis|px', meta.lower()):
                    if self._set_element_value(active, limit_price):
                        print('   ✅ Limit via TAB-Navigation gesetzt'); got_price=True
            except Exception: pass
        if (not skip_price) and STRICT_FIELD_MATCH and not got_price and not fields.get('price'):
            if DEBUG_MODE: print('   🔒 STRICT_FIELD_MATCH aktiv – warte auf separates Preisfeld')
            for _ in range(6):
                time.sleep(0.4)
                newf=self._identify_order_fields()
                if newf.get('price') and newf.get('price')!=newf.get('qty'):
                    try:
                        newf['price'].click(); newf['price'].clear()
                    except Exception: pass
                    if self._simulate_keystrokes(newf['price'], limit_price) or self.js_fill(newf['price'], limit_price):
                        print('   ✅ Limit nach Wartezeit gesetzt'); got_price=True; break
        def _commit_price(expected_val):
            try:
                cands=[]
                try: cands.extend(self.driver.find_elements(By.CSS_SELECTOR,'[data-auto-tag="price"]'))
                except Exception: pass
                for xp in ["//input[contains(@placeholder,'Limit') or contains(@placeholder,'Preis') or contains(@placeholder,'Price')]","//input[contains(@name,'price') or contains(@name,'limit')]","//input[contains(@id,'price') or contains(@id,'limit')]"]:
                    try:
                        for el in self.driver.find_elements(By.XPATH,xp):
                            if el not in cands: cands.append(el)
                    except Exception: continue
                if not cands: return False
                try: expected_f=float(str(expected_val).replace(',','.'))
                except Exception: expected_f=None
                for cand in cands:
                    try:
                        if not cand.is_displayed(): continue
                        raw=cand.get_attribute('value') or cand.text or ''
                        txt=raw.replace('\u202f',' ').replace('€','').replace('EUR','').replace(' ','').replace(',', '.')
                        if expected_f is not None:
                            m=re.search(r"(\d+\.?\d*)", txt)
                            if m and abs(float(m.group(1))-expected_f)<=max(1e-7, expected_f*0.0005): return True
                        # retry
                        try: cand.click(); cand.clear()
                        except Exception: pass
                        if not self._simulate_keystrokes(cand, expected_val): self.js_fill(cand, expected_val)
                        try: cand.send_keys(Keys.ENTER)
                        except Exception: pass
                        time.sleep(0.15)
                        try:
                            raw2=cand.get_attribute('value') or ''
                            if expected_f is not None:
                                m2=re.search(r"(\d+\.?\d*)", raw2.replace(',', '.'))
                                if m2 and abs(float(m2.group(1))-expected_f)<=max(1e-7, expected_f*0.0005):
                                    print('   ✅ Limit Preis bestätigt (Commit)'); return True
                        except Exception: pass
                    except Exception: continue
                return False
            except Exception: return False
        if got_price and PRICE_COMMIT_VERIFY and not skip_price:
            if not _commit_price(limit_price):
                print('   ⚠️ Limit Preis konnte nicht verifiziert werden – bitte prüfen')
        elif got_price and DEBUG_MODE and not skip_price:
            try:
                lp_field=self.driver.find_element(By.ID,'LimitPrice')
                print(f"   🧾 LimitPrice Feld Rohwert: {lp_field.get_attribute('value')}")
            except Exception: pass
        if (not skip_qty) and not got_qty:
            got_qty=self._try_fill_input(qty_selectors, qty, 'Menge/Amount')
        if (not skip_price) and not got_price:
            got_price=self._try_fill_input(price_selectors, limit_price, 'Limit Preis/Price')
        if (not skip_qty) and not got_qty:
            print('   ❌ Menge NICHT gesetzt – bitte manuell eingeben!')
        if (not skip_price) and not got_price:
            print('   ❌ Limit NICHT gesetzt – bitte manuell eingeben!')
        if ((not skip_qty) and not got_qty) or ((not skip_price) and not got_price):
            try:
                script="""
                const q=arguments[0]; const p=arguments[1]; const out={qty:false,price:false,total:0};
                const candidates=[...document.querySelectorAll('input')].filter(i=>!i.disabled && i.type!=='hidden' && i.offsetParent);
                out.total=candidates.length;
                function setVal(el,val){ try{el.focus(); el.value=val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return true;}catch(e){return false;} }
                if(candidates.length){ if(setVal(candidates[0], q)) out.qty=true; }
                if(candidates.length>1){ if(setVal(candidates[1], p)) out.price=true; }
                return out;"""
                res=self.driver.execute_script(script, str(qty), str(limit_price))
                if res:
                    if (not skip_qty) and not got_qty and res.get('qty'):
                        print(f"   ✅ Menge per Positions-Fallback gesetzt (1. Input von {res.get('total')})"); got_qty=True
                    if (not skip_price) and not got_price and res.get('price'):
                        print(f"   ✅ Limit per Positions-Fallback gesetzt (2. Input von {res.get('total')})"); got_price=True
            except Exception as e:
                if DEBUG_MODE: print(f"   ⚠️ Positions-Fallback Fehler: {e}")
        if ((not skip_qty) and not got_qty) or ((not skip_price) and not got_price):
            s_qty2, s_price2 = self._js_smart_fill(qty, limit_price)
            if (not skip_qty) and s_qty2 and not got_qty: got_qty=True
            if (not skip_price) and s_price2 and not got_price: got_price=True
        if (not skip_qty) and not got_qty:
            self._deep_find_and_fill(qty, 'Menge/Amount')
        if (not skip_price) and not got_price:
            before=self._last_qty_element
            self._deep_find_and_fill(limit_price, 'Limit Preis/Price')
            try:
                if before is not None and before == self._last_price_element:
                    print("   ⚠️ Preisfeld identisch mit Mengenfeld – UI unterscheidet evtl. Modi. Bitte manuell prüfen.")
                    self.dump_debug('duplicate_qty_price_field')
            except Exception: pass
        if ((not skip_qty) and not got_qty) or ((not skip_price) and not got_price):
            self.dump_debug('unfilled_inputs')

    def apply_max_and_bps_buttons(self, trade):
        """Versucht Menge über 'Max' zu setzen und Preis via -25bps / +25bps.
        BUY => -25bps, SELL => +25bps. Setzt Flags im Trade dict."""
        changed=False
        # 1. Max Button
        if USE_MAX_BUTTON:
            try:
                max_selectors = [
                    "//button[normalize-space()='Max']",
                    "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'max')]",
                ]
                if self._try_click_selectors(max_selectors, 'Max Button', required=False):
                    trade['qty_via_button']=True
                    changed=True
            except Exception:
                pass
        # 2. BPS Buttons
        if USE_BPS_BUTTONS:
            target = '-25bps' if trade['action']=='BUY' else '+25bps'
            # Reihenfolge: direkter Treffer, fallback case-insensitive enthält
            bps_selectors = [
                f"//button[normalize-space()='{target}']",
                f"//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{target.lower()}')]",
            ]
            if self._try_click_selectors(bps_selectors, f'BPS Button {target}', required=False):
                trade['price_via_bps']=True
                changed=True
        if changed and DEBUG_MODE:
            print(f"   🧷 Button-Anwendung: qty={trade.get('qty_via_button')} price={trade.get('price_via_bps')}")
        return changed

    def process_trade(self, trade):
        try:
            # --- SELL Schutz Prüfen ---
            if trade.get('action') == 'SELL':
                # 1. Deaktiviert?
                if DISABLE_SELLS:
                    print(f"🛑 SELL {trade['pair']} übersprungen (DISABLE_SELLS aktiv)")
                    return
                # 2. Whitelist aktiv?
                if SELL_WHITELIST and trade['pair'].upper() not in SELL_WHITELIST:
                    print(f"🛑 SELL {trade['pair']} nicht in SELL_WHITELIST -> übersprungen")
                    return
                # 3. Fraction Prüfung falls Portfolio-Daten vorliegen
                try:
                    if MAX_SELL_FRACTION < 0.999 and trade.get('portfolio_qty'):
                        allowed = trade['portfolio_qty'] * MAX_SELL_FRACTION
                        if trade['quantity'] > allowed + 1e-12:
                            print(f"🛑 SELL {trade['pair']} Menge {trade['quantity']} > erlaubte {allowed:.8f} (MAX_SELL_FRACTION)")
                            return
                except Exception:
                    pass
                # 4. Preis Schutz (falls Marktpreis ermittelbar)
                if STRICT_SELL_PRICE_PROTECT > 0 and trade.get('market_price') and trade.get('limit_price'):
                    try:
                        mp = float(trade['market_price']); lp = float(trade['limit_price'])
                        if lp < mp * (1-STRICT_SELL_PRICE_PROTECT):
                            print(f"🛑 SELL {trade['pair']} Limit {lp} zu tief (Markt {mp}) > Schutz greift")
                            return
                    except Exception:
                        pass
                # 5. Manuelle Bestätigung
                if SELL_CONFIRM:
                    try:
                        ans = input(f"❓ Bestätige SELL {trade['pair']} Menge ~{trade.get('quantity')} (y / skip): ").strip().lower()
                        if ans not in ('y','yes','j'):  # skip
                            print(f"🛑 SELL {trade['pair']} abgebrochen durch Nutzer")
                            return
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        print('⚠️ Eingabeproblem – SELL wird sicherheitshalber abgebrochen')
                        return
            self.ensure_trade_page(trade)
            trade = self.override_limit_with_realtime(trade)
            trade = self.adjust_trade_for_portfolio(trade)
            if trade.get('skip'): return
            if TAB_NAV:
                self.navigate_via_tab_sequence(trade)
            else:
                self.select_pair(trade); time.sleep(0.4)
                self.ensure_side(trade['action']); time.sleep(0.3)
                if not self.ensure_limit_strategy_with_search():
                    self.ensure_limit_strategy()
            # Versuche jetzt Max und BPS Buttons VOR direkter Eingabe
            try:
                self.apply_max_and_bps_buttons(trade)
            except Exception:
                if DEBUG_MODE:
                    print('   ⚠️ apply_max_and_bps_buttons Fehler')
            self.fill_quantity_and_price(trade); time.sleep(0.25)
            # Laufzeit-Validierung: aktuelles UI Paar MUSS gewünschtes EUR Paar sein
            try:
                ui_pair = (self.get_current_pair() or '').upper()
                intended = trade['pair'].upper()
                if STRICT_EUR_ONLY and (not ui_pair.endswith('-EUR') or ui_pair != intended):
                    print(f"🛑 ABBRUCH: UI Paar '{ui_pair}' != beabsichtigt '{intended}' oder nicht -EUR. Trade übersprungen.")
                    return
            except Exception:
                pass
            # SAFE PREVIEW: Order NICHT weiter klicken, Benutzer fragt Entscheidung ab
            if SAFE_PREVIEW_MODE:
                print('\n🔐 SAFE PREVIEW AKTIV – Order nur vorausgefüllt.')
                print('   ENTER = nächste Order | c = diesen verwerfen | s = Rest überspringen | q = alles abbrechen')
                try:
                    choice = input('   Eingabe: ').strip().lower()
                except KeyboardInterrupt:
                    choice = 'q'
                if choice == 'q':
                    self.abort_all = True
                    print('🛑 Abbruch aller weiteren Trades.'); return
                if choice == 's':
                    self.skip_rest = True
                    print('⏹️ Restliche Trades werden nicht mehr gezeigt.'); return
                if choice == 'c':
                    print('♻️ Verworfen – UI bitte selbst zurücksetzen falls nötig.'); return
                # ENTER -> einfach weiter ohne Review/Reset
                return
            # Optional NICHT automatisch Review klicken – Nutzer soll manuell klicken
            if not WAIT_FOR_CLICK:
                self.review_and_submit_order(); time.sleep(0.2)
            else:
                if PAPER_MODE:
                    print('📝 PAPER MODE: Order nur ansehen. ENTER -> Reset (Zurücksetzen), dann nächster Trade.')
                else:
                    print('🖱️ REAL MODE: Prüfen & gewünschte Seite (Kaufen/Verkaufen) sichtbar lassen. ENTER -> Review (falls verfügbar).')
                try:
                    input()
                except KeyboardInterrupt:
                    raise
                # Nach Bestätigung: im Paper Mode zurücksetzen, im Real Mode Review klicken
                if PAPER_MODE:
                    self.review_and_submit_order()  # nutzt Reset-Pfad in PAPER_MODE
                else:
                    self.review_and_submit_order()
        except Exception as e:
            print(f'❌ Trade {trade.get("id")} Fehler: {e}')
            self.dump_debug(f'trade_{trade.get("id")}_error')

    def run_trader(self, trades):
        print(f"🚀 Starte Auto-Trader für {len(trades)} Trades (auto_submit={'ON' if self.auto_submit else 'OFF'})")
        for idx, trade in enumerate(trades):
            if self.abort_all:
                print('\n🛑 Verarbeitung zuvor abgebrochen (abort_all).'); break
            if self.skip_rest:
                print('\n⏹️ Weitere Trades übersprungen (skip_rest aktiv).'); break
            print(f"\n🔄 Verarbeite Trade {idx+1}/{len(trades)}: {trade['action']} {trade['quantity']:.6f} {trade['pair']} @ {trade['limit_price']}")
            self.process_trade(trade)
            if self.abort_all or self.skip_rest:
                break
            if self.auto_continue and idx < len(trades) - 1:
                print("⏩ Weiter in" , f"{self.wait_between:.1f}s ...")
                time.sleep(self.wait_between)
            elif not self.auto_continue and idx < len(trades) - 1:
                input("⏸️ ENTER für nächsten Trade...")
        print("\n🎯 Alle Trades vorbereitet. Jetzt manuell prüfen & senden.")

# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------
def main():
    print('🔧 Starte Fusion Existing Browser Multi-Trade Auto-Fill (verbesserte Version)')
    print(f'⚙️ auto_continue={AUTO_CONTINUE} wait={WAIT_BETWEEN}s realtime_limit={USE_REALTIME_LIMIT} portfolio={PORTFOLIO_CHECK} debug={DEBUG_MODE} wait_for_click={WAIT_FOR_CLICK} safe_preview={SAFE_PREVIEW_MODE} force_sell_typing={FORCE_SELL_TYPING} paper={PAPER_MODE}')
    if not ensure_selenium():
        print('❌ Selenium fehlt. Abbruch.'); return
    loader = TradeLoader()
    if not loader.load(): return
    # Wenn auf Klick gewartet werden soll -> auto_continue deaktivieren
    effective_auto_continue = AUTO_CONTINUE and (not WAIT_FOR_CLICK)
    automation = FusionExistingAutomation(auto_continue=effective_auto_continue, wait_between=WAIT_BETWEEN, auto_submit=AUTO_SUBMIT)
    if not automation.attach_or_start_debug_chrome(): return
    automation.find_fusion_tab()
    automation.run_trader(loader.trades)
    print('✅ Fertig – prüfen & manuell senden.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n⏹️ Abgebrochen')

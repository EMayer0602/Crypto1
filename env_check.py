#!/usr/bin/env python3
"""
Environment diagnostic script for Crypto_trading1 project.
Run:  python env_check.py

Checks:
 1. Python version
 2. Virtual environment detection
 3. Required package availability + versions (from requirements.txt if exists)
 4. Optional packages (pandas_market_calendars, mplfinance, ib_insync)
 5. Conflicting duplicate module names on sys.path
 6. Basic import smoke test of key project modules
 7. File system sanity (count CSVs, large file warning)
 8. .env presence & key variables
 9. Timezone / locale info

Exit code 0 if all mandatory checks pass, 1 otherwise.
"""
from __future__ import annotations
import sys, os, importlib, subprocess, json, platform, pathlib, re, textwrap, time
from typing import List, Tuple

MANDATORY_MODULES = [
    ("pandas", "pd"),
    ("numpy", "np"),
    ("scipy", None),
    ("yfinance", None),
    ("plotly", None),
]
OPTIONAL_MODULES = [
    ("pandas_market_calendars", "mcal"),
    ("mplfinance", "mpf"),
    ("ib_insync", None),
]
KEY_PROJECT_IMPORTS = [
    "crypto_backtesting_module",
    "plotly_utils",
    "signal_utils",
    "config",
]
REQ_FILE = pathlib.Path("requirements.txt")
ENV_FILE = pathlib.Path('.env')
CSV_GLOB = "*.csv"

class Color:
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    YELLOW = "\x1b[33m"
    CYAN = "\x1b[36m"
    BOLD = "\x1b[1m"
    RESET = "\x1b[0m"

def c(txt, color):
    if not sys.stdout.isatty():
        return txt
    return f"{color}{txt}{Color.RESET}"

def header(title: str):
    print("\n" + c("== " + title + " ==", Color.CYAN))

def check_python():
    header("Python Version")
    print(sys.version.replace('\n', ' '))
    major_ok = sys.version_info >= (3, 10)
    print("Minimum 3.10:", c("OK", Color.GREEN) if major_ok else c("Upgrade recommended", Color.YELLOW))
    return major_ok

def detect_virtual_env():
    header("Virtual Environment")
    in_venv = (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    env_name = os.environ.get('VIRTUAL_ENV') or ('venv' if in_venv else 'system')
    print("Active base:", sys.prefix)
    print("Detected:", c("VENV" if in_venv else "SYSTEM", Color.GREEN if in_venv else Color.YELLOW), env_name)
    return in_venv

def parse_requirements():
    header("Requirements File")
    reqs = {}
    if REQ_FILE.exists():
        for line in REQ_FILE.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#'): continue
            m = re.match(r"([A-Za-z0-9_.\-]+)([<>=!~]*.*)?", line)
            if m:
                pkg = m.group(1)
                spec = m.group(2) or ''
                reqs[pkg.lower()] = spec
        print(f"Found {len(reqs)} entries in requirements.txt")
    else:
        print(c("requirements.txt missing", Color.YELLOW))
    return reqs

def get_pkg_version(mod_name: str):
    try:
        mod = importlib.import_module(mod_name)
        ver = getattr(mod, '__version__', 'unknown')
        return True, ver
    except Exception as e:
        return False, str(e)

def check_modules(reqs):
    header("Module Availability (Mandatory)")
    ok = True
    for mod, alias in MANDATORY_MODULES:
        present, info = get_pkg_version(mod)
        if present:
            print(f"{mod:<28} version {info}")
        else:
            print(c(f"{mod:<28} MISSING ({info})", Color.RED))
            ok = False
    header("Module Availability (Optional)")
    for mod, alias in OPTIONAL_MODULES:
        present, info = get_pkg_version(mod)
        if present:
            print(f"{mod:<28} version {info}")
        else:
            print(c(f"{mod:<28} not installed", Color.YELLOW))
    return ok

def check_duplicate_modules():
    header("Duplicate Module Names on sys.path")
    from collections import defaultdict
    locations = defaultdict(list)
    for p in sys.path:
        try:
            if not p or not os.path.isdir(p):
                continue
            for item in os.listdir(p):
                if not item or item.startswith('_'):
                    continue
                name = item.split('.')[0].lower()
                locations[name].append(p)
        except Exception:
            pass
    dups = {k:v for k,v in locations.items() if len(v)>1 and k in [m[0] for m in MANDATORY_MODULES+OPTIONAL_MODULES]}
    if not dups:
        print("No concerning duplicates for tracked modules")
    else:
        for name, paths in dups.items():
            print(c(f"Duplicate: {name} -> {paths}", Color.YELLOW))


def smoke_imports():
    header("Project Module Smoke Imports")
    all_ok = True
    for name in KEY_PROJECT_IMPORTS:
        try:
            importlib.import_module(name)
            print(f"{name:<32} OK")
        except Exception as e:
            all_ok = False
            print(c(f"{name:<32} FAIL: {e}", Color.RED))
    return all_ok

def csv_sanity():
    header("CSV Files Summary")
    csvs = list(pathlib.Path('.').glob(CSV_GLOB))
    print(f"CSV count: {len(csvs)}")
    large = [p for p in csvs if p.stat().st_size > 20_000_000]
    if large:
        print(c(f"Warning: {len(large)} large CSVs >20MB", Color.YELLOW))
    if len(csvs) == 0:
        print(c("No CSV files found (unexpected for backtests)", Color.YELLOW))


def env_file_check():
    header(".env File")
    if not ENV_FILE.exists():
        print(c(".env missing", Color.YELLOW))
        return False
    try:
        content = ENV_FILE.read_text(errors='ignore')
        keys = {}
        for line in content.splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k,v=line.split('=',1)
                keys[k.strip()] = v.strip()
        needed = ["BITPANDA_API_KEY"]
        ok = True
        for k in needed:
            if k not in keys or not keys[k] or 'YOUR_NEW_API_KEY_HERE' in keys[k]:
                print(c(f"{k} not set or placeholder", Color.YELLOW))
                ok = False
            else:
                print(f"{k} set (masked)")
        return ok
    except Exception as e:
        print(c(f"Read error: {e}", Color.RED))
        return False

def tz_locale():
    header("Timezone / Locale")
    print("Platform:", platform.platform())
    print("Timezone offset (secs):", -time.timezone)
    print("TZ env:", os.environ.get('TZ','<unset>'))


def main():
    print(c("CRYPTO ENVIRONMENT DIAGNOSTIC", Color.BOLD))
    results = []
    results.append(check_python())
    detect_virtual_env()
    reqs = parse_requirements()
    results.append(check_modules(reqs))
    check_duplicate_modules()
    results.append(smoke_imports())
    csv_sanity()
    results.append(env_file_check())
    tz_locale()

    mandatory_pass = all(results)
    header("Summary")
    print("Mandatory checks pass:" , c(str(mandatory_pass), Color.GREEN if mandatory_pass else Color.RED))
    if not mandatory_pass:
        print(c("One or more mandatory checks failed. See above.", Color.RED))
        sys.exit(1)
    else:
        print(c("All mandatory checks passed.", Color.GREEN))

if __name__ == '__main__':
    main()

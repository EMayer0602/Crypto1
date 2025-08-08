#!/usr/bin/env python3
"""Remove all emojis from live_backtest_clean.py"""

import re

def remove_emojis_from_file(filepath):
    """Remove all emojis from a Python file"""
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define emoji replacements
    emoji_replacements = {
        '📊': '[CHART]',
        '🚀': '[START]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '🔓': '[BUY]',
        '🔒': '[SELL]',
        '💰': '[MONEY]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '🔍': '[DEBUG]',
        '⚠️': '[WARNING]',
        '💼': '[CAPITAL]',
        '🔄': '[TRADES]',
        '🎯': '[TARGET]',
    }
    
    # Replace emojis
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Also remove any remaining emoji characters using regex
    # This regex matches most emoji characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    content = emoji_pattern.sub('', content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Emojis removed from {filepath}")

if __name__ == "__main__":
    remove_emojis_from_file("live_backtest_clean.py")
    print("✓ Done!")

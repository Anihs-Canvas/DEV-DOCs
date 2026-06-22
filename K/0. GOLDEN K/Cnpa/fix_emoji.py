#!/usr/bin/env python3
"""Fix double-encoded emoji in cnpa_main.html.

The corruption: UTF-8 emoji bytes were interpreted as cp1252 characters,
then those characters were re-encoded as UTF-8.

Fix: find cp1252-encoded-emojis-re-encoded-as-UTF8 patterns,
reverse them back to the original emoji.
"""
import re
import sys

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Strategy: find sequences of 2-4 characters that when:
# 1. Encoded as cp1252 (single bytes)
# 2. Decoded as UTF-8
# ...produce valid Unicode in the emoji/symbol ranges.
# We then replace the corrupted text with the correct text.

# Emoji and common symbol ranges to check for:
# U+1F300-U+1FAFF (Misc Symbols, Emoticons, etc.)
# U+2600-U+27BF (Misc Symbols)
# U+2700-U+27BF (Dingbats)
# U+2000-U+206F (General Punctuation, including smart quotes)

def try_fix(text):
    """Try to fix a potentially corrupted sequence.
    Returns (fixed_text, True) if fixable, else (text, False).
    """
    try:
        # Step 1: encode the corrupted text as cp1252 bytes
        raw = text.encode("cp1252")
        # Step 2: decode those bytes as UTF-8
        fixed = raw.decode("utf-8")
        # If the fixed text is the same, no corruption
        if fixed == text:
            return text, False
        # Check that the fixed text contains reasonable characters
        # (emoji, symbols, etc.) - not garbage
        for ch in fixed:
            cp = ord(ch)
            # Allow: common symbols, emoji ranges, ASCII
            if cp < 0x20 and cp not in (0x0A, 0x0D, 0x09):
                return text, False
        return fixed, True
    except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
        return text, False

# Find sequences that look like they might be corrupted emoji
# Pattern: sequences of 2-4 high-byte characters (cp1252-re-encoded UTF-8)
# These typically look like: ðŸ... or â... etc.

# We'll use a byte-level approach: find all runs of non-ASCII characters
# that could be corrupted emoji sequences.

# Approach: iterate through the content, find runs of characters
# where each character's cp1252 byte is >= 0x80, and try to fix them.

fixes = 0
i = 0
result = []
while i < len(content):
    ch = content[i]
    cp = ord(ch)
    
    # Check if this could be the start of a corrupted multi-byte emoji
    # Common start bytes in cp1252 for UTF-8 emoji prefixes:
    # 0xF0 (ð) -> UTF-8 4-byte sequence start
    # 0xC3 (Ã) -> could be part of corruption
    # 0xE2 (â) -> UTF-8 3-byte sequence start for symbols/emoji
    # 0xC2 (Â) -> could be part of corruption
    
    if cp in (0xF0, 0xC3, 0xE2, 0xC2):
        # Try progressively longer sequences (2-8 chars)
        best_fix = None
        best_len = 0
        for length in range(2, 9):
            if i + length > len(content):
                break
            candidate = content[i:i+length]
            fixed, ok = try_fix(candidate)
            if ok and fixed != candidate:
                # Verify: the fixed text should have fewer characters
                # (emoji takes fewer chars than the corrupted form)
                if len(fixed) <= len(candidate):
                    best_fix = fixed
                    best_len = length
        
        if best_fix is not None:
            result.append(best_fix)
            fixes += 1
            i += best_len
            continue
    
    result.append(ch)
    i += 1

if fixes > 0:
    fixed_content = "".join(result)
    # Write fixed file
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    print(f"Fixed {fixes} corrupted sequences")
else:
    print("No fixes found - trying alternative approach...")
    
    # Alternative: try to fix all non-ASCII runs
    fixes2 = 0
    result2 = []
    i = 0
    while i < len(content):
        ch = content[i]
        cp = ord(ch)
        
        if cp > 127:
            # Try sequences of 2-8 chars starting here
            best_fix = None
            best_len = 0
            for length in range(2, 9):
                if i + length > len(content):
                    break
                candidate = content[i:i+length]
                fixed, ok = try_fix(candidate)
                if ok and fixed != candidate and len(fixed) < len(candidate):
                    best_fix = fixed
                    best_len = length
            
            if best_fix:
                result2.append(best_fix)
                fixes2 += 1
                i += best_len
                continue
        
        result2.append(ch)
        i += 1
    
    fixed_content2 = "".join(result2)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(fixed_content2)
    print(f"Fixed {fixes2} corrupted sequences with broader approach")

print("Done.")

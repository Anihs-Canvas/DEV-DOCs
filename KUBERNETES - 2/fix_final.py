"""Final direct fix using Unicode escapes to avoid syntax errors."""
with open('helm.html', 'r', encoding='utf-8') as f:
    text = f.read()

fixes = [
    ('\u00f0\u0178\u201c\u0161', '&#x1F4DA;'),
    ('\u00f0\u0178\u201c\u017d', '&#x1F4CE;'),
    ('\u00f0\u0178\u2014\u00ba', '&#x1F5FA;'),
    ('\u00f0\u0178\u017d\u00af', '&#x1F3AF;'),
    ('\u00f0\u0178\u008f\u0020', '&#x1F3E0;'),
    ('\u00f0\u0178\u0178\u00a2', '&#x1F7E2;'),
    ('\u00f0\u0178\u0178\u00a1', '&#x1F7E1;'),
    ('\u00f0\u0178\u201d\u00b4', '&#x1F534;'),
    ('\u00f0\u0178\u201d\u00a7', '&#x1F527;'),
    ('\u00f0\u0178\u0161\u20ac', '&#x1F680;'),
    ('\u00e2\u0161\u00a0', '&#x26A0;'),
    ('\u00e2\u0161\u00a1', '&#x26A1;'),
    ('\u00e2\u0153\u2026', '&#x2705;'),
    ('\u00e2\u009d\u0152', '&#x274C;'),
    ('\u00f0\u0178\u2019\u00a1', '&#x1F4A1;'),
    ('\u00f0\u0178\u00a7\u00aa', '&#x1F9EA;'),
    ('\u00f0\u0178\u00a7\u0020', '&#x1F9E0;'),
    ('\u00e2\u2020\u2019', '&#x2192;'),
    ('\u00e2\u0160\u017e', '&#x229E;'),
    ('\u00e2\u0160\u0178', '&#x229F;'),
    ('\u00e2\u2013\u00b6', '&#x25B6;'),
    ('\u00e2\u2013\u00bc', '&#x25BC;'),
    ('\u00e2\u02dc\u00b0', '&#x2630;'),
    ('\u00e2\u008f\u00b1', '&#x23F1;'),
    ('\u00f0\u0178\u008f\u2020', '&#x1F3C6;'),
    ('\u00e2\u20ac\u201d', '&#x2014;'),
    ('\u00e2\u20ac\u201c', '&#x2013;'),
    ('\u00e2\u20ac\u00a6', '&#x2026;'),
    ('\u00e2\u02dc\u00b8', '&#x2638;'),
    ('\u00ef\u00b8\u008f', ''),
]

count = 0
for old, new in fixes:
    if old in text:
        c = text.count(old)
        text = text.replace(old, new)
        count += c
        print(f'Fixed {c}x')

# Generic scan for remaining F0 patterns
emoji_cp_map = {
    0x1F4DA: '&#x1F4DA;', 0x1F4E6: '&#x1F4E6;', 0x1F4CA: '&#x1F4CA;',
    0x1F4CB: '&#x1F4CB;', 0x1F4CE: '&#x1F4CE;', 0x1F4D6: '&#x1F4D6;',
    0x1F4C5: '&#x1F4C5;', 0x1F5FA: '&#x1F5FA;', 0x1F3AF: '&#x1F3AF;',
    0x1F3E0: '&#x1F3E0;', 0x1F7E2: '&#x1F7E2;', 0x1F7E1: '&#x1F7E1;',
    0x1F534: '&#x1F534;', 0x1F527: '&#x1F527;', 0x1F680: '&#x1F680;',
    0x26A0: '&#x26A0;', 0x26A1: '&#x26A1;', 0x2705: '&#x2705;',
    0x274C: '&#x274C;', 0x1F4A1: '&#x1F4A1;', 0x1F9EA: '&#x1F9EA;',
    0x1F9E0: '&#x1F9E0;', 0x2192: '&#x2192;', 0x229E: '&#x229E;',
    0x229F: '&#x229F;', 0x25B6: '&#x25B6;', 0x25BC: '&#x25BC;',
    0x2630: '&#x2630;', 0x23F1: '&#x23F1;', 0x1F3C6: '&#x1F3C6;',
    0x2638: '&#x2638;', 0x2014: '&#x2014;', 0x2013: '&#x2013;',
    0x2026: '&#x2026;', 0x1F525: '&#x1F525;', 0x1F4BB: '&#x1F4BB;',
    0x1F512: '&#x1F512;', 0x1F504: '&#x1F504;', 0x1F4C8: '&#x1F4C8;',
    0x1F4AA: '&#x1F4AA;', 0x1F916: '&#x1F916;', 0x1F6E1: '&#x1F6E1;',
    0x1F3D7: '&#x1F3D7;', 0x1F631: '&#x1F631;', 0x1F60E: '&#x1F60E;',
    0x1F389: '&#x1F389;', 0x1F4DD: '&#x1F4DD;',
}

chars = list(text)
new_chars = []
i = 0
extra = 0
while i < len(chars):
    if ord(chars[i]) == 0x00F0 and i+3 < len(chars):
        b = [0xF0, ord(chars[i+1]), ord(chars[i+2]), ord(chars[i+3])]
        if all(0x80 <= x <= 0xBF for x in b[1:]):
            cp = ((b[0]&7)<<18)|((b[1]&0x3F)<<12)|((b[2]&0x3F)<<6)|(b[3]&0x3F)
            if cp in emoji_cp_map:
                new_chars.append(emoji_cp_map[cp])
                i += 4; extra += 1; continue
    elif ord(chars[i]) == 0x00E0 and i+2 < len(chars):
        b = [0xE0, ord(chars[i+1]), ord(chars[i+2])]
        if all(0x80 <= x <= 0xBF for x in b[1:]):
            cp = ((b[0]&0xF)<<12)|((b[1]&0x3F)<<6)|(b[2]&0x3F)
            if cp in emoji_cp_map:
                new_chars.append(emoji_cp_map[cp])
                i += 3; extra += 1; continue
    new_chars.append(chars[i])
    i += 1

if extra:
    text = ''.join(new_chars)
    count += extra
    print(f'Generic fixes: {extra}')

print(f'Total: {count}')
with open('helm.html', 'w', encoding='utf-8') as f:
    f.write(text)
print(f'Size: {len(text)} chars ({len(text.encode("utf-8"))/1024:.1f} KB)')

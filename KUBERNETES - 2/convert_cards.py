"""Convert all card-grid sections to cleaner compact formats."""
import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\finOps_ai.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

def find_matching_close(html, start_pos):
    depth = 1
    pos = html.find('>', start_pos) + 1
    while pos < len(html):
        no = html.find('<div', pos)
        nc = html.find('</div>', pos)
        if no != -1 and no < nc:
            depth += 1
            pos = no + 4
        elif nc != -1:
            depth -= 1
            if depth == 0:
                return nc + 6
            pos = nc + 6
        else:
            return -1
    return -1

def extract_cards(grid_inner):
    cards = []
    for m in re.finditer(r'<div class="info-card[^"]*">', grid_inner):
        card_start = m.start()
        card_end = find_matching_close(grid_inner, card_start)
        if card_end == -1:
            continue
        card_html = grid_inner[card_start:card_end]
        h_match = re.search(r'<h5>(.*?)</h5>', card_html)
        heading = h_match.group(1) if h_match else ''
        h5_end = card_html.find('</h5>')
        if h5_end != -1:
            after_h5 = card_html[h5_end + 5:]
            p_match = re.search(r'<p>(.*?)</p>', after_h5, re.DOTALL)
            para = p_match.group(1).strip() if p_match else ''
        else:
            p_match = re.search(r'<p>(.*?)</p>', card_html, re.DOTALL)
            para = p_match.group(1).strip() if p_match else ''
        cards.append({'heading': heading, 'para': para})
    return cards

def make_compact_list(cards):
    items = []
    for i, card in enumerate(cards):
        items.append(f'                    <div class="cl-item"><span class="cl-num">{i+1:02d}</span><div class="cl-body"><strong>{card["heading"]}</strong><p>{card["para"]}</p></div></div>')
    return '<div class="compact-list">\n' + '\n'.join(items) + '\n                </div>'

def make_compare_row(cards):
    if len(cards) < 2:
        return make_compact_list(cards)
    return '<div class="compare-row">\n                    <div class="cr-col"><h5>' + cards[0]['heading'] + '</h5><p>' + cards[0]['para'] + '</p></div>\n                    <div class="cr-divider"></div>\n                    <div class="cr-col"><h5>' + cards[1]['heading'] + '</h5><p>' + cards[1]['para'] + '</p></div>\n                </div>'

def make_compact_grid(cards):
    items = []
    for card in cards:
        items.append(f'                    <div class="cg-item"><h5>{card["heading"]}</h5><p>{card["para"]}</p></div>')
    return '<div class="compact-grid">\n' + '\n'.join(items) + '\n                </div>'

grids = list(re.finditer(r'<div class="card-grid[^"]*">', content))
conversions = []
failed = 0

for g in grids:
    start = g.start()
    end = find_matching_close(content, start)
    if end == -1:
        failed += 1
        continue
    grid_html = content[start:end]
    cards = extract_cards(grid_html)
    if not cards:
        failed += 1
        continue
    
    n = len(cards)
    if n == 2:
        new_html = make_compare_row(cards)
    elif n == 3:
        new_html = make_compact_grid(cards)
    else:
        new_html = make_compact_list(cards)
    
    conversions.append((start, end, new_html, n))

conversions.sort(key=lambda x: x[0], reverse=True)

counts = {}
for start, end, new_html, n in conversions:
    content = content[:start] + new_html + content[end:]
    counts[n] = counts.get(n, 0) + 1

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Conversions completed:")
for n in sorted(counts):
    print(f"  {n}-card grids: {counts[n]} converted")
print(f"  Total converted: {sum(counts.values())}")
print(f"  Failed: {failed}")
print(f"  card-grid remaining: {len(re.findall(r'<div class=\"card-grid', content))}")

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 3\Backstage.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'id="ch2"' in l and '<div id="ch2">' in l:
        print(f'Ch2 content: line {i+1}')
    if 'id="ch3"' in l and 'chapter-intro' not in l and '<div id="ch3">' in l:
        print(f'Ch3 content: line {i+1}')
    if 'id="ch7"' in l and '<div id="ch7">' in l:
        print(f'Ch7 content: line {i+1}')
    if 'id="ch11"' in l and '<div id="ch11">' in l:
        print(f'Ch11 content: line {i+1}')
    if 'id="ch19"' in l and '<div id="ch19">' in l:
        print(f'Ch19 content: line {i+1}')
print(f'Total: {len(lines)} lines')

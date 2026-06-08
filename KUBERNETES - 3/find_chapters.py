with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 3\Backstage.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="ch1"' in l:
        print(f'Ch1 content start: line {i+1}')
    if 'id="ch2"' in l:
        print(f'Ch2 content start: line {i+1}')
    if 'id="ch3"' in l:
        print(f'Ch3 content start: line {i+1}')
    if 'id="ch4"' in l:
        print(f'Ch4 content start: line {i+1}')
    if 'id="ch5"' in l:
        print(f'Ch5 content start: line {i+1}')
    if 'id="ch6"' in l:
        print(f'Ch6 content start: line {i+1}')
    if 'id="ch7"' in l:
        print(f'Ch7 content start: line {i+1}')
    if 'id="ch8"' in l:
        print(f'Ch8 content start: line {i+1}')
    if 'id="ch9"' in l:
        print(f'Ch9 content start: line {i+1}')
    if 'id="ch10"' in l:
        print(f'Ch10 content start: line {i+1}')
print(f'Total lines: {len(lines)}')

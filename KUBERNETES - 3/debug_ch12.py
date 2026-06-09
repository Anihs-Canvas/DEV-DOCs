import re
c = open('Backstage.html','r',encoding='utf-8').read()
m = re.search(r'Chapter 12 .*? CBA Practice', c)
d = c.rfind('<div class="cba-exam-questions">', 0, m.start())
dp = 0; i = d
while i < len(c):
    if c[i:i+4] == '<div' and c[i:i+5] != '</div>': dp += 1
    elif c[i:i+6] == '</div>':
        dp -= 1
        if dp == 0: e = i+6; break
    i += 1
a = c[e:e+2000]
# Find speed-tip opening
st_start = a.find('<div class="cba-speed-tip">')
print(f"Speed-tip starts at offset {st_start}")
# Find all </div> after that
after_st = a[st_start:]
div_count = after_st.count('</div>')
print(f"Number of </div> after speed-tip: {div_count}")
# Find first </div>
first_div = after_st.find('</div>')
print(f"First </div> at offset {st_start + first_div}")
# Print the speed-tip content
print(f"\nSpeed-tip content ({first_div} chars):")
print(repr(after_st[:first_div+6]))





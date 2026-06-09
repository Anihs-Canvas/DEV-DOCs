import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

qas = len(re.findall(r'class="exam-question-item"', h))
gb = h.count('This is a key Helm certification concept')
details = re.findall(r'<details>.*?</details>', h, re.DOTALL)
doubles = sum(1 for d in details if d.count('class="eq-explanation"') > 1)
noexp = sum(1 for d in details if d.count('class="eq-explanation"') == 0)
ch21 = 'id="ch21"' in h

print("Lines:", h.count('\n'))
print("Q&As:", qas)
print("Generic boilerplates:", gb)
print("Double explanations:", doubles)
print("Missing explanations:", noexp)
print("Ch21 present:", ch21)

# Check chapter divs
for ch in range(1, 22):
    if f'id="ch{ch}"' not in h:
        print(f"MISSING: Ch{ch}")
# Check appendix divs
for app in ['a','b','c','d','e','f']:
    if f'id="appendix-{app}"' not in h:
        print(f"MISSING: Appendix {app.upper()}")

print("\nAll chapters + appendices present:", all(f'id="ch{ch}"' in h for ch in range(1,22)) and all(f'id="appendix-{a}"' in h for a in 'abcdef'))

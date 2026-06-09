import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()
details = re.findall(r'<details>.*?</details>', h, re.DOTALL)
double = [d for d in details if d.count('class="eq-explanation"') > 1]

for i, d in enumerate(double):
    exps = re.findall(r'class="eq-explanation">(.*?)</div>\s*(?=<div class="eq-explanation">|</details>)', d, re.DOTALL)
    print("\nRemaining double #{}: {} exps".format(i+1, len(exps)))
    for j, e in enumerate(exps):
        preview = e[:150].strip().replace('\n',' ').replace('  ',' ')
        print("  Exp {}: {}".format(j+1, preview))

# Also check Ch1 which had the most doubles
ch1_start = h.find('id="ch1"')
ch2_start = h.find('id="ch2"')
ch1 = h[ch1_start:ch2_start]
ch1_doubles = re.findall(r'<details>.*?</details>', ch1, re.DOTALL)
ch1_double = [d for d in ch1_doubles if d.count('class="eq-explanation"') > 1]
print("\nCh1 remaining doubles:", len(ch1_double))

import re
h = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

# Find all details blocks
details = re.findall(r'<details>.*?</details>', h, re.DOTALL)
print("Total Q&A blocks:", len(details))

double = [d for d in details if d.count('class="eq-explanation"') > 1]
print("With double explanations:", len(double))

# Show first few examples
for i, d in enumerate(double[:3]):
    exps = re.findall(r'(class="eq-explanation">.*?</div>)', d, re.DOTALL)
    print("\nExample {}: {} explanation blocks".format(i+1, len(exps)))
    for j, e in enumerate(exps):
        preview = e[:120].replace('\n',' ')
        print("  Exp {}: {}...".format(j+1, preview))

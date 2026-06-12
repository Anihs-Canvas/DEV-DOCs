import re
c=open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()
qs=c.count('exam-question-item')
ans=c.count('eq-answer')
exps=c.count('eq-explanation')
print(f'Questions: {qs} | Answers: {ans} | Explanations: {exps} | Match: {qs==ans==exps}')
diag_in_exp=len(re.findall(r'eq-explanation.*?diagram-container', c, re.DOTALL))
print(f'Explanations with diagrams: {diag_in_exp}/{exps}')

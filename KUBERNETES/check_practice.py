import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8').read()

# For each chapter, find the last major section before the next chapter
for ch in range(1, 21):
    cid = f'id="ch{ch}"'
    ncid = f'id="ch{ch+1}"' if ch < 20 else 'id="appendix-a"'
    
    idx = html.find(cid)
    nidx = html.find(ncid, idx+1) if idx >= 0 else -1
    
    if idx >= 0 and nidx > 0:
        section = html[idx:nidx]
        # Find last significant section
        # Look for cka-exam-questions, ckad-practice-drill, section-block etc
        sections = []
        for m in re.finditer(r'class="(cka-exam-questions|ckad-practice-drill|section-block|chapter-intro|learning-objectives|key-takeaways)"', section):
            sections.append((m.start(), m.group(1)))
        
        if sections:
            last = sections[-1]
            # Check if exam questions or practice drill is last
            is_ok = last[1] in ('cka-exam-questions', 'ckad-practice-drill')
            if not is_ok:
                print(f"Ch{ch}: Last section is {last[1]} (should be cka-exam-questions or ckad-practice-drill)")
        else:
            print(f"Ch{ch}: No sections found")
    else:
        print(f"Ch{ch}: Not found (idx={idx}, nidx={nidx})")

print("\nVerification complete.")

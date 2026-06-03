with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find part1-intro section
start = content.find('id="part1-intro"')
if start > 0:
    # Show surrounding text with repr
    chunk = content[start-200:start+500]
    print(repr(chunk[:300]))
    print("...")
    # Find the closing </section> of part1-intro
    end = content.find('</section>', start)
    # Find the next <section class="chapter-section" id="cat1">
    cat1 = content.find('id="cat1"', end)
    if cat1 > 0:
        # Show from end of part1-intro to cat1
        between = content[end:cat1+20]
        print(f"\nBetween part1-intro </section> and cat1:")
        for line in between.split('\n')[:10]:
            print(f"  |{line}|")

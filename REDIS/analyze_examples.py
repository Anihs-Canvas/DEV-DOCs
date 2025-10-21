import re

# Read the HTML file
with open('redis_commands_full_documentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define sections after line 32460
sections = [
    ('Geospatial Indices', 32460, 33125),
    ('HyperLogLog', 33125, 33242),
    ('JSON', 33242, 33842),
    ('Pub/Sub', 33842, 34629),
    ('Scripting and Functions', 34629, 35194),
    ('Redis Query Engine', 35194, 36050),
    ('Server Management', 36050, 37098),
    ('Stream', 37098, 38670),
    ('Auto-suggest', 38670, 39755),
    ('Time Series', 39755, 40614),
    ('Top-K', 40614, 41625),
    ('Transactions', 41625, 42960),
    ('Vector Set', 42960, 99999),
]

# Get lines of file
lines = content.split('\n')

# Process each section
for section_name, start_line, end_line in sections:
    print(f"\n{'='*80}")
    print(f"SECTION: {section_name}")
    print(f"{'='*80}")
    
    # Extract section content
    section_content = '\n'.join(lines[start_line-1:end_line-1])
    
    # Find all commands (h3 elements with id)
    commands = re.findall(r'<h3[^>]*id="([^"]+)"[^>]*>([^<]+)</h3>', section_content)
    
    if not commands:
        print("No commands found in this section.")
        continue
    
    incomplete_commands = []
    
    for cmd_id, cmd_name in commands:
        # Find the examples for this command
        # Look for pattern of Example 1: through Example 5:
        cmd_pattern = f'id="{cmd_id}"[^<]*</h3>.*?(?=<h3|</section>)'
        match = re.search(cmd_pattern, section_content, re.DOTALL)
        
        if match:
            cmd_section = match.group(0)
            # Count examples
            examples = re.findall(r'<h5>Example (\d+):', cmd_section)
            
            if examples:
                max_example = max(int(e) for e in examples)
                if max_example < 5:
                    incomplete_commands.append((cmd_name.strip(), max_example))
    
    if incomplete_commands:
        print(f"\nCommands with incomplete examples ({len(incomplete_commands)} found):\n")
        for cmd_name, num_examples in sorted(incomplete_commands):
            print(f"  {cmd_name:30} - {num_examples} example(s) (needs {5 - num_examples} more)")
    else:
        print(f"\nAll commands have 5 examples!")


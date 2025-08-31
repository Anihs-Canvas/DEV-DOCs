import re

# Read the file
with open('Events_that_trigger_workflows_mastery.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace grid containers with simple sections
# Pattern: <div class="grid"> followed by examples, ended by </div>
def replace_grid_section(match):
    grid_content = match.group(1)
    # Remove the outer grid div and close the examples section
    # Also remove individual example div wrappers
    cleaned_content = grid_content.replace('        <div class="example">', '      <div class="example">')
    cleaned_content = cleaned_content.replace('        </div>\n\n        <div class="example">', '      </div>\n\n      <div class="example">')
    cleaned_content = cleaned_content.replace('        </div>\n      </div>', '      </div>')
    return cleaned_content

# Find and replace all grid sections
pattern = r'      <div class="grid">\n(.*?)\n      </div>'
new_content = re.sub(pattern, replace_grid_section, content, flags=re.DOTALL)

# Write the updated content back
with open('Events_that_trigger_workflows_mastery.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Grid layouts have been replaced with vertical stacking.")
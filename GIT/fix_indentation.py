import re

# Read the file
with open('Events_that_trigger_workflows_mastery.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix indentation issues for examples
# Replace incorrectly indented div class="example" 
content = re.sub(r'        <div class="example">', '      <div class="example">', content)
content = re.sub(r'          <h4>', '        <h4>', content)
content = re.sub(r'          <pre>', '        <pre>', content)
content = re.sub(r'          <div class="printout">', '        <div class="printout">', content)
content = re.sub(r'        </div>\n\n        <div class="example">', '      </div>\n\n      <div class="example">', content)
content = re.sub(r'        </div>\n    </section>', '      </div>\n    </section>', content)

# Write the updated content back
with open('Events_that_trigger_workflows_mastery.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Indentation issues have been fixed.")
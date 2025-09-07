#!/usr/bin/env python3
"""
Final HTML validation script
"""

from html.parser import HTMLParser
from collections import defaultdict

class FinalHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.line_number = 1
        self.tag_stack = []
        self.issues = []
        
    def handle_starttag(self, tag, attrs):
        if tag.lower() in ['div', 'section', 'pre', 'code', 'ul', 'ol', 'li']:
            self.tag_stack.append({
                'tag': tag.lower(),
                'line': self.line_number
            })
    
    def handle_endtag(self, tag):
        if tag.lower() in ['div', 'section', 'pre', 'code', 'ul', 'ol', 'li']:
            if not self.tag_stack:
                self.issues.append(f"Line {self.line_number}: Extra closing tag </{tag}>")
                return
            
            last_open = self.tag_stack[-1]
            if last_open['tag'] == tag.lower():
                self.tag_stack.pop()
            else:
                self.issues.append(f"Line {self.line_number}: Mismatched closing tag </{tag}>, expected </{last_open['tag']}>")
    
    def handle_data(self, data):
        self.line_number += data.count('\n')

def validate_html(file_path):
    validator = FinalHTMLValidator()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validator.feed(content)
        
        print(f"Validation results for: {file_path}")
        print(f"Found {len(validator.issues)} issues")
        print(f"Found {len(validator.tag_stack)} unclosed tags")
        
        if validator.issues:
            print("\nFirst 10 issues:")
            for issue in validator.issues[:10]:
                print(f"  {issue}")
        
        if validator.tag_stack:
            print("\nUnclosed tags:")
            for tag in validator.tag_stack:
                print(f"  Line {tag['line']}: Unclosed <{tag['tag']}>")
        
        return len(validator.issues) == 0 and len(validator.tag_stack) == 0
        
    except Exception as e:
        print(f"Error validating file: {e}")
        return False

def main():
    final_file = r"C:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\Kubernetes_CORRECTED_FINAL.html"
    is_valid = validate_html(final_file)
    
    if is_valid:
        print("\nHTML is now valid!")
    else:
        print("\nHTML still has issues")

if __name__ == "__main__":
    main()
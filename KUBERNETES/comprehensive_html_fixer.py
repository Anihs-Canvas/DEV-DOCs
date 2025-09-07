#!/usr/bin/env python3
"""
Comprehensive HTML structure fixer for Kubernetes documentation.
This script analyzes HTML structure and fixes all tag mismatches.
"""

import re
from collections import defaultdict
from html.parser import HTMLParser
import sys

class HTMLStructureFixer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.line_number = 1
        self.char_position = 0
        self.tag_stack = []  # Stack of open tags with positions
        self.issues = []     # List of issues found
        self.lines = []      # Store all lines for fixing
        self.in_pre = False  # Track if we're inside <pre> tags
        
    def handle_starttag(self, tag, attrs):
        position = f"Line {self.line_number}"
        
        if tag.lower() == 'pre':
            self.in_pre = True
        
        # Only track structural tags that need to be balanced
        if tag.lower() in ['div', 'section', 'pre', 'code', 'ul', 'ol', 'li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.tag_stack.append({
                'tag': tag.lower(),
                'line': self.line_number,
                'position': position
            })
    
    def handle_endtag(self, tag):
        if tag.lower() == 'pre':
            self.in_pre = False
            
        # Only process structural tags
        if tag.lower() in ['div', 'section', 'pre', 'code', 'ul', 'ol', 'li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if not self.tag_stack:
                self.issues.append(f"Line {self.line_number}: Extra closing tag </{tag}>")
                return
            
            # Check if this closing tag matches the most recent opening tag
            last_open = self.tag_stack[-1]
            if last_open['tag'] == tag.lower():
                self.tag_stack.pop()
            else:
                # Mismatch - look for matching opening tag in stack
                found_match = False
                for i in range(len(self.tag_stack) - 1, -1, -1):
                    if self.tag_stack[i]['tag'] == tag.lower():
                        # Found match, close all intervening tags
                        for j in range(len(self.tag_stack) - 1, i, -1):
                            unclosed = self.tag_stack[j]
                            self.issues.append(f"Line {unclosed['line']}: Unclosed tag <{unclosed['tag']}>")
                        # Remove all tags from the match onwards
                        self.tag_stack = self.tag_stack[:i]
                        found_match = True
                        break
                
                if not found_match:
                    self.issues.append(f"Line {self.line_number}: Extra closing tag </{tag}>")
    
    def handle_data(self, data):
        # Count newlines to track line numbers
        self.line_number += data.count('\n')
    
    def get_unclosed_tags(self):
        """Return all unclosed tags"""
        return self.tag_stack
    
    def fix_html_structure(self, file_path):
        """Main method to fix HTML structure"""
        print(f"Analyzing HTML structure in: {file_path}")
        
        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.lines = content.split('\n')
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Parse HTML
        try:
            self.feed(content)
        except Exception as e:
            print(f"HTML parsing error: {e}")
            # Continue with what we have
        
        # Get all unclosed tags
        unclosed_tags = self.get_unclosed_tags()
        
        print(f"\nFound {len(self.issues)} HTML issues:")
        for issue in self.issues[:20]:  # Show first 20 issues
            print(f"  {issue}")
        if len(self.issues) > 20:
            print(f"  ... and {len(self.issues) - 20} more issues")
        
        print(f"\nFound {len(unclosed_tags)} unclosed tags:")
        for tag_info in unclosed_tags:
            print(f"  Line {tag_info['line']}: Unclosed <{tag_info['tag']}>")
        
        return self.apply_fixes(file_path, content)
    
    def apply_fixes(self, file_path, content):
        """Apply structural fixes to the HTML"""
        lines = content.split('\n')
        fixed_lines = []
        
        # Strategy: Add missing closing tags at logical points
        print(f"\nApplying fixes...")
        
        in_code_block = False
        pre_depth = 0
        div_depth = 0
        section_depth = 0
        
        for i, line in enumerate(lines):
            current_line = line
            line_num = i + 1
            
            # Track pre/code blocks
            if '<pre>' in line or '<pre ' in line:
                in_code_block = True
                pre_depth += 1
            if '</pre>' in line:
                in_code_block = False
                pre_depth = max(0, pre_depth - 1)
            
            # Track div depth
            div_opens = len(re.findall(r'<div[^>]*>', line))
            div_closes = len(re.findall(r'</div>', line))
            div_depth += div_opens - div_closes
            
            # Track section depth  
            section_opens = len(re.findall(r'<section[^>]*>', line))
            section_closes = len(re.findall(r'</section>', line))
            section_depth += section_opens - section_closes
            
            # Fix specific known issues
            
            # If we find unclosed code/pre tags, close them
            if in_code_block and line.strip() and not line.strip().startswith('<') and not line.strip().startswith(' ') and line_num > 1194:
                if '</code>' not in line and '</pre>' not in line:
                    # Check if this might be the end of a code block
                    if line.strip().endswith('</div>') or line.strip().endswith('<h4>'):
                        current_line = line.replace('</div>', '</code></pre></div>')
                        current_line = current_line.replace('<h4>', '</code></pre>\n<h4>')
                        in_code_block = False
                        pre_depth = 0
            
            # Add missing closing tags at section boundaries
            if '<section' in line and div_depth > 5:  # Too many open divs
                # Close some divs before starting new section
                current_line = '</div>' * min(3, div_depth - 2) + '\n' + current_line
                div_depth -= min(3, div_depth - 2)
            
            # Fix common patterns where divs should be closed
            if line.strip() == '<!-- Pod Resource -->' and div_depth > 3:
                current_line = '</div>\n' + current_line
                div_depth -= 1
            
            fixed_lines.append(current_line)
        
        # Add any remaining closing tags at the end
        while div_depth > 0:
            fixed_lines.append('</div>')
            div_depth -= 1
        
        while section_depth > 0:
            fixed_lines.append('</section>')
            section_depth -= 1
        
        while pre_depth > 0:
            fixed_lines.append('</code></pre>')
            pre_depth -= 1
        
        # Write the fixed content
        output_path = file_path.replace('.html', '_FINAL.html')
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            print(f"\nFixed HTML written to: {output_path}")
            return True
        except Exception as e:
            print(f"Error writing fixed file: {e}")
            return False

def main():
    fixer = HTMLStructureFixer()
    input_file = r"C:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\Kubernetes_CORRECTED.html"
    
    success = fixer.fix_html_structure(input_file)
    if success:
        print("\n✅ HTML structure fixing completed!")
    else:
        print("\n❌ HTML structure fixing failed!")

if __name__ == "__main__":
    main()
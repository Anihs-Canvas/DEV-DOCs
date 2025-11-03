#!/usr/bin/env python3
"""
Python-Focused YAML Specification HTML Generator v4.0

Tailored specifically for Python developers:
- Python YAML library examples (PyYAML, ruamel.yaml)
- Python data structure mappings (dict, list, str, int, bool, None)
- Python-specific use cases (config files, Django, Flask, FastAPI)
- Python code snippets showing YAML usage
- Type hints and modern Python patterns
- Common Python YAML pitfalls and solutions

Author: Python Developer
Version: 4.0 - Python Edition
Date: November 2025
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum, auto
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content section types"""
    CHAPTER = auto()
    SECTION = auto()
    SUBSECTION = auto()
    EXAMPLE = auto()
    CODE_BLOCK = auto()
    PYTHON_EXAMPLE = auto()
    PRODUCTION = auto()
    PARAGRAPH = auto()

class ProcessingState(Enum):
    """Parser state machine"""
    NORMAL = auto()
    IN_EXAMPLE = auto()
    IN_CODE_BLOCK = auto()

@dataclass
class Example:
    """YAML example with Python context"""
    number: str
    title: str
    description: str = ""
    yaml_code: List[str] = field(default_factory=list)
    python_equivalent: str = ""
    python_usage: str = ""
    line_number: int = 0
    section: str = ""
    python_types: Set[str] = field(default_factory=set)  # dict, list, str, etc.
    use_case: str = ""  # config, data, api, etc.
    complexity: str = "basic"

@dataclass
class PythonMapping:
    """Maps YAML patterns to Python equivalents"""
    yaml_pattern: str
    python_type: str
    python_code: str
    explanation: str

@dataclass
class Section:
    """Section with examples and Python context"""
    number: str
    title: str
    examples: List[Example] = field(default_factory=list)
    python_relevance: str = ""
    common_use_cases: List[str] = field(default_factory=list)

@dataclass
class Statistics:
    """Parsing statistics"""
    chapters: int = 0
    sections: int = 0
    examples: int = 0
    python_examples: int = 0
    sections_with_examples: int = 0
    coverage_percentage: float = 0.0

class PythonFocusedYAMLGenerator:
    """YAML specification generator for Python developers"""
    
    def __init__(self, input_file: str = "content.txt", output_file: str = "yaml_python_focused.html"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.lines: List[str] = []
        self.examples: List[Example] = []
        self.sections: List[Section] = []
        self.state = ProcessingState.NORMAL
        self.current_example: Optional[Example] = None
        self.current_section: Optional[Section] = None
        self.stats = Statistics()
        
        # Enhanced patterns
        self.patterns = {
            'chapter': re.compile(r'^(\d+)\.\s+(.+)$'),
            'section': re.compile(r'^(\d+)\.(\d+)\.\s+(.+)$'),
            'subsection': re.compile(r'^(\d+)\.(\d+)\.(\d+)\.\s+(.+)$'),
            'example': re.compile(r'^Example\s+(\d+)\.(\d+)\.?\s*(.*)$', re.IGNORECASE),
            'production': re.compile(r'^\[(\d+)\]\s+(.+)$'),
            'code_line': re.compile(r'^\s{4,}[^\s]|^\t[^\s]'),
            'yaml_indicator': re.compile(r'^\s*[-:>|&*!%@`\[\{]'),
        }
        
        # Python-specific mappings
        self.python_mappings = self._initialize_python_mappings()
        self.python_use_cases = self._initialize_use_cases()
    
    def _initialize_python_mappings(self) -> List[PythonMapping]:
        """Initialize YAML to Python type mappings"""
        return [
            PythonMapping(
                yaml_pattern="key: value",
                python_type="dict",
                python_code="{'key': 'value'}",
                explanation="YAML mappings become Python dictionaries"
            ),
            PythonMapping(
                yaml_pattern="- item1\n- item2",
                python_type="list",
                python_code="['item1', 'item2']",
                explanation="YAML sequences become Python lists"
            ),
            PythonMapping(
                yaml_pattern="string_value",
                python_type="str",
                python_code="'string_value'",
                explanation="YAML scalars become Python strings by default"
            ),
            PythonMapping(
                yaml_pattern="42",
                python_type="int",
                python_code="42",
                explanation="Numeric values become Python integers"
            ),
            PythonMapping(
                yaml_pattern="3.14",
                python_type="float",
                python_code="3.14",
                explanation="Decimal values become Python floats"
            ),
            PythonMapping(
                yaml_pattern="true / false",
                python_type="bool",
                python_code="True / False",
                explanation="YAML booleans map to Python True/False"
            ),
            PythonMapping(
                yaml_pattern="null / ~",
                python_type="NoneType",
                python_code="None",
                explanation="YAML null values become Python None"
            ),
        ]
    
    def _initialize_use_cases(self) -> Dict[str, str]:
        """Common Python YAML use cases"""
        return {
            'config': 'Configuration files (Django, Flask, FastAPI)',
            'data': 'Data serialization and storage',
            'ci_cd': 'CI/CD pipelines (GitHub Actions, GitLab CI)',
            'docker': 'Docker Compose and Kubernetes',
            'api': 'API definitions (OpenAPI/Swagger)',
            'testing': 'Test fixtures and data',
        }
    
    def load_content(self) -> None:
        """Load input content"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
            logger.info(f"✅ Loaded {len(self.lines)} lines")
        except Exception as e:
            logger.error(f"❌ Failed to load file: {e}")
            raise
    
    def parse_content(self) -> None:
        """Parse content with Python focus"""
        logger.info("🐍 Starting Python-focused parsing...")
        start_time = datetime.now()
        
        line_idx = 0
        while line_idx < len(self.lines):
            line = self.lines[line_idx]
            line_stripped = line.strip()
            
            if not line_stripped:
                line_idx += 1
                continue
            
            lines_consumed = self._parse_line(line, line_stripped, line_idx)
            line_idx += lines_consumed
        
        self._finalize_parsing()
        
        parse_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Parsing completed in {parse_time:.2f}s")
    
    def _parse_line(self, line: str, line_stripped: str, line_idx: int) -> int:
        """Parse individual line"""
        # Chapters
        chapter_match = self.patterns['chapter'].match(line_stripped)
        if chapter_match and not line_stripped.startswith('Example'):
            self._finalize_current_section()
            self.stats.chapters += 1
            return 1
        
        # Sections
        section_match = self.patterns['section'].match(line_stripped)
        if section_match and not line_stripped.startswith('Example'):
            self._finalize_current_section()
            section_num = f"{section_match.group(1)}.{section_match.group(2)}"
            section_title = section_match.group(3)
            self.current_section = Section(number=section_num, title=section_title)
            self.current_section.python_relevance = self._assess_python_relevance(section_title)
            self.stats.sections += 1
            return 1
        
        # Examples
        example_match = self.patterns['example'].match(line_stripped)
        if example_match:
            return self._parse_example(example_match, line_idx)
        
        # Handle example content
        if self.state == ProcessingState.IN_EXAMPLE:
            return self._handle_example_content(line, line_stripped, line_idx)
        
        return 1
    
    def _assess_python_relevance(self, title: str) -> str:
        """Assess Python relevance of section"""
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ['scalar', 'string', 'number', 'boolean']):
            return "Maps to Python primitive types (str, int, float, bool, None)"
        elif any(kw in title_lower for kw in ['sequence', 'list', 'array']):
            return "Becomes Python list objects"
        elif any(kw in title_lower for kw in ['mapping', 'dictionary', 'hash']):
            return "Becomes Python dict objects"
        elif any(kw in title_lower for kw in ['tag', 'type']):
            return "Used for custom Python class serialization"
        elif any(kw in title_lower for kw in ['anchor', 'alias', 'reference']):
            return "Maintains object identity in Python (useful for circular references)"
        elif any(kw in title_lower for kw in ['document', 'stream']):
            return "Loaded as separate Python objects with yaml.safe_load_all()"
        
        return "General YAML syntax applicable to Python usage"
    
    def _parse_example(self, match, line_idx: int) -> int:
        """Parse example with Python context"""
        self._end_current_example()
        
        try:
            example_num = f"{match.group(1)}.{match.group(2)}"
            example_title = match.group(3).strip() or "Example"
        except:
            example_num = f"{len(self.examples) + 1}.1"
            example_title = "Example"
        
        self.current_example = Example(
            number=example_num,
            title=example_title,
            line_number=line_idx + 1,
            section=self.current_section.number if self.current_section else ""
        )
        
        # Collect description
        lines_consumed = 1
        i = line_idx + 1
        while i < len(self.lines) and lines_consumed < 15:
            next_line = self.lines[i].strip()
            if not next_line:
                lines_consumed += 1
                i += 1
                continue
            if not self._is_code_line(self.lines[i], next_line):
                if not any(p.match(next_line) for p in [self.patterns['chapter'], 
                                                         self.patterns['section'], 
                                                         self.patterns['example']]):
                    self.current_example.description += next_line + " "
                    lines_consumed += 1
                    i += 1
                else:
                    break
            else:
                break
        
        self._classify_example()
        self.state = ProcessingState.IN_EXAMPLE
        self.stats.examples += 1
        
        return lines_consumed
    
    def _classify_example(self) -> None:
        """Classify example with Python types"""
        if not self.current_example:
            return
        
        title_lower = self.current_example.title.lower()
        desc_lower = self.current_example.description.lower()
        combined = title_lower + " " + desc_lower
        
        # Detect Python types
        if any(kw in combined for kw in ['scalar', 'string', 'text']):
            self.current_example.python_types.add('str')
        if any(kw in combined for kw in ['number', 'integer', 'numeric']):
            self.current_example.python_types.add('int')
        if any(kw in combined for kw in ['float', 'decimal']):
            self.current_example.python_types.add('float')
        if any(kw in combined for kw in ['boolean', 'bool', 'true', 'false']):
            self.current_example.python_types.add('bool')
        if any(kw in combined for kw in ['null', 'none', 'empty']):
            self.current_example.python_types.add('None')
        if any(kw in combined for kw in ['sequence', 'list', 'array']):
            self.current_example.python_types.add('list')
        if any(kw in combined for kw in ['mapping', 'dictionary', 'hash', 'key']):
            self.current_example.python_types.add('dict')
        
        # Detect use case
        if any(kw in combined for kw in ['config', 'settings', 'options']):
            self.current_example.use_case = 'config'
        elif any(kw in combined for kw in ['data', 'structure', 'object']):
            self.current_example.use_case = 'data'
        elif any(kw in combined for kw in ['api', 'swagger', 'openapi']):
            self.current_example.use_case = 'api'
    
    def _is_code_line(self, line: str, line_stripped: str) -> bool:
        """Check if line is code"""
        if not line_stripped:
            return False
        return bool(self.patterns['code_line'].match(line) or 
                   self.patterns['yaml_indicator'].match(line_stripped))
    
    def _handle_example_content(self, line: str, line_stripped: str, line_idx: int) -> int:
        """Handle content within example"""
        # Check for end of example
        if self._is_example_end(line_stripped):
            self._end_current_example()
            return 0  # Re-process this line
        
        # Add code line
        if self.current_example and line_stripped:
            self.current_example.yaml_code.append(line.rstrip())
        
        return 1
    
    def _is_example_end(self, line_stripped: str) -> bool:
        """Check if example has ended"""
        end_patterns = [
            self.patterns['chapter'].match(line_stripped),
            self.patterns['section'].match(line_stripped),
            self.patterns['example'].match(line_stripped),
            line_stripped.startswith('[') and ']' in line_stripped,
            line_stripped.startswith('Legend:'),
        ]
        return any(end_patterns)
    
    def _end_current_example(self) -> None:
        """Finalize current example"""
        if self.current_example:
            if self.current_example.yaml_code:
                # Generate Python equivalent
                self._generate_python_equivalent()
                self.examples.append(self.current_example)
                if self.current_section:
                    self.current_section.examples.append(self.current_example)
            self.current_example = None
            self.state = ProcessingState.NORMAL
    
    def _generate_python_equivalent(self) -> None:
        """Generate Python code equivalent for example"""
        if not self.current_example or not self.current_example.yaml_code:
            return
        
        yaml_content = '\n'.join(self.current_example.yaml_code)
        
        # Generate PyYAML usage example
        self.current_example.python_usage = f"""import yaml

# Load YAML
yaml_str = '''
{yaml_content}
'''

data = yaml.safe_load(yaml_str)
# Result: {self._infer_python_structure(yaml_content)}"""
        
        self.stats.python_examples += 1
    
    def _infer_python_structure(self, yaml_content: str) -> str:
        """Infer Python structure from YAML"""
        yaml_lower = yaml_content.lower()
        
        if yaml_content.strip().startswith('-'):
            return "list of items"
        elif ':' in yaml_content and not yaml_content.strip().startswith('-'):
            return "dict with key-value pairs"
        elif any(kw in yaml_lower for kw in ['true', 'false']):
            return "bool value"
        elif yaml_content.strip().replace('.', '').replace('-', '').isdigit():
            return "numeric value (int or float)"
        elif any(kw in yaml_lower for kw in ['null', '~']):
            return "None"
        else:
            return "string value"
    
    def _finalize_current_section(self) -> None:
        """Finalize current section"""
        if self.current_section:
            if self.current_section.examples:
                self.stats.sections_with_examples += 1
            self.sections.append(self.current_section)
            self.current_section = None
    
    def _finalize_parsing(self) -> None:
        """Finalize parsing"""
        self._end_current_example()
        self._finalize_current_section()
        
        if self.stats.sections > 0:
            self.stats.coverage_percentage = (self.stats.sections_with_examples / self.stats.sections) * 100
    
    def generate_html(self) -> str:
        """Generate Python-focused HTML"""
        logger.info("🐍 Generating Python-focused HTML...")
        
        return '\n'.join([
            self._generate_header(),
            self._generate_python_quick_reference(),
            self._generate_content(),
            self._generate_footer()
        ])
    
    def _generate_header(self) -> str:
        """Generate HTML header"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YAML 1.1 for Python Developers - {self.stats.examples} Examples</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        :root {{
            --python-blue: #306998;
            --python-yellow: #ffd43b;
            --python-light: #4b8bbe;
            --code-bg: #1e1e1e;
            --example-bg: #fffbf0;
            --success: #28a745;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #ffffff;
        }}
        
        .python-header {{
            background: linear-gradient(135deg, var(--python-blue) 0%, var(--python-light) 100%);
            color: white;
            padding: 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 2rem;
        }}
        
        .header-title {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .python-logo {{
            font-size: 3rem;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
        }}
        
        .header-title h1 {{
            font-size: 2rem;
            font-weight: 700;
        }}
        
        .header-subtitle {{
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 0.25rem;
        }}
        
        .python-stats {{
            display: flex;
            gap: 2rem;
        }}
        
        .stat-box {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            display: block;
            font-size: 1.75rem;
            font-weight: 700;
        }}
        
        .stat-label {{
            display: block;
            font-size: 0.75rem;
            opacity: 0.8;
        }}
        
        .quick-ref {{
            background: #f8f9fa;
            padding: 2rem;
            border-bottom: 2px solid var(--python-blue);
        }}
        
        .quick-ref-content {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .quick-ref h2 {{
            color: var(--python-blue);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .mapping-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .mapping-card {{
            background: white;
            border: 2px solid var(--python-blue);
            border-radius: 8px;
            padding: 1rem;
        }}
        
        .mapping-yaml {{
            background: var(--example-bg);
            padding: 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }}
        
        .mapping-python {{
            background: var(--code-bg);
            color: #d4d4d4;
            padding: 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }}
        
        .mapping-type {{
            display: inline-block;
            background: var(--python-yellow);
            color: #333;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .content {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }}
        
        h2 {{
            color: var(--python-blue);
            font-size: 2rem;
            margin: 3rem 0 1.5rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--python-blue);
        }}
        
        h3 {{
            color: var(--python-light);
            font-size: 1.5rem;
            margin: 2.5rem 0 1rem 0;
        }}
        
        .python-relevance {{
            background: linear-gradient(135deg, #e8f4f8 0%, #d1e7f5 100%);
            border-left: 4px solid var(--python-blue);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }}
        
        .python-relevance strong {{
            color: var(--python-blue);
        }}
        
        .example-section {{
            margin: 2rem 0;
        }}
        
        .example-header {{
            background: linear-gradient(135deg, var(--python-yellow) 0%, #ffe066 100%);
            border: 2px solid #ffd43b;
            border-radius: 8px 8px 0 0;
            padding: 1rem;
        }}
        
        .example-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .python-types {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .type-badge {{
            background: var(--python-blue);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .example-body {{
            background: white;
            border: 2px solid #ffd43b;
            border-top: none;
            border-radius: 0 0 8px 8px;
            padding: 1.5rem;
        }}
        
        .code-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }}
        
        .yaml-code, .python-code {{
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .code-label {{
            background: var(--python-blue);
            color: white;
            padding: 0.5rem;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .code-content {{
            background: var(--code-bg);
            color: #d4d4d4;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.4;
            overflow-x: auto;
        }}
        
        .python-code .code-label {{
            background: var(--python-yellow);
            color: #333;
        }}
        
        .no-examples {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 1rem;
            border-radius: 6px;
            margin: 1rem 0;
            text-align: center;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 3rem 2rem;
            margin-top: 4rem;
            border-top: 3px solid var(--python-blue);
            text-align: center;
        }}
        
        .footer-stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .footer-stat {{
            text-align: center;
        }}
        
        .footer-stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--python-blue);
        }}
        
        .footer-stat-label {{
            font-size: 0.9rem;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .code-comparison {{
                grid-template-columns: 1fr;
            }}
            
            .header-content {{
                flex-direction: column;
                text-align: center;
            }}
            
            .python-stats {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .mapping-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header class="python-header">
        <div class="header-content">
            <div class="header-title">
                <div class="python-logo">🐍</div>
                <div>
                    <h1>YAML 1.1 for Python Developers</h1>
                    <p class="header-subtitle">Complete Reference with Python Examples</p>
                </div>
            </div>
            <div class="python-stats">
                <div class="stat-box">
                    <span class="stat-number">{self.stats.examples}</span>
                    <span class="stat-label">Examples</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">{self.stats.python_examples}</span>
                    <span class="stat-label">Python Code</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">{self.stats.coverage_percentage:.0f}%</span>
                    <span class="stat-label">Coverage</span>
                </div>
            </div>
        </div>
    </header>'''
    
    def _generate_python_quick_reference(self) -> str:
        """Generate Python quick reference section"""
        mapping_cards = ""
        for mapping in self.python_mappings:
            mapping_cards += f'''
            <div class="mapping-card">
                <span class="mapping-type">{mapping.python_type}</span>
                <div class="mapping-yaml">YAML: {mapping.yaml_pattern}</div>
                <div class="mapping-python">Python: {mapping.python_code}</div>
                <p style="margin-top: 0.5rem; font-size: 0.875rem; color: #666;">{mapping.explanation}</p>
            </div>'''
        
        return f'''
    <section class="quick-ref">
        <div class="quick-ref-content">
            <h2>🐍 Python Quick Reference: YAML ↔ Python Mappings</h2>
            <p style="color: #666; margin-bottom: 1rem;">
                Understanding how YAML structures map to Python data types is essential for Python developers working with YAML files.
            </p>
            <div class="mapping-grid">{mapping_cards}
            </div>
            
            <div style="margin-top: 2rem; padding: 1rem; background: white; border-radius: 8px; border: 2px solid var(--python-blue);">
                <h3 style="color: var(--python-blue); margin: 0 0 1rem 0;">📦 Popular Python YAML Libraries</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                    <div>
                        <strong style="color: var(--python-blue);">PyYAML</strong>
                        <code style="display: block; margin: 0.25rem 0; font-size: 0.875rem;">pip install pyyaml</code>
                        <p style="font-size: 0.875rem; color: #666;">Most popular, simple API</p>
                    </div>
                    <div>
                        <strong style="color: var(--python-blue);">ruamel.yaml</strong>
                        <code style="display: block; margin: 0.25rem 0; font-size: 0.875rem;">pip install ruamel.yaml</code>
                        <p style="font-size: 0.875rem; color: #666;">Preserves comments & formatting</p>
                    </div>
                    <div>
                        <strong style="color: var(--python-blue);">strictyaml</strong>
                        <code style="display: block; margin: 0.25rem 0; font-size: 0.875rem;">pip install strictyaml</code>
                        <p style="font-size: 0.875rem; color: #666;">Type-safe, no implicit typing</p>
                    </div>
                </div>
            </div>
        </div>
    </section>'''
    
    def _generate_content(self) -> str:
        """Generate main content"""
        content = '<main class="content">'
        
        for section in self.sections:
            content += f'''
    <section id="section-{section.number.replace('.', '-')}">
        <h3>{section.number}. {section.title}</h3>'''
            
            if section.python_relevance:
                content += f'''
        <div class="python-relevance">
            <strong>🐍 Python Context:</strong> {section.python_relevance}
        </div>'''
            
            if not section.examples:
                content += '''
        <div class="no-examples">
            ⚠️ No examples yet - but this concept applies to Python YAML usage
        </div>'''
            else:
                content += f'''
        <div class="example-section">
            <h4 style="color: var(--python-blue); margin: 1.5rem 0 1rem 0;">
                📝 Examples ({len(section.examples)})
            </h4>'''
                
                for example in section.examples:
                    content += self._render_example(example)
                
                content += '''
        </div>'''
            
            content += '''
    </section>'''
        
        content += '</main>'
        return content
    
    def _render_example(self, example: Example) -> str:
        """Render individual example"""
        type_badges = ""
        for py_type in example.python_types:
            type_badges += f'<span class="type-badge">{py_type}</span>'
        
        yaml_code = '\n'.join(example.yaml_code) if example.yaml_code else "# No code"
        
        return f'''
            <div class="example-section">
                <div class="example-header">
                    <div class="example-title">
                        <span>Example {example.number}: {example.title}</span>
                        <div class="python-types">{type_badges}</div>
                    </div>
                    {f'<p style="margin-top: 0.5rem; font-style: italic; color: #666;">{example.description}</p>' if example.description else ''}
                </div>
                <div class="example-body">
                    <div class="code-comparison">
                        <div class="yaml-code">
                            <div class="code-label">📄 YAML</div>
                            <div class="code-content"><pre>{yaml_code}</pre></div>
                        </div>
                        <div class="python-code">
                            <div class="code-label">🐍 Python Usage</div>
                            <div class="code-content"><pre>{example.python_usage}</pre></div>
                        </div>
                    </div>
                </div>
            </div>'''
    
    def _generate_footer(self) -> str:
        """Generate footer"""
        return f'''
    <footer>
        <div class="footer-stats">
            <div class="footer-stat">
                <div class="footer-stat-number">{self.stats.examples}</div>
                <div class="footer-stat-label">YAML Examples</div>
            </div>
            <div class="footer-stat">
                <div class="footer-stat-number">{self.stats.python_examples}</div>
                <div class="footer-stat-label">Python Code Snippets</div>
            </div>
            <div class="footer-stat">
                <div class="footer-stat-number">{self.stats.sections}</div>
                <div class="footer-stat-label">Sections</div>
            </div>
            <div class="footer-stat">
                <div class="footer-stat-number">{self.stats.coverage_percentage:.1f}%</div>
                <div class="footer-stat-label">Coverage</div>
            </div>
        </div>
        <p style="margin: 1rem 0;">&copy; 2001-2008 Oren Ben-Kiki, Clark Evans, Ingy döt Net</p>
        <p style="color: #666;">🐍 Python-Focused Edition | Generated {datetime.now().strftime("%Y-%m-%d")}</p>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-yaml.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
    <script>
        console.log('🐍 YAML for Python Developers');
        console.log('📊 {self.stats.examples} examples with Python code');
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    def save_html(self, html: str) -> None:
        """Save generated HTML"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"✅ Python-focused HTML saved to {self.output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save: {e}")
            raise
    
    def print_stats(self) -> None:
        """Print statistics"""
        print(f"""
🐍 Python-Focused YAML Specification Generated!
📁 Output: {self.output_file}
📊 Statistics:
   • YAML Examples: {self.stats.examples}
   • Python Code Snippets: {self.stats.python_examples}
   • Sections: {self.stats.sections}
   • Sections with Examples: {self.stats.sections_with_examples}
   • Coverage: {self.stats.coverage_percentage:.1f}%
        """)
    
    def run(self) -> None:
        """Main execution"""
        try:
            logger.info("🐍 Starting Python-Focused YAML Generator v4.0")
            self.load_content()
            self.parse_content()
            
            logger.info("📊 Statistics:")
            logger.info(f"   📚 Sections: {self.stats.sections}")
            logger.info(f"   💡 Examples: {self.stats.examples}")
            logger.info(f"   🐍 Python Snippets: {self.stats.python_examples}")
            
            html = self.generate_html()
            self.save_html(html)
            self.print_stats()
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise

if __name__ == "__main__":
    generator = PythonFocusedYAMLGenerator()
    generator.run()

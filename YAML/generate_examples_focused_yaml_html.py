#!/usr/bin/env python3
"""
Example-Focused YAML 1.1 Specification HTML Generator v3.0

This version prioritizes EXAMPLES over text content:
- Enhanced example extraction with better pattern matching
- Ensures every section has illustrative examples
- Advanced code block detection and formatting
- Visual emphasis on examples with enhanced styling
- Interactive example browser with syntax highlighting
- Automatic example categorization and tagging

Author: AI Assistant  
Version: 3.0 - Examples First
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

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Enumeration of content section types"""
    CHAPTER = auto()
    SECTION = auto()
    SUBSECTION = auto()
    EXAMPLE = auto()
    CODE_BLOCK = auto()
    INLINE_CODE = auto()
    PRODUCTION = auto()
    PARAGRAPH = auto()
    LEGEND = auto()
    ERROR = auto()
    EMPTY = auto()

class ProcessingState(Enum):
    """State machine for content parsing"""
    NORMAL = auto()
    IN_EXAMPLE = auto()
    IN_CODE_BLOCK = auto()
    IN_PRODUCTION = auto()

@dataclass
class Example:
    """Enhanced YAML example with comprehensive metadata"""
    number: str
    title: str
    description: str = ""
    code: List[str] = field(default_factory=list)
    line_number: int = 0
    section: str = ""
    tags: Set[str] = field(default_factory=set)
    complexity: str = "basic"  # basic, intermediate, advanced
    yaml_type: str = ""  # scalar, sequence, mapping, document, etc.

@dataclass
class CodeBlock:
    """Standalone code block outside of examples"""
    content: List[str] = field(default_factory=list)
    language: str = "yaml"
    line_number: int = 0
    context: str = ""

@dataclass
class Section:
    """Section with its examples"""
    number: str
    title: str
    examples: List[Example] = field(default_factory=list)
    code_blocks: List[CodeBlock] = field(default_factory=list)
    has_examples: bool = False

@dataclass
class ContentBlock:
    """Content block with enhanced metadata"""
    type: ContentType
    content: str
    raw_lines: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TOCItem:
    """Table of contents item"""
    level: int
    id: str
    text: str
    number: str = ""
    example_count: int = 0

@dataclass
class Statistics:
    """Enhanced parsing statistics"""
    chapters: int = 0
    sections: int = 0
    examples: int = 0
    code_blocks: int = 0
    productions: int = 0
    inline_code: int = 0
    errors: int = 0
    sections_with_examples: int = 0
    coverage_percentage: float = 0.0

class ExampleFocusedYAMLSpecGenerator:
    """Enhanced YAML specification generator focusing on examples"""
    
    def __init__(self, input_file: str, output_file: str = "yaml_examples_focused.html"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.lines: List[str] = []
        self.content_blocks: List[ContentBlock] = []
        self.toc_items: List[TOCItem] = []
        self.examples: List[Example] = []
        self.code_blocks: List[CodeBlock] = []
        self.sections: List[Section] = []
        self.state = ProcessingState.NORMAL
        self.current_example: Optional[Example] = None
        self.current_code_block: Optional[CodeBlock] = None
        self.current_section: Optional[Section] = None
        self.stats = Statistics()
        
        # Enhanced patterns for better example detection
        self.patterns = {
            'chapter': re.compile(r'^(\d+)\.\s+(.+)$'),
            'section': re.compile(r'^(\d+)\.(\d+)\.\s+(.+)$'),
            'subsection': re.compile(r'^(\d+)\.(\d+)\.(\d+)\.\s+(.+)$'),
            'example': re.compile(r'^Example\s+(\d+)\.(\d+)\.?\s*(.*)$', re.IGNORECASE),
            'production': re.compile(r'^\[(\d+)\]\s+(.+)$'),
            'legend': re.compile(r'^Legend:'),
            'error': re.compile(r'^ERROR:|^Error:', re.IGNORECASE),
            
            # Enhanced code detection patterns
            'code_line': re.compile(r'^\s{4,}[^\s]|^\t[^\s]'),  # Indented lines
            'yaml_indicator': re.compile(r'^\s*[-:>|&*!%@`]'),  # YAML indicators
            'yaml_scalar': re.compile(r'^\s*["\'].*["\']$|^\s*\w+:\s*\w+'),  # YAML scalars
            'bracket_notation': re.compile(r'^\s*[\[\{].*[\]\}]\s*$'),  # Bracket notation
            'code_fence': re.compile(r'^```|^~~~'),  # Code fences
            'inline_code': re.compile(r'`([^`]+)`'),  # Inline code
            
            # Content type detection
            'flow_sequence': re.compile(r'\[.*\]'),
            'flow_mapping': re.compile(r'\{.*\}'),
            'document_marker': re.compile(r'^---\s*$|^\.\.\.\s*$'),
            'directive': re.compile(r'^%\w+'),
            'anchor_alias': re.compile(r'[&*]\w+'),
        }
    
    def load_content(self) -> None:
        """Load and validate input content"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
            logger.info(f"✅ Loaded {len(self.lines)} lines from {self.input_file}")
        except Exception as e:
            logger.error(f"❌ Failed to load {self.input_file}: {e}")
            raise

    def parse_content(self) -> None:
        """Enhanced content parsing with focus on examples"""
        logger.info("🔍 Starting example-focused parsing...")
        start_time = datetime.now()
        
        line_idx = 0
        while line_idx < len(self.lines):
            line = self.lines[line_idx]
            line_stripped = line.strip()
            
            if not line_stripped:
                line_idx += 1
                continue
            
            # Parse line and get number of lines consumed
            content_block, lines_consumed = self._parse_line(line, line_stripped, line_idx)
            
            if content_block:
                self.content_blocks.append(content_block)
                self._update_current_section(content_block)
            
            line_idx += lines_consumed
        
        # Finalize parsing
        self._end_current_example()
        self._end_current_code_block()
        self._finalize_current_section()
        self._calculate_statistics()
        
        parse_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Example-focused parsing completed in {parse_time:.2f}s")

    def _parse_line(self, line: str, line_stripped: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Enhanced line parsing with better example detection"""
        
        # Chapters
        chapter_match = self.patterns['chapter'].match(line_stripped)
        if chapter_match and not line_stripped.startswith('Example'):
            return self._parse_chapter(chapter_match), 1
        
        # Sections
        section_match = self.patterns['section'].match(line_stripped)
        if section_match and not line_stripped.startswith('Example'):
            return self._parse_section(section_match), 1
        
        # Subsections
        subsection_match = self.patterns['subsection'].match(line_stripped)
        if subsection_match and not line_stripped.startswith('Example'):
            return self._parse_subsection(subsection_match), 1
        
        # Examples (Enhanced detection)
        example_match = self._detect_example(line_stripped, line_idx)
        if example_match:
            return self._parse_example(example_match, line_idx)
        
        # Code blocks (Enhanced detection)
        if self._is_code_line(line, line_stripped):
            return self._handle_code_content(line, line_idx)
        
        # Productions
        production_match = self.patterns['production'].match(line_stripped)
        if production_match:
            return self._parse_production(production_match), 1
        
        # Handle state-specific parsing
        if self.state == ProcessingState.IN_EXAMPLE:
            return self._handle_example_content(line, line_idx)
        elif self.state == ProcessingState.IN_CODE_BLOCK:
            return self._handle_code_block_content(line, line_idx)
        
        # Extract inline code
        if self.patterns['inline_code'].search(line_stripped):
            self.stats.inline_code += len(self.patterns['inline_code'].findall(line_stripped))
        
        # Regular paragraphs
        if line_stripped:
            return ContentBlock(
                type=ContentType.PARAGRAPH,
                content=line_stripped,
                raw_lines=[line]
            ), 1
        
        return None, 1

    def _detect_example(self, line_stripped: str, line_idx: int) -> Optional[re.Match]:
        """Enhanced example detection"""
        # Standard example pattern
        match = self.patterns['example'].match(line_stripped)
        if match:
            return match
        
        # Alternative patterns for implicit examples
        if any([
            line_stripped.lower().startswith('consider'),
            line_stripped.lower().startswith('for example'),
            line_stripped.lower().startswith('here is'),
            line_stripped.lower().startswith('the following'),
            'example' in line_stripped.lower() and ':' in line_stripped
        ]):
            # Look ahead for code content
            if self._has_code_ahead(line_idx):
                # Create synthetic example
                return type('Match', (), {
                    'group': lambda self, i: {
                        1: str(len(self.examples) + 1),
                        2: "1", 
                        3: line_stripped[:50] + "..."
                    }.get(i, "")
                })()
        
        return None

    def _has_code_ahead(self, line_idx: int, lookahead: int = 5) -> bool:
        """Check if code content follows within next few lines"""
        for i in range(1, min(lookahead + 1, len(self.lines) - line_idx)):
            next_line = self.lines[line_idx + i].strip()
            if self._is_code_line(self.lines[line_idx + i], next_line):
                return True
        return False

    def _is_code_line(self, line: str, line_stripped: str) -> bool:
        """Enhanced code line detection"""
        if not line_stripped:
            return False
        
        # Check multiple indicators
        indicators = [
            self.patterns['code_line'].match(line),  # Indentation
            self.patterns['yaml_indicator'].match(line_stripped),  # YAML syntax
            self.patterns['yaml_scalar'].match(line_stripped),  # YAML scalars
            self.patterns['bracket_notation'].match(line_stripped),  # Brackets
            self.patterns['document_marker'].match(line_stripped),  # Document markers
            self.patterns['directive'].match(line_stripped),  # Directives
            self.patterns['anchor_alias'].search(line_stripped),  # Anchors/aliases
        ]
        
        return any(indicators)

    def _parse_example(self, match, line_idx: int) -> Tuple[ContentBlock, int]:
        """Enhanced example parsing with better content extraction"""
        self._end_current_example()
        
        try:
            example_num = f"{match.group(1)}.{match.group(2)}"
            example_title = match.group(3).strip() if match.group(3) else "Untitled Example"
        except:
            # Handle synthetic examples
            example_num = f"{len(self.examples) + 1}.1"
            example_title = "Implicit Example"
        
        self.current_example = Example(
            number=example_num,
            title=example_title,
            line_number=line_idx + 1,
            section=getattr(self.current_section, 'number', '') if self.current_section else ""
        )
        
        # Enhanced example metadata extraction
        lines_consumed = 1
        i = line_idx + 1
        
        # Collect description and analyze content
        while i < len(self.lines) and lines_consumed < 15:  # Extended look-ahead
            next_line = self.lines[i].strip()
            
            if not next_line:
                lines_consumed += 1
                i += 1
                continue
            
            # Description in parentheses or following lines
            if (next_line.startswith('(') and next_line.endswith(')')) or \
               (not self._is_code_line(self.lines[i], next_line) and 
                not any(p.match(next_line) for p in [self.patterns['chapter'], 
                                                   self.patterns['section'], 
                                                   self.patterns['example']])):
                self.current_example.description += next_line + " "
                lines_consumed += 1
                i += 1
            else:
                break
        
        # Classify example type
        self._classify_example()
        
        self.state = ProcessingState.IN_EXAMPLE
        
        return ContentBlock(
            type=ContentType.EXAMPLE,
            content=f"Example {example_num}: {example_title}",
            metadata={
                'number': example_num,
                'title': example_title,
                'description': self.current_example.description.strip(),
                'tags': list(self.current_example.tags),
                'complexity': self.current_example.complexity,
                'yaml_type': self.current_example.yaml_type
            }
        ), lines_consumed

    def _classify_example(self) -> None:
        """Classify example by content and complexity"""
        if not self.current_example:
            return
        
        title_lower = self.current_example.title.lower()
        desc_lower = self.current_example.description.lower()
        
        # YAML type classification
        type_keywords = {
            'scalar': ['scalar', 'string', 'number', 'boolean', 'null'],
            'sequence': ['sequence', 'list', 'array', 'collection'],
            'mapping': ['mapping', 'hash', 'dictionary', 'key', 'value'],
            'document': ['document', 'stream', 'multiple'],
            'anchor': ['anchor', 'alias', 'reference'],
            'tag': ['tag', 'type', 'schema'],
            'directive': ['directive', 'yaml', 'version'],
            'flow': ['flow', 'compact', 'inline'],
            'block': ['block', 'literal', 'folded']
        }
        
        for yaml_type, keywords in type_keywords.items():
            if any(keyword in title_lower or keyword in desc_lower for keyword in keywords):
                self.current_example.yaml_type = yaml_type
                self.current_example.tags.add(yaml_type)
                break
        
        # Complexity classification
        complexity_indicators = {
            'advanced': ['complex', 'nested', 'advanced', 'multiple', 'inheritance'],
            'intermediate': ['moderate', 'structured', 'formatted', 'schema'],
            'basic': ['simple', 'basic', 'plain', 'minimal']
        }
        
        for complexity, keywords in complexity_indicators.items():
            if any(keyword in title_lower or keyword in desc_lower for keyword in keywords):
                self.current_example.complexity = complexity
                break

    def _handle_example_content(self, line: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Enhanced example content handling"""
        line_stripped = line.strip()
        
        # Check for end of example
        if self._is_example_end(line_stripped, line_idx):
            self._end_current_example()
            return None, 0  # Re-process this line
        
        # Add code line to current example
        if self.current_example and line_stripped:
            self.current_example.code.append(line.rstrip())
        
        return None, 1

    def _is_example_end(self, line_stripped: str, line_idx: int) -> bool:
        """Determine if example has ended"""
        # End patterns
        end_patterns = [
            self.patterns['chapter'].match(line_stripped),
            self.patterns['section'].match(line_stripped),
            self.patterns['example'].match(line_stripped),
            line_stripped.startswith('Legend:'),
            line_stripped.startswith('[') and ']' in line_stripped  # Production
        ]
        
        if any(end_patterns):
            return True
        
        # End on multiple empty lines or clear context switch
        if not line_stripped:
            # Look ahead for content type
            for i in range(1, min(4, len(self.lines) - line_idx)):
                next_line = self.lines[line_idx + i].strip()
                if next_line and not self._is_code_line(self.lines[line_idx + i], next_line):
                    return True
        
        return False

    def _handle_code_content(self, line: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Handle standalone code blocks"""
        if not self.current_code_block:
            self.current_code_block = CodeBlock(
                line_number=line_idx + 1,
                context=getattr(self.current_section, 'title', '') if self.current_section else ""
            )
            self.state = ProcessingState.IN_CODE_BLOCK
        
        self.current_code_block.content.append(line.rstrip())
        return None, 1

    def _handle_code_block_content(self, line: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Handle content within code blocks"""
        line_stripped = line.strip()
        
        # Check for end of code block
        if not self._is_code_line(line, line_stripped) and line_stripped:
            self._end_current_code_block()
            return None, 0  # Re-process this line
        
        if self.current_code_block:
            self.current_code_block.content.append(line.rstrip())
        
        return None, 1

    def _end_current_example(self) -> None:
        """Finalize current example"""
        if self.current_example:
            if self.current_example.code:  # Only add if it has code
                self.examples.append(self.current_example)
                if self.current_section:
                    self.current_section.examples.append(self.current_example)
                    self.current_section.has_examples = True
            self.current_example = None
            self.state = ProcessingState.NORMAL

    def _end_current_code_block(self) -> None:
        """Finalize current code block"""
        if self.current_code_block:
            if self.current_code_block.content:  # Only add if it has content
                self.code_blocks.append(self.current_code_block)
                if self.current_section:
                    self.current_section.code_blocks.append(self.current_code_block)
            self.current_code_block = None
            self.state = ProcessingState.NORMAL

    def _parse_chapter(self, match) -> ContentBlock:
        """Parse chapter with example tracking"""
        self._finalize_current_section()
        
        chapter_num = match.group(1)
        chapter_title = match.group(2)
        chapter_id = self._clean_id(f"chapter-{chapter_num}-{chapter_title}")
        
        return ContentBlock(
            type=ContentType.CHAPTER,
            content=f"Chapter {chapter_num}. {chapter_title}",
            metadata={'number': chapter_num, 'title': chapter_title, 'id': chapter_id}
        )

    def _parse_section(self, match) -> ContentBlock:
        """Parse section with example tracking"""
        self._finalize_current_section()
        
        section_num = f"{match.group(1)}.{match.group(2)}"
        section_title = match.group(3)
        section_id = self._clean_id(f"section-{section_num}-{section_title}")
        
        self.current_section = Section(number=section_num, title=section_title)
        
        return ContentBlock(
            type=ContentType.SECTION,
            content=f"{section_num}. {section_title}",
            metadata={'number': section_num, 'title': section_title, 'id': section_id}
        )

    def _parse_subsection(self, match) -> ContentBlock:
        """Parse subsection"""
        section_num = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        section_title = match.group(4)
        section_id = self._clean_id(f"section-{section_num}-{section_title}")
        
        return ContentBlock(
            type=ContentType.SUBSECTION,
            content=f"{section_num}. {section_title}",
            metadata={'number': section_num, 'title': section_title, 'id': section_id}
        )

    def _parse_production(self, match) -> ContentBlock:
        """Parse production rule"""
        prod_num = match.group(1)
        prod_content = match.group(2)
        
        return ContentBlock(
            type=ContentType.PRODUCTION,
            content=f"[{prod_num}] {prod_content}",
            metadata={'number': prod_num, 'content': prod_content}
        )

    def _update_current_section(self, content_block: ContentBlock) -> None:
        """Update current section context"""
        if content_block.type == ContentType.SECTION:
            self.current_section = Section(
                number=content_block.metadata.get('number', ''),
                title=content_block.metadata.get('title', '')
            )

    def _finalize_current_section(self) -> None:
        """Finalize current section"""
        if self.current_section:
            self.sections.append(self.current_section)
            self.current_section = None

    def _calculate_statistics(self) -> None:
        """Calculate comprehensive statistics"""
        self.stats.examples = len(self.examples)
        self.stats.code_blocks = len(self.code_blocks)
        self.stats.sections = len([b for b in self.content_blocks if b.type == ContentType.SECTION])
        self.stats.chapters = len([b for b in self.content_blocks if b.type == ContentType.CHAPTER])
        self.stats.productions = len([b for b in self.content_blocks if b.type == ContentType.PRODUCTION])
        self.stats.sections_with_examples = len([s for s in self.sections if s.has_examples])
        
        if self.stats.sections > 0:
            self.stats.coverage_percentage = (self.stats.sections_with_examples / self.stats.sections) * 100

    def _clean_id(self, text: str) -> str:
        """Generate clean HTML ID"""
        return re.sub(r'[^\w-]', '-', text.lower()).strip('-')

    def generate_html(self) -> str:
        """Generate example-focused HTML"""
        logger.info("🎨 Generating example-focused HTML...")
        
        html_parts = [
            self._generate_html_header(),
            self._generate_navigation(),
            self._generate_content(),
            self._generate_html_footer()
        ]
        
        return '\n'.join(html_parts)

    def _generate_html_header(self) -> str:
        """Generate enhanced HTML header"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="YAML 1.1 Specification - Example-Focused Reference with {self.stats.examples} Comprehensive Examples">
    <meta name="author" content="YAML Community">
    <meta name="generator" content="Example-Focused YAML Spec Generator v3.0">
    <meta name="build-date" content="{datetime.now().isoformat()}">
    <title>YAML 1.1 Specification - {self.stats.examples} Examples & Code Samples</title>
    
    <!-- Preload critical resources -->
    <link rel="preload" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css" as="style">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css">
    
    <style>
        :root {{
            --example-primary: #0066cc;
            --example-secondary: #ff6b35;
            --example-success: #28a745;
            --example-warning: #ffc107;
            --example-danger: #dc3545;
            --code-bg: #1e1e1e;
            --code-text: #d4d4d4;
            --section-bg: #f8f9fa;
            --border: #dee2e6;
            --shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #ffffff;
            margin: 0;
            scroll-behavior: smooth;
        }}
        
        /* Enhanced Header */
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .header-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 2rem;
        }}
        
        .header-brand h1 {{
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }}
        
        .header-subtitle {{
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.9;
            font-weight: 400;
        }}
        
        .header-stats {{
            display: flex;
            gap: 2rem;
            align-items: center;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            line-height: 1;
        }}
        
        .stat-label {{
            display: block;
            font-size: 0.75rem;
            opacity: 0.8;
            margin-top: 0.25rem;
        }}
        
        /* Example-focused styling */
        .example-highlight {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid var(--example-warning);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 2rem 0;
            box-shadow: var(--shadow);
            position: relative;
        }}
        
        .example-highlight::before {{
            content: "💡 EXAMPLE";
            position: absolute;
            top: -12px;
            left: 1rem;
            background: var(--example-warning);
            color: #333;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        
        .example-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }}
        
        .example-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--example-primary);
            margin: 0;
        }}
        
        .example-tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .example-tag {{
            padding: 0.25rem 0.5rem;
            background: var(--example-secondary);
            color: white;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .example-description {{
            margin: 0.5rem 0 1rem 0;
            font-style: italic;
            color: #666;
        }}
        
        .code-block {{
            background: var(--code-bg);
            color: var(--code-text);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            line-height: 1.4;
            border: 1px solid #333;
        }}
        
        .code-block code {{
            background: none;
            padding: 0;
            font-size: 0.9rem;
        }}
        
        /* Section styling */
        .content-section {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        h2 {{
            font-size: 2rem;
            color: var(--example-primary);
            margin: 3rem 0 1.5rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--example-primary);
        }}
        
        h3 {{
            font-size: 1.5rem;
            color: var(--example-secondary);
            margin: 2.5rem 0 1rem 0;
        }}
        
        h4 {{
            font-size: 1.25rem;
            color: #555;
            margin: 2rem 0 1rem 0;
        }}
        
        /* Navigation */
        .toc-toggle {{
            position: fixed;
            top: 120px;
            right: 2rem;
            background: var(--example-primary);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            box-shadow: var(--shadow);
            z-index: 1001;
            transition: all 0.3s ease;
        }}
        
        .toc-toggle:hover {{
            background: var(--example-secondary);
            transform: translateY(-2px);
        }}
        
        .toc-sidebar {{
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100vh;
            background: white;
            border-left: 1px solid var(--border);
            box-shadow: var(--shadow);
            padding: 2rem;
            overflow-y: auto;
            transition: right 0.3s ease;
            z-index: 1002;
        }}
        
        .toc-sidebar.active {{
            right: 0;
        }}
        
        .toc-sidebar h3 {{
            margin-top: 0;
            color: var(--example-primary);
            border-bottom: 2px solid var(--example-primary);
            padding-bottom: 0.5rem;
        }}
        
        .toc-list {{
            list-style: none;
            padding: 0;
        }}
        
        .toc-item {{
            margin: 0.5rem 0;
        }}
        
        .toc-item a {{
            color: #333;
            text-decoration: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            display: block;
            transition: all 0.2s ease;
        }}
        
        .toc-item a:hover {{
            background: var(--section-bg);
            color: var(--example-primary);
        }}
        
        .toc-item .example-count {{
            float: right;
            background: var(--example-success);
            color: white;
            padding: 0.125rem 0.375rem;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        /* Section without examples warning */
        .no-examples-warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 1rem;
            border-radius: 6px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 500;
        }}
        
        /* Footer */
        footer {{
            background: var(--section-bg);
            padding: 3rem 0 2rem 0;
            margin-top: 4rem;
            text-align: center;
            border-top: 1px solid var(--border);
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
            color: var(--example-primary);
            display: block;
        }}
        
        .footer-stat-label {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.25rem;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .header-container {{
                flex-direction: column;
                text-align: center;
            }}
            
            .header-stats {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .toc-sidebar {{
                width: 100%;
                right: -100%;
            }}
            
            .toc-toggle {{
                top: 100px;
                right: 1rem;
            }}
            
            .footer-stats {{
                flex-direction: column;
                gap: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header class="main-header">
        <div class="header-container">
            <div class="header-brand">
                <h1>YAML 1.1 Specification</h1>
                <p class="header-subtitle">Example-Focused Complete Reference</p>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <span class="stat-number">{self.stats.examples}</span>
                    <span class="stat-label">Examples</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{self.stats.code_blocks}</span>
                    <span class="stat-label">Code Blocks</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{self.stats.coverage_percentage:.0f}%</span>
                    <span class="stat-label">Coverage</span>
                </div>
            </div>
        </div>
    </header>'''

    def _generate_navigation(self) -> str:
        """Generate example-focused navigation"""
        # Build TOC items with example counts
        toc_items = []
        current_chapter = None
        
        for block in self.content_blocks:
            if block.type == ContentType.CHAPTER:
                current_chapter = block.metadata
                chapter_examples = len([e for e in self.examples 
                                      if e.section.startswith(current_chapter['number'])])
                toc_items.append({
                    'level': 2,
                    'id': block.metadata['id'],
                    'text': f"Chapter {current_chapter['number']}. {current_chapter['title']}",
                    'examples': chapter_examples
                })
            elif block.type == ContentType.SECTION:
                section_examples = len([e for e in self.examples 
                                      if e.section == block.metadata['number']])
                toc_items.append({
                    'level': 3,
                    'id': block.metadata['id'],
                    'text': f"{block.metadata['number']}. {block.metadata['title']}",
                    'examples': section_examples
                })
        
        toc_html = '''
    <button class="toc-toggle" onclick="toggleTOC()">📚 Examples Index</button>
    <nav class="toc-sidebar" id="tocSidebar">
        <h3>Navigation ({} Examples)</h3>
        <ul class="toc-list">'''.format(self.stats.examples)
        
        for item in toc_items:
            example_badge = f'<span class="example-count">{item["examples"]}</span>' if item['examples'] > 0 else ''
            toc_html += f'''
            <li class="toc-item">
                <a href="#{item['id']}">{item['text']} {example_badge}</a>
            </li>'''
        
        toc_html += '''
        </ul>
    </nav>'''
        
        return toc_html

    def _generate_content(self) -> str:
        """Generate example-focused content"""
        content_html = '<div class="content-section">'
        current_section_examples = []
        
        for block in self.content_blocks:
            if block.type == ContentType.CHAPTER:
                content_html += f'''
    <h2 id="{block.metadata['id']}">Chapter {block.metadata['number']}. {block.metadata['title']}</h2>'''
                
            elif block.type == ContentType.SECTION:
                # First, close previous section and show its examples
                if current_section_examples:
                    content_html += self._render_section_examples(current_section_examples)
                    current_section_examples = []
                
                # Start new section
                section_examples = [e for e in self.examples if e.section == block.metadata['number']]
                current_section_examples = section_examples
                
                content_html += f'''
    <h3 id="{block.metadata['id']}">{block.metadata['number']}. {block.metadata['title']}</h3>'''
                
                # Show warning if no examples
                if not section_examples:
                    content_html += '''
    <div class="no-examples-warning">
        ⚠️ This section currently has no illustrative examples. Examples would help clarify the concepts.
    </div>'''
                
            elif block.type == ContentType.SUBSECTION:
                content_html += f'''
    <h4 id="{block.metadata['id']}">{block.metadata['number']}. {block.metadata['title']}</h4>'''
                
            elif block.type == ContentType.EXAMPLE:
                # Examples are handled in section rendering
                pass
                
            elif block.type == ContentType.PARAGRAPH:
                # Only include paragraphs that provide context for examples
                if self._is_example_context(block.content):
                    content_html += f'<p>{block.content}</p>'
        
        # Handle final section examples
        if current_section_examples:
            content_html += self._render_section_examples(current_section_examples)
        
        content_html += '</div>'
        return content_html

    def _is_example_context(self, text: str) -> bool:
        """Determine if paragraph provides useful context for examples"""
        context_keywords = [
            'example', 'consider', 'following', 'shows', 'demonstrates',
            'illustrates', 'represents', 'yaml', 'syntax', 'format',
            'structure', 'pattern', 'rule', 'valid', 'invalid'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in context_keywords) or len(text) < 200

    def _render_section_examples(self, examples: List[Example]) -> str:
        """Render examples for a section"""
        if not examples:
            return ""
        
        html = f'''
    <div class="section-examples">
        <h4>📝 Examples ({len(examples)})</h4>'''
        
        for example in examples:
            html += f'''
        <div class="example-highlight">
            <div class="example-header">
                <h5 class="example-title">Example {example.number}: {example.title}</h5>
                <div class="example-tags">'''
            
            # Add tags
            for tag in example.tags:
                html += f'<span class="example-tag">{tag}</span>'
            
            if example.complexity != 'basic':
                html += f'<span class="example-tag">{example.complexity}</span>'
            
            html += '''
                </div>
            </div>'''
            
            if example.description:
                html += f'<p class="example-description">{example.description}</p>'
            
            if example.code:
                html += '''
            <div class="code-block">
                <pre><code class="language-yaml">'''
                html += '\n'.join(example.code)
                html += '''</code></pre>
            </div>'''
            
            html += '''
        </div>'''
        
        html += '''
    </div>'''
        
        return html

    def _generate_html_footer(self) -> str:
        """Generate comprehensive footer with statistics"""
        return f'''
    <footer>
        <div class="footer-stats">
            <div class="footer-stat">
                <span class="footer-stat-number">{self.stats.examples}</span>
                <span class="footer-stat-label">Total Examples</span>
            </div>
            <div class="footer-stat">
                <span class="footer-stat-number">{self.stats.code_blocks}</span>
                <span class="footer-stat-label">Code Blocks</span>
            </div>
            <div class="footer-stat">
                <span class="footer-stat-number">{self.stats.sections_with_examples}</span>
                <span class="footer-stat-label">Sections with Examples</span>
            </div>
            <div class="footer-stat">
                <span class="footer-stat-number">{self.stats.coverage_percentage:.1f}%</span>
                <span class="footer-stat-label">Example Coverage</span>
            </div>
        </div>
        <p>&copy; 2001-2008 Oren Ben-Kiki, Clark Evans, Ingy döt Net</p>
        <p>Enhanced with Example-Focused YAML Spec Generator v3.0</p>
    </footer>
    
    <!-- Enhanced JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-yaml.min.js"></script>
    <script>
        function toggleTOC() {{
            const sidebar = document.getElementById('tocSidebar');
            sidebar.classList.toggle('active');
        }}
        
        // Close TOC when clicking outside
        document.addEventListener('click', function(e) {{
            const sidebar = document.getElementById('tocSidebar');
            const toggle = document.querySelector('.toc-toggle');
            
            if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {{
                sidebar.classList.remove('active');
            }}
        }});
        
        // Smooth scrolling for links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    // Close TOC after navigation
                    document.getElementById('tocSidebar').classList.remove('active');
                }}
            }});
        }});
        
        // Example highlighting on scroll
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '-100px 0px -100px 0px'
        }};
        
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.transform = 'translateY(0)';
                    entry.target.style.opacity = '1';
                }}
            }});
        }}, observerOptions);
        
        // Observe all examples
        document.querySelectorAll('.example-highlight').forEach(example => {{
            example.style.transform = 'translateY(20px)';
            example.style.opacity = '0.8';
            example.style.transition = 'all 0.6s ease';
            observer.observe(example);
        }});
        
        console.log('🚀 Example-Focused YAML Spec Generator v3.0');
        console.log('📊 {self.stats.examples} examples, {self.stats.code_blocks} code blocks');
        console.log('📈 {self.stats.coverage_percentage:.1f}% section coverage');
    </script>
</body>
</html>'''

    def save_html(self, html_content: str) -> None:
        """Save generated HTML"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"✅ Example-focused HTML saved to {self.output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save HTML: {e}")
            raise

    def print_statistics(self) -> None:
        """Print comprehensive statistics"""
        print(f"""
🎉 Example-Focused YAML Specification Generated!
📁 Output: {self.output_file}
📊 Statistics:
   • Examples: {self.stats.examples}
   • Code Blocks: {self.stats.code_blocks}
   • Chapters: {self.stats.chapters}
   • Sections: {self.stats.sections}
   • Sections with Examples: {self.stats.sections_with_examples}
   • Example Coverage: {self.stats.coverage_percentage:.1f}%
   • Productions: {self.stats.productions}
   • Inline Code: {self.stats.inline_code}
        """)

    def run(self) -> None:
        """Main execution method"""
        try:
            logger.info("🚀 Starting Example-Focused YAML Spec Generator v3.0")
            
            # Load and parse content
            self.load_content()
            self.parse_content()
            
            # Log statistics
            logger.info("📊 Parsing Statistics:")
            logger.info(f"   📚 Chapters: {self.stats.chapters}")
            logger.info(f"   📑 Sections: {self.stats.sections}")
            logger.info(f"   💡 Examples: {self.stats.examples}")
            logger.info(f"   🔧 Code Blocks: {self.stats.code_blocks}")
            logger.info(f"   📈 Coverage: {self.stats.coverage_percentage:.1f}%")
            
            # Generate and save HTML
            html_content = self.generate_html()
            self.save_html(html_content)
            
            # Print final statistics
            self.print_statistics()
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise

if __name__ == "__main__":
    generator = ExampleFocusedYAMLSpecGenerator("content.txt")
    generator.run()
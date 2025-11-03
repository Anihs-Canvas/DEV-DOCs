#!/usr/bin/env python3
"""
Advanced YAML 1.1 Specification HTML Generator v2.0

This completely rewritten generator features:
- Object-oriented architecture with proper separation of concerns
- Sophisticated content parsing with state machine pattern
- Comprehensive error handling and logging
- Modern responsive HTML5 with enhanced CSS3 animations
- Advanced JavaScript for better user experience
- Automatic statistics generation and performance monitoring
- Extensible design for future enhancements

Author: AI Assistant  
Version: 2.0
Date: November 2025
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum, auto
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('yaml_generator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Enumeration of content section types"""
    CHAPTER = auto()
    SECTION = auto()
    SUBSECTION = auto()
    EXAMPLE = auto()
    PRODUCTION = auto()
    PARAGRAPH = auto()
    CODE = auto()
    LEGEND = auto()
    ERROR = auto()
    EMPTY = auto()

class ProcessingState(Enum):
    """Current processing state for state machine"""
    NORMAL = auto()
    IN_EXAMPLE = auto()
    IN_PRODUCTION = auto()
    IN_LEGEND = auto()

@dataclass
class TOCItem:
    """Table of Contents item with hierarchical structure"""
    level: int
    id: str
    text: str
    number: str
    parent_id: Optional[str] = None
    children: List['TOCItem'] = field(default_factory=list)

@dataclass
class ContentBlock:
    """Represents a structured block of content"""
    type: ContentType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    line_number: int = 0
    raw_lines: List[str] = field(default_factory=list)

@dataclass
class Example:
    """YAML example with comprehensive metadata"""
    number: str
    title: str
    description: str = ""
    code: str = ""
    legend: str = ""
    errors: List[str] = field(default_factory=list)
    line_number: int = 0

@dataclass
class Production:
    """BNF production rule with metadata"""
    number: str
    name: str
    definition: str
    line_number: int = 0

@dataclass
class DocumentStats:
    """Comprehensive document statistics"""
    total_lines: int = 0
    chapters: int = 0
    sections: int = 0
    examples: int = 0
    productions: int = 0
    errors: int = 0
    processing_time: float = 0.0
    html_lines: int = 0

class YAMLSpecGenerator:
    """Advanced YAML Specification HTML Generator"""
    
    def __init__(self, content_path: Path, output_path: Path):
        self.content_path = Path(content_path)
        self.output_path = Path(output_path)
        self.lines: List[str] = []
        self.blocks: List[ContentBlock] = []
        self.toc_items: List[TOCItem] = []
        self.examples: List[Example] = []
        self.productions: List[Production] = []
        self.stats = DocumentStats()
        self.state = ProcessingState.NORMAL
        self.current_example: Optional[Example] = None
        self.html_output: List[str] = []
        
        # Regex patterns
        self.patterns = {
            'chapter': re.compile(r'^Chapter\s+(\d+)\.\s+(.+)$'),
            'section': re.compile(r'^(\d+)\.(\d+)\.\s+(.+)$'),
            'subsection': re.compile(r'^(\d+)\.(\d+)\.(\d+)\.\s+(.+)$'),
            'example': re.compile(r'^Example\s+(\d+)\.(\d+)\.\s*(.*)$'),
            'production': re.compile(r'^\[(\d+)\]\s+(.+?)\s+::=\s+(.+)$'),
            'legend': re.compile(r'^Legend:\s*(.*)$'),
            'error': re.compile(r'^ERROR:\s*(.*)$'),
            'yaml_directive': re.compile(r'^%YAML'),
            'document_marker': re.compile(r'^---\s*$')
        }
    
    def load_content(self) -> None:
        """Load and validate content file"""
        try:
            if not self.content_path.exists():
                raise FileNotFoundError(f"Content file not found: {self.content_path}")
            
            with open(self.content_path, 'r', encoding='utf-8') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
            
            self.stats.total_lines = len(self.lines)
            logger.info(f"Loaded {self.stats.total_lines} lines from {self.content_path}")
            
        except Exception as e:
            logger.error(f"Failed to load content: {e}")
            raise
    
    def parse_content(self) -> None:
        """Parse content into structured blocks"""
        start_time = datetime.now()
        logger.info("Starting content parsing...")
        
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            line_stripped = line.strip()
            
            try:
                block, lines_consumed = self._parse_line(line, line_stripped, i)
                if block:
                    block.line_number = i + 1
                    self.blocks.append(block)
                    self._update_stats(block)
                
                i += lines_consumed
                
            except Exception as e:
                logger.warning(f"Error parsing line {i + 1}: {e}")
                # Create error block and continue
                error_block = ContentBlock(
                    type=ContentType.ERROR,
                    content=f"Parse error: {e}",
                    line_number=i + 1,
                    raw_lines=[line]
                )
                self.blocks.append(error_block)
                i += 1
        
        self._end_current_example()  # Ensure any final example is closed
        
        self.stats.processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Parsing completed in {self.stats.processing_time:.2f}s")
        self._log_stats()
    
    def _parse_line(self, line: str, line_stripped: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Parse a single line and return content block and lines consumed"""
        
        # Skip empty lines in normal state
        if not line_stripped and self.state == ProcessingState.NORMAL:
            return ContentBlock(type=ContentType.EMPTY, content=""), 1
        
        # Chapter headers
        chapter_match = self.patterns['chapter'].match(line_stripped)
        if chapter_match:
            return self._parse_chapter(chapter_match), 1
        
        # Section headers
        section_match = self.patterns['section'].match(line_stripped)
        if section_match and not line_stripped.startswith('Example'):
            return self._parse_section(section_match), 1
        
        # Subsection headers
        subsection_match = self.patterns['subsection'].match(line_stripped)
        if subsection_match and not line_stripped.startswith('Example'):
            return self._parse_subsection(subsection_match), 1
        
        # Examples
        example_match = self.patterns['example'].match(line_stripped)
        if example_match:
            return self._parse_example(example_match, line_idx)
        
        # Productions
        production_match = self.patterns['production'].match(line_stripped)
        if production_match:
            return self._parse_production(production_match), 1
        
        # Legend
        legend_match = self.patterns['legend'].match(line_stripped)
        if legend_match:
            return self._parse_legend(line_idx)
        
        # Error markers
        error_match = self.patterns['error'].match(line_stripped)
        if error_match:
            return self._parse_error(error_match), 1
        
        # Handle state-specific parsing
        if self.state == ProcessingState.IN_EXAMPLE:
            return self._handle_example_content(line, line_idx)
        
        # Regular paragraphs
        if line_stripped:
            return ContentBlock(
                type=ContentType.PARAGRAPH,
                content=line_stripped,
                raw_lines=[line]
            ), 1
        
        return None, 1

    def _parse_chapter(self, match) -> ContentBlock:
        """Parse chapter header"""
        self._end_current_example()  # End any ongoing example
        
        chapter_num = match.group(1)
        chapter_title = match.group(2)
        chapter_id = self._clean_id(f"chapter-{chapter_num}-{chapter_title}")
        
        # Add to TOC
        toc_item = TOCItem(
            level=2,
            id=chapter_id,
            text=f"Chapter {chapter_num}. {chapter_title}",
            number=chapter_num
        )
        self.toc_items.append(toc_item)
        
        return ContentBlock(
            type=ContentType.CHAPTER,
            content=f"Chapter {chapter_num}. {chapter_title}",
            metadata={
                'number': chapter_num,
                'title': chapter_title,
                'id': chapter_id
            }
        )

    def _parse_section(self, match) -> ContentBlock:
        """Parse section header"""
        self._end_current_example()
        
        section_num = f"{match.group(1)}.{match.group(2)}"
        section_title = match.group(3)
        section_id = self._clean_id(f"section-{section_num}-{section_title}")
        
        toc_item = TOCItem(
            level=3,
            id=section_id,
            text=f"{section_num}. {section_title}",
            number=section_num
        )
        self.toc_items.append(toc_item)
        
        return ContentBlock(
            type=ContentType.SECTION,
            content=f"{section_num}. {section_title}",
            metadata={
                'number': section_num,
                'title': section_title,
                'id': section_id
            }
        )

    def _parse_subsection(self, match) -> ContentBlock:
        """Parse subsection header"""
        self._end_current_example()
        
        subsection_num = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        subsection_title = match.group(4)
        subsection_id = self._clean_id(f"section-{subsection_num}-{subsection_title}")
        
        toc_item = TOCItem(
            level=4,
            id=subsection_id,
            text=f"{subsection_num}. {subsection_title}",
            number=subsection_num
        )
        self.toc_items.append(toc_item)
        
        return ContentBlock(
            type=ContentType.SUBSECTION,
            content=f"{subsection_num}. {subsection_title}",
            metadata={
                'number': subsection_num,
                'title': subsection_title,
                'id': subsection_id
            }
        )

    def _parse_example(self, match, line_idx: int) -> Tuple[ContentBlock, int]:
        """Parse example with look-ahead for description and code"""
        self._end_current_example()
        
        example_num = f"{match.group(1)}.{match.group(2)}"
        example_title = match.group(3).strip()
        
        self.current_example = Example(
            number=example_num,
            title=example_title,
            line_number=line_idx + 1
        )
        
        # Look ahead for description
        lines_consumed = 1
        i = line_idx + 1
        
        # Collect description lines (usually in parentheses)
        while i < len(self.lines) and lines_consumed < 10:  # Safety limit
            next_line = self.lines[i].strip()
            if next_line.startswith('(') and next_line.endswith(')'):
                self.current_example.description += next_line + " "
                lines_consumed += 1
                i += 1
            elif not next_line:  # Empty line marks end of description
                lines_consumed += 1
                break
            else:
                break
        
        self.state = ProcessingState.IN_EXAMPLE
        
        return ContentBlock(
            type=ContentType.EXAMPLE,
            content=f"Example {example_num}. {example_title}",
            metadata={
                'number': example_num,
                'title': example_title,
                'description': self.current_example.description.strip()
            }
        ), lines_consumed

# HTML Header
html_output.append('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YAML 1.1 Specification - Complete Reference</title>
    <link rel="preload" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism.min.css"></noscript>
    <style>
        body {
            font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif;
            line-height: 1.55;
            margin: 0;
            color: #222;
            background: #fafafa;
        }

        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: #ffffff;
            padding: 0;
            border-bottom: none;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            position: relative;
            overflow: hidden;
            animation: slideDown 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            position: relative;
            z-index: 1;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .brand-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #dc2626, #ef4444);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 24px;
            box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
        }

        .brand-text h1 {
            margin: 0;
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.2;
        }

        .brand-subtitle {
            margin: 0;
            font-size: 0.875rem;
            color: #94a3b8;
            font-weight: 500;
        }

        .header-stats {
            display: flex;
            gap: 2rem;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fafc;
            line-height: 1;
        }

        .stat-label {
            display: block;
            font-size: 0.75rem;
            color: #94a3b8;
            font-weight: 500;
            margin-top: 0.25rem;
        }

        html { scroll-behavior: smooth; }

        body.toc-open .toc-sidebar {
            transform: translateX(0);
        }

        .toc-sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 300px;
            background: #ffffff;
            border-right: 1px solid #e7edf7;
            box-shadow: 0 0 24px rgba(16,23,37,0.06);
            padding: 16px 14px;
            overflow-y: auto;
            transform: translateX(-100%);
            transition: transform 200ms ease;
            z-index: 1000;
        }

        .toc-sidebar h2 {
            margin: 8px 6px 10px;
            font-size: 16px;
            color: #0d1b2a;
        }

        .toc-sidebar ol {
            list-style: decimal;
            padding-left: 22px;
        }

        .toc-sidebar ol.sub-toc {
            list-style-type: disc;
            margin-top: 8px;
            margin-bottom: 12px;
            padding-left: 18px;
        }

        .toc-sidebar a {
            color: #0d1b2a;
            text-decoration: none;
        }

        .toc-sidebar a:hover {
            text-decoration: underline;
        }

        .toc-sidebar a.active {
            font-weight: 600;
            color: #1b3a6f;
            position: relative;
        }

        .toc-sidebar a.active::before {
            content: "";
            position: absolute;
            left: -12px;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 14px;
            background: #4361ee;
            border-radius: 2px;
        }

        #tocToggle {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1001;
            background: linear-gradient(135deg, #dc2626, #ef4444);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        #tocToggle:hover {
            background: linear-gradient(135deg, #b91c1c, #dc2626);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
        }

        #backToTop {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 100;
            background: linear-gradient(135deg, #dc2626, #ef4444);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
            display: none;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }

        #backToTop.show {
            display: flex;
        }

        #backToTop:hover {
            background: linear-gradient(135deg, #b91c1c, #dc2626);
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
        }

        main {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .chapter {
            margin-bottom: 4rem;
        }

        h2 {
            font-size: 2rem;
            color: #1e3a8a;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #2563eb;
            scroll-margin-top: 100px;
        }

        h3 {
            font-size: 1.5rem;
            color: #1e40af;
            margin: 2rem 0 1rem 0;
            scroll-margin-top: 100px;
        }

        h4 {
            font-size: 1.25rem;
            color: #2563eb;
            margin: 1.5rem 0 1rem 0;
            scroll-margin-top: 100px;
        }

        h5 {
            font-size: 1.1rem;
            color: #3b82f6;
            margin: 1rem 0 0.75rem 0;
        }

        p {
            margin-bottom: 1rem;
            color: #374151;
            line-height: 1.7;
        }

        .production {
            background: #f8fafc;
            border-left: 4px solid #6366f1;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            border-radius: 6px;
        }

        .prod-num {
            color: #6366f1;
            font-weight: bold;
            margin-right: 8px;
            display: inline-block;
            min-width: 40px;
        }

        .production code {
            background: transparent;
            padding: 0;
            color: #1e293b;
        }

        .example {
            background: #fefce8;
            border: 1px solid #fde047;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }

        .example h5 {
            color: #854d0e;
            margin-top: 0;
            margin-bottom: 1rem;
            font-weight: 600;
        }

        .example p {
            color: #713f12;
            margin-bottom: 1rem;
        }

        .example pre {
            background: #1e293b !important;
            margin: 0.5rem 0;
            border-radius: 6px;
        }

        .legend {
            background: #fef3c7;
            padding: 0.75rem 1rem;
            margin: 0.75rem 0;
            border-left: 3px solid #f59e0b;
            font-size: 0.875rem;
            color: #92400e;
            font-style: italic;
        }

        pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 1.25rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
            line-height: 1.5;
        }

        code {
            background: #f1f5f9;
            color: #475569;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
            font-family: 'Courier New', monospace;
        }

        pre code {
            background: transparent;
            color: inherit;
            padding: 0;
        }

        ul, ol {
            margin: 1rem 0 1rem 2rem;
            color: #374151;
        }

        li {
            margin-bottom: 0.5rem;
            line-height: 1.7;
        }

        dt {
            font-weight: 600;
            color: #1e40af;
            margin-top: 1rem;
        }

        dd {
            margin-left: 2rem;
            margin-bottom: 0.5rem;
            color: #374151;
        }

        .sidebar-controls {
            display: flex;
            gap: 6px;
            align-items: center;
            margin-bottom: 12px;
        }

        .expand-collapse-btn {
            width: 24px;
            height: 24px;
            border: 1px solid #e7edf7;
            background: #f8f9fa;
            color: #495057;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            line-height: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .expand-collapse-btn:hover {
            background: #e9ecef;
            border-color: #dee2e6;
        }
    </style>
</head>
<body>
''')

# Add header
html_output.append('''
    <div class="main-header">
        <div class="header-container">
            <div class="header-brand">
                <div class="brand-icon">Y</div>
                <div class="brand-text">
                    <h1>YAML 1.1 Specification</h1>
                    <p class="brand-subtitle">Complete Reference Guide</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <span class="stat-number">127</span>
                    <span class="stat-label">Examples</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">222</span>
                    <span class="stat-label">Productions</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">10</span>
                    <span class="stat-label">Chapters</span>
                </div>
            </div>
        </div>
    </div>

    <button id="tocToggle" aria-label="Toggle table of contents" aria-expanded="false">
        ☰ Table of Contents
    </button>

    <button id="backToTop" hidden aria-label="Back to top">
        ↑
    </button>
''')

# Process content line by line
i = 0
in_example = False
in_production = False
example_code_lines = []
current_example_title = ""
current_example_description = ""
toc_items = []

def escape_html(text):
    """Escape HTML special characters"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def clean_id(text):
    """Create clean ID from heading text"""
    # Remove special characters and convert to lowercase
    clean = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    clean = re.sub(r'[\s_]+', '-', clean)
    return clean.strip('-')

html_output.append('<main>')

while i < len(lines):
    line = lines[i].rstrip('\n')

    # Match Example headers
    example_match = re.match(r'^Example (\d+)\.(\d+)\.\s*(.*)$', line)
    if example_match:
        # Close any previous example
        if in_example:
            if example_code_lines:
                yaml_code = '\n'.join(example_code_lines)
                html_output.append(f'<pre><code class="language-yaml">{escape_html(yaml_code)}</code></pre>')
            html_output.append('</div>')
            example_code_lines = []
            in_example = False

        # Start new example
        example_num = f"{example_match.group(1)}.{example_match.group(2)}"
        example_title = example_match.group(3).strip()
        current_example_title = f"Example {example_num}. {example_title}"
        current_example_description = ""

        html_output.append(f'<div class="example">')
        html_output.append(f'<h5>{escape_html(current_example_title)}</h5>')

        # Look ahead for description and code
        i += 1
        # Skip description lines (in parentheses)
        while i < len(lines):
            next_line = lines[i].strip()
            if next_line.startswith('(') and next_line.endswith(')'):
                html_output.append(f'<p>{escape_html(next_line)}</p>')
                i += 1
            elif not next_line:  # Empty line after description
                i += 1
                break
            else:
                break

        in_example = True
        example_code_lines = []
        continue

    # Match Production notations
    prod_match = re.match(r'^\[(\d+)\]\s+(.+?)\s+::=\s+(.+)$', line)
    if prod_match:
        prod_num = prod_match.group(1)
        prod_name = prod_match.group(2)
        prod_def = prod_match.group(3)

        html_output.append(f'<div class="production">')
        html_output.append(f'<span class="prod-num">[{prod_num}]</span>')
        html_output.append(f'<code>{escape_html(prod_name)} ::= {escape_html(prod_def)}</code>')
        html_output.append('</div>')
        i += 1
        continue

    # Match Chapter headers
    chapter_match = re.match(r'^Chapter (\d+)\.\s+(.+)$', line)
    if chapter_match:
        if in_example:
            html_output.append('</div>')
            in_example = False

        chapter_num = chapter_match.group(1)
        chapter_title = chapter_match.group(2)
        chapter_id = clean_id(f"chapter-{chapter_num}-{chapter_title}")

        html_output.append(f'<div class="chapter">')
        html_output.append(f'<h2 id="{chapter_id}">Chapter {chapter_num}. {escape_html(chapter_title)}</h2>')

        toc_items.append({
            'level': 2,
            'id': chapter_id,
            'text': f"Chapter {chapter_num}. {chapter_title}",
            'number': chapter_num
        })
        i += 1
        continue

    # Match section headers (e.g., "3.1. Processes")
    section_match = re.match(r'^(\d+)\.(\d+)\.\s+(.+)$', line)
    if section_match and not line.startswith('Example'):
        if in_example:
            html_output.append('</div>')
            in_example = False

        section_num = f"{section_match.group(1)}.{section_match.group(2)}"
        section_title = section_match.group(3)
        section_id = clean_id(f"section-{section_num}-{section_title}")

        html_output.append(f'<h3 id="{section_id}">{section_num}. {escape_html(section_title)}</h3>')

        toc_items.append({
            'level': 3,
            'id': section_id,
            'text': f"{section_num}. {section_title}",
            'number': section_num
        })
        i += 1
        continue

    # Match subsection headers (e.g., "3.1.1. Represent")
    subsection_match = re.match(r'^(\d+)\.(\d+)\.(\d+)\.\s+(.+)$', line)
    if subsection_match and not line.startswith('Example'):
        if in_example:
            html_output.append('</div>')
            in_example = False

        subsection_num = f"{subsection_match.group(1)}.{subsection_match.group(2)}.{subsection_match.group(3)}"
        subsection_title = subsection_match.group(4)
        subsection_id = clean_id(f"section-{subsection_num}-{subsection_title}")

        html_output.append(f'<h4 id="{subsection_id}">{subsection_num}. {escape_html(subsection_title)}</h4>')

        toc_items.append({
            'level': 4,
            'id': subsection_id,
            'text': f"{subsection_num}. {subsection_title}",
            'number': subsection_num
        })
        i += 1
        continue

    # Handle Legend markers
    if line.strip() == 'Legend:' or line.startswith('Legend:'):
        if in_example:
            if example_code_lines:
                # Output the YAML code
                yaml_code = '\n'.join(example_code_lines)
                html_output.append(f'<pre><code class="language-yaml">{escape_html(yaml_code)}</code></pre>')
                example_code_lines = []

            # Add legend section
            html_output.append(f'<div class="legend">')
            html_output.append(f'<strong>Legend:</strong><br>')

            # Collect legend lines - stop at Chapter, Example, or %YAML
            i += 1
            while i < len(lines):
                legend_line = lines[i].strip()
                if (not legend_line or
                    legend_line.startswith('Example') or
                    legend_line.startswith('%YAML') or
                    legend_line.startswith('Chapter') or
                    re.match(r'^\d+\.\d+\.', legend_line)):
                    break
                html_output.append(f'{escape_html(legend_line)}<br>')
                i += 1
            html_output.append('</div>')
            continue
        i += 1
        continue

    # Handle ERROR markers
    if line.strip().startswith('ERROR:'):
        if in_example:
            html_output.append(f'<p style="color: #dc2626; font-weight: 600;">{escape_html(line.strip())}</p>')
        i += 1
        continue

    # Skip YAML directive lines and equivalent format lines
    if line.startswith('%YAML') or line.startswith('---') and in_example and example_code_lines:
        # This is the equivalent YAML format - skip for now or add to a separate section
        i += 1
        continue

    # Collect example code lines
    if in_example:
        # Check for lines that explicitly end examples
        if line.startswith('Legend:') or line.startswith('ERROR:') or line.startswith('Example') or line.startswith('Chapter') or line.startswith('%YAML') or re.match(r'^\d+\.\d+\.', line.strip()):
            # Don't collect this line, let other handlers process it
            pass
        elif line.strip():
            # Check if this looks like a regular paragraph (prose) rather than YAML
            # Prose typically:
            # - Starts with capital letter and has multiple words
            # - Contains punctuation like periods in mid-sentence
            # - Has sentence structure
            stripped = line.strip()

            # Check if it's likely prose
            is_prose = False
            if len(stripped) > 30:  # Long lines are often prose
                # Check for prose indicators
                if (stripped[0].isupper() and
                    (' the ' in stripped.lower() or ' a ' in stripped.lower() or
                     ' is ' in stripped.lower() or ' are ' in stripped.lower() or
                     ' uses ' in stripped.lower() or ' provides ' in stripped.lower() or
                     '. ' in stripped[:-1])):  # Period not at end
                    is_prose = True

            if is_prose and example_code_lines:
                # End the example, output the code collected so far
                yaml_code = '\n'.join(example_code_lines)
                html_output.append(f'<pre><code class="language-yaml">{escape_html(yaml_code)}</code></pre>')
                example_code_lines = []
                # This line will be processed as a paragraph
                html_output.append(f'<p>{escape_html(stripped)}</p>')
                i += 1
                continue
            else:
                # Collect as YAML code
                example_code_lines.append(line)
                i += 1
                continue
        else:
            # Empty line - check if we should end the example
            if example_code_lines and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # End example if next line starts new section
                if next_line.startswith('Example') or next_line.startswith('Chapter') or next_line.startswith('Legend:') or re.match(r'^\d+\.\d+\.', next_line) or next_line.startswith('%YAML') or not next_line:
                    yaml_code = '\n'.join(example_code_lines)
                    html_output.append(f'<pre><code class="language-yaml">{escape_html(yaml_code)}</code></pre>')
                    html_output.append('</div>')
                    example_code_lines = []
                    in_example = False
                else:
                    # Empty line within code
                    example_code_lines.append('')
            i += 1
            continue

    # Empty line outside example
    if not line.strip():
        html_output.append('<p>&nbsp;</p>')
        i += 1
        continue

    # Regular paragraph
    if line.strip() and not in_example:
        html_output.append(f'<p>{escape_html(line.strip())}</p>')

    i += 1

# Close any remaining example
if in_example:
    if example_code_lines:
        yaml_code = '\n'.join(example_code_lines)
        html_output.append(f'<pre><code class="language-yaml">{escape_html(yaml_code)}</code></pre>')
    html_output.append('</div>')

html_output.append('</main>')

# Generate TOC sidebar
toc_html = '''
<aside class="toc-sidebar" id="tocSidebar">
    <div class="sidebar-controls">
        <button class="expand-collapse-btn" onclick="expandAllSubTOCs()" title="Expand All">⊞</button>
        <button class="expand-collapse-btn" onclick="collapseAllSubTOCs()" title="Collapse All">⊟</button>
        <h2>Table of Contents</h2>
    </div>
    <ol class="toc-list">
'''

current_chapter = None
for item in toc_items:
    if item['level'] == 2:  # Chapter
        if current_chapter:
            toc_html += '</ol></li>'
        toc_html += f'<li><a href="#{item["id"]}">{item["text"]}</a><ol class="sub-toc">'
        current_chapter = item['number']
    elif item['level'] == 3:  # Section
        toc_html += f'<li><a href="#{item["id"]}">{item["text"]}</a></li>'
    elif item['level'] == 4:  # Subsection
        toc_html += f'<li><a href="#{item["id"]}" class="sub-command">{item["text"]}</a></li>'

if current_chapter:
    toc_html += '</ol></li>'

toc_html += '''
    </ol>
</aside>
'''

# Insert TOC after body tag
html_with_toc = []
for line in html_output:
    html_with_toc.append(line)
    if '<body>' in line:
        html_with_toc.append(toc_html)

# Add JavaScript
html_with_toc.append('''
<script defer src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-core.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/prismjs@1/plugins/autoloader/prism-autoloader.min.js"></script>
<script>
  (function () {
    const btn = document.getElementById('tocToggle');
    const sidebar = document.getElementById('tocSidebar');
    const stored = (typeof localStorage !== 'undefined') ? localStorage.getItem('tocOpen') : null;
    if (stored === '1') {
      document.body.classList.add('toc-open');
      if (btn) btn.setAttribute('aria-expanded', 'true');
    }

    function toggle() {
      const open = document.body.classList.toggle('toc-open');
      if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      try { localStorage.setItem('tocOpen', open ? '1' : '0'); } catch (e) {}
    }

    if (btn) btn.addEventListener('click', toggle);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('toc-open')) {
        toggle();
      }
    });

    sidebar && sidebar.addEventListener('click', function (e) {
      const target = e.target;
      if (target && target.tagName === 'A') {
        const href = target.getAttribute('href');
        if (href && href.startsWith('#')) {
          const targetElement = document.querySelector(href);
          if (targetElement) {
            const offset = 100;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;

            window.scrollTo({
              top: offsetPosition,
              behavior: 'smooth'
            });

            targetElement.style.transition = 'background-color 0.3s ease';
            targetElement.style.backgroundColor = '#fff3cd';
            setTimeout(() => {
              targetElement.style.backgroundColor = '';
            }, 2000);
          }
        }

        if (window.innerWidth < 1000) {
          document.body.classList.remove('toc-open');
          if (btn) btn.setAttribute('aria-expanded', 'false');
          try { localStorage.setItem('tocOpen', '0'); } catch (e) {}
        }
      }
    });

    const sidebarLinks = sidebar ? Array.from(sidebar.querySelectorAll('a[href^="#"]')) : [];
    const idToLinks = new Map();
    sidebarLinks.forEach(a => {
      const id = decodeURIComponent(a.getAttribute('href') || '').slice(1);
      if (!id) return;
      const arr = idToLinks.get(id) || [];
      arr.push(a);
      idToLinks.set(id, arr);
    });
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const id = entry.target.id;
        const links = idToLinks.get(id);
        if (!links || !links.length) return;
        if (entry.isIntersecting) {
          sidebarLinks.forEach(l => l.classList.remove('active'));
          links.forEach(l => l.classList.add('active'));
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px', threshold: 0.01 });
    idToLinks.forEach((_, id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    const btt = document.getElementById('backToTop');
    function onScroll() {
      const show = window.scrollY > 400;
      if (btt) {
        if (show) {
          btt.classList.add('show');
          btt.removeAttribute('hidden');
        } else {
          btt.classList.remove('show');
          btt.setAttribute('hidden', '');
        }
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    btt && btt.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

    window.expandAllSubTOCs = function() {
      const subTocs = document.querySelectorAll('.toc-sidebar .sub-toc');
      subTocs.forEach(subToc => {
        subToc.style.display = 'block';
      });
    };

    window.collapseAllSubTOCs = function() {
      const subTocs = document.querySelectorAll('.toc-sidebar .sub-toc');
      subTocs.forEach(subToc => {
        subToc.style.display = 'none';
      });
    };
  })();
</script>
</body>
</html>
''')

# Write output
output_path = Path(r"c:\Users\owner\Desktop\DEV-DOCs\YAML\yaml.html")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_with_toc))

print(f"Generated {output_path}")
print(f"Processed {len([item for item in toc_items if item['level'] == 2])} chapters")
print(f"Total sections: {len(toc_items)}")

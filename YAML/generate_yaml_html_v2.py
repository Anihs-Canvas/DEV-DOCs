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
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum, auto
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
    LEGEND = auto()
    ERROR = auto()
    EMPTY = auto()

class ProcessingState(Enum):
    """Current processing state for state machine"""
    NORMAL = auto()
    IN_EXAMPLE = auto()

@dataclass
class ContentBlock:
    """Represents a structured block of content"""
    type: ContentType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    line_number: int = 0

@dataclass
class Example:
    """YAML example with comprehensive metadata"""
    number: str
    title: str
    description: str = ""
    code: str = ""
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

class YAMLSpecGenerator:
    """Advanced YAML Specification HTML Generator"""
    
    def __init__(self, content_path: Path, output_path: Path):
        self.content_path = Path(content_path)
        self.output_path = Path(output_path)
        self.lines: List[str] = []
        self.blocks: List[ContentBlock] = []
        self.examples: List[Example] = []
        self.stats = DocumentStats()
        self.state = ProcessingState.NORMAL
        self.current_example: Optional[Example] = None
        self.html_output: List[str] = []
        
        # Enhanced regex patterns
        self.patterns = {
            'chapter': re.compile(r'^Chapter\s+(\d+)\.\s+(.+)$'),
            'section': re.compile(r'^(\d+)\.(\d+)\.\s+(.+)$'),
            'subsection': re.compile(r'^(\d+)\.(\d+)\.(\d+)\.\s+(.+)$'),
            'example': re.compile(r'^Example\s+(\d+)\.(\d+)\.\s*(.*)$'),
            'production': re.compile(r'^\[(\d+)\]\s+(.+?)\s+::=\s+(.+)$'),
            'legend': re.compile(r'^Legend:\s*(.*)$'),
            'error': re.compile(r'^ERROR:\s*(.*)$'),
        }
    
    def load_content(self) -> None:
        """Load and validate content file"""
        try:
            if not self.content_path.exists():
                raise FileNotFoundError(f"Content file not found: {self.content_path}")
            
            with open(self.content_path, 'r', encoding='utf-8') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
            
            self.stats.total_lines = len(self.lines)
            logger.info(f"✅ Loaded {self.stats.total_lines} lines from {self.content_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load content: {e}")
            raise
    
    def parse_content(self) -> None:
        """Parse content into structured blocks"""
        start_time = datetime.now()
        logger.info("🔍 Starting content parsing...")
        
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
                logger.warning(f"⚠️ Error parsing line {i + 1}: {e}")
                i += 1
        
        self._end_current_example()
        
        self.stats.processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Parsing completed in {self.stats.processing_time:.2f}s")
        self._log_stats()
    
    def _parse_line(self, line: str, line_stripped: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Parse a single line and return content block and lines consumed"""
        
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
        
        # Handle example content
        if self.state == ProcessingState.IN_EXAMPLE:
            return self._handle_example_content(line, line_idx)
        
        # Regular paragraphs
        if line_stripped:
            return ContentBlock(type=ContentType.PARAGRAPH, content=line_stripped), 1
        
        return None, 1

    def _parse_chapter(self, match) -> ContentBlock:
        """Parse chapter header"""
        self._end_current_example()
        
        chapter_num = match.group(1)
        chapter_title = match.group(2)
        chapter_id = self._clean_id(f"chapter-{chapter_num}-{chapter_title}")
        
        return ContentBlock(
            type=ContentType.CHAPTER,
            content=f"Chapter {chapter_num}. {chapter_title}",
            metadata={'number': chapter_num, 'title': chapter_title, 'id': chapter_id}
        )

    def _parse_section(self, match) -> ContentBlock:
        """Parse section header"""
        self._end_current_example()
        
        section_num = f"{match.group(1)}.{match.group(2)}"
        section_title = match.group(3)
        section_id = self._clean_id(f"section-{section_num}-{section_title}")
        
        return ContentBlock(
            type=ContentType.SECTION,
            content=f"{section_num}. {section_title}",
            metadata={'number': section_num, 'title': section_title, 'id': section_id}
        )

    def _parse_subsection(self, match) -> ContentBlock:
        """Parse subsection header"""
        self._end_current_example()
        
        subsection_num = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        subsection_title = match.group(4)
        subsection_id = self._clean_id(f"section-{subsection_num}-{subsection_title}")
        
        return ContentBlock(
            type=ContentType.SUBSECTION,
            content=f"{subsection_num}. {subsection_title}",
            metadata={'number': subsection_num, 'title': subsection_title, 'id': subsection_id}
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
        
        while i < len(self.lines) and lines_consumed < 5:
            next_line = self.lines[i].strip()
            if next_line.startswith('(') and next_line.endswith(')'):
                self.current_example.description += next_line + " "
                lines_consumed += 1
                i += 1
            elif not next_line:
                lines_consumed += 1
                break
            else:
                break
        
        self.state = ProcessingState.IN_EXAMPLE
        
        return ContentBlock(
            type=ContentType.EXAMPLE,
            content=f"Example {example_num}. {example_title}",
            metadata={'number': example_num, 'title': example_title, 'description': self.current_example.description.strip()}
        ), lines_consumed

    def _parse_production(self, match) -> ContentBlock:
        """Parse BNF production rule"""
        prod_num = match.group(1)
        prod_name = match.group(2)
        prod_def = match.group(3)
        
        return ContentBlock(
            type=ContentType.PRODUCTION,
            content=f"[{prod_num}] {prod_name} ::= {prod_def}",
            metadata={'number': prod_num, 'name': prod_name, 'definition': prod_def}
        )

    def _parse_legend(self, line_idx: int) -> Tuple[ContentBlock, int]:
        """Parse legend section"""
        legend_content = []
        lines_consumed = 1
        i = line_idx + 1
        
        while i < len(self.lines):
            legend_line = self.lines[i].strip()
            if (not legend_line or legend_line.startswith('Example') or 
                legend_line.startswith('Chapter') or self.patterns['section'].match(legend_line)):
                break
            legend_content.append(legend_line)
            lines_consumed += 1
            i += 1
        
        return ContentBlock(
            type=ContentType.LEGEND,
            content='\n'.join(legend_content),
            metadata={'lines': legend_content}
        ), lines_consumed

    def _parse_error(self, match) -> ContentBlock:
        """Parse error marker"""
        return ContentBlock(
            type=ContentType.ERROR,
            content=match.group(1),
            metadata={'error_text': match.group(1)}
        )

    def _handle_example_content(self, line: str, line_idx: int) -> Tuple[Optional[ContentBlock], int]:
        """Handle content within an example"""
        line_stripped = line.strip()
        
        # Check for end of example
        if (line_stripped.startswith('Legend:') or line_stripped.startswith('ERROR:') or
            line_stripped.startswith('Example') or line_stripped.startswith('Chapter') or
            self.patterns['section'].match(line_stripped)):
            
            self._end_current_example()
            return None, 0  # Let main parser handle this line
        
        # Add to current example code
        if self.current_example:
            self.current_example.code += line + '\n'
        
        return None, 1

    def _end_current_example(self) -> None:
        """Finalize current example if it exists"""
        if self.current_example and self.state == ProcessingState.IN_EXAMPLE:
            self.current_example.code = self.current_example.code.strip()
            self.examples.append(self.current_example)
            self.current_example = None
            self.state = ProcessingState.NORMAL

    def _clean_id(self, text: str) -> str:
        """Create clean HTML ID from text"""
        clean = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[\s_]+', '-', clean).strip('-')

    def _update_stats(self, block: ContentBlock) -> None:
        """Update document statistics"""
        if block.type == ContentType.CHAPTER:
            self.stats.chapters += 1
        elif block.type in [ContentType.SECTION, ContentType.SUBSECTION]:
            self.stats.sections += 1
        elif block.type == ContentType.EXAMPLE:
            self.stats.examples += 1
        elif block.type == ContentType.PRODUCTION:
            self.stats.productions += 1
        elif block.type == ContentType.ERROR:
            self.stats.errors += 1

    def _log_stats(self) -> None:
        """Log parsing statistics"""
        logger.info("📊 Parsing Statistics:")
        logger.info(f"   📚 Chapters: {self.stats.chapters}")
        logger.info(f"   📑 Sections: {self.stats.sections}")
        logger.info(f"   💡 Examples: {self.stats.examples}")
        logger.info(f"   🔧 Productions: {self.stats.productions}")
        logger.info(f"   ❌ Errors: {self.stats.errors}")

    def generate_html(self) -> None:
        """Generate complete HTML document"""
        logger.info("🎨 Generating enhanced HTML...")
        
        self.html_output = []
        
        self._generate_header()
        self._generate_navigation()
        self._generate_main_content()
        self._generate_toc_sidebar()
        self._generate_footer()
        self._generate_scripts()
        
        logger.info("✅ HTML generation completed")

    def _generate_header(self) -> None:
        """Generate HTML header with enhanced metadata"""
        self.html_output.extend([
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <meta name="description" content="Complete YAML 1.1 Specification with examples and production rules">',
            '    <meta name="author" content="YAML Community">',
            f'    <meta name="generator" content="Advanced YAML Spec Generator v2.0">',
            f'    <meta name="build-date" content="{datetime.now().isoformat()}">',
            '    <title>YAML 1.1 Specification - Enhanced Complete Reference</title>',
            '    <link rel="preload" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism.min.css" as="style">',
            '    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism.min.css">'
        ])
        
        self._generate_css()

    def _generate_css(self) -> None:
        """Generate comprehensive CSS styles"""
        self.html_output.extend([
            '    <style>',
            '        :root {',
            '            --primary: #1e3a8a;',
            '            --secondary: #2563eb;',
            '            --accent: #dc2626;',
            '            --bg: #fafafa;',
            '            --text: #1f2937;',
            '            --border: #e5e7eb;',
            '            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);',
            '        }',
            '        ',
            '        * { box-sizing: border-box; }',
            '        ',
            '        body {',
            '            font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;',
            '            line-height: 1.6;',
            '            color: var(--text);',
            '            background: var(--bg);',
            '            margin: 0;',
            '            scroll-behavior: smooth;',
            '        }',
            '        ',
            '        .main-header {',
            '            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);',
            '            color: white;',
            '            box-shadow: var(--shadow);',
            '        }',
            '        ',
            '        .header-container {',
            '            max-width: 1200px;',
            '            margin: 0 auto;',
            '            padding: 2rem 1.5rem;',
            '            display: flex;',
            '            justify-content: space-between;',
            '            align-items: center;',
            '            flex-wrap: wrap;',
            '            gap: 1.5rem;',
            '        }',
            '        ',
            '        .header-brand {',
            '            display: flex;',
            '            align-items: center;',
            '            gap: 1rem;',
            '        }',
            '        ',
            '        .brand-icon {',
            '            width: 56px;',
            '            height: 56px;',
            '            background: linear-gradient(135deg, var(--accent), #ef4444);',
            '            border-radius: 16px;',
            '            display: flex;',
            '            align-items: center;',
            '            justify-content: center;',
            '            color: white;',
            '            font-weight: 800;',
            '            font-size: 28px;',
            '        }',
            '        ',
            '        .brand-text h1 {',
            '            margin: 0;',
            '            font-size: 2rem;',
            '            font-weight: 800;',
            '            background: linear-gradient(135deg, #ffffff, #e2e8f0);',
            '            -webkit-background-clip: text;',
            '            -webkit-text-fill-color: transparent;',
            '        }',
            '        ',
            '        .brand-subtitle {',
            '            margin: 0.25rem 0 0 0;',
            '            font-size: 0.9rem;',
            '            color: #94a3b8;',
            '            font-weight: 500;',
            '        }',
            '        ',
            '        .header-stats {',
            '            display: grid;',
            '            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));',
            '            gap: 2rem;',
            '        }',
            '        ',
            '        .stat-item {',
            '            text-align: center;',
            '            background: rgba(255, 255, 255, 0.1);',
            '            backdrop-filter: blur(10px);',
            '            border-radius: 12px;',
            '            padding: 1rem;',
            '            border: 1px solid rgba(255, 255, 255, 0.1);',
            '        }',
            '        ',
            '        .stat-number {',
            '            display: block;',
            '            font-size: 1.75rem;',
            '            font-weight: 800;',
            '            color: #ffffff;',
            '        }',
            '        ',
            '        .stat-label {',
            '            display: block;',
            '            font-size: 0.8rem;',
            '            color: #cbd5e1;',
            '            margin-top: 0.25rem;',
            '        }',
            '        ',
            '        #tocToggle {',
            '            position: fixed;',
            '            top: 20px;',
            '            left: 20px;',
            '            z-index: 1001;',
            '            background: linear-gradient(135deg, var(--accent), #ef4444);',
            '            color: white;',
            '            border: none;',
            '            border-radius: 12px;',
            '            padding: 14px 18px;',
            '            cursor: pointer;',
            '            box-shadow: var(--shadow);',
            '            font-weight: 600;',
            '            transition: all 0.3s ease;',
            '        }',
            '        ',
            '        #tocToggle:hover {',
            '            transform: translateY(-2px);',
            '        }',
            '        ',
            '        .toc-sidebar {',
            '            position: fixed;',
            '            top: 0;',
            '            left: 0;',
            '            height: 100vh;',
            '            width: 350px;',
            '            background: white;',
            '            border-right: 1px solid var(--border);',
            '            box-shadow: var(--shadow);',
            '            padding: 1rem;',
            '            overflow-y: auto;',
            '            transform: translateX(-100%);',
            '            transition: transform 0.3s ease;',
            '            z-index: 1000;',
            '        }',
            '        ',
            '        body.toc-open .toc-sidebar {',
            '            transform: translateX(0);',
            '        }',
            '        ',
            '        main {',
            '            max-width: 1200px;',
            '            margin: 2rem auto;',
            '            padding: 2rem;',
            '            background: white;',
            '            border-radius: 16px;',
            '            box-shadow: var(--shadow);',
            '        }',
            '        ',
            '        .chapter {',
            '            margin-bottom: 4rem;',
            '        }',
            '        ',
            '        h2 {',
            '            font-size: 2.25rem;',
            '            font-weight: 800;',
            '            color: var(--primary);',
            '            margin: 0 0 2rem 0;',
            '            padding-bottom: 1rem;',
            '            border-bottom: 3px solid var(--secondary);',
            '            scroll-margin-top: 100px;',
            '        }',
            '        ',
            '        h3 {',
            '            font-size: 1.75rem;',
            '            font-weight: 700;',
            '            color: #1e40af;',
            '            margin: 2.5rem 0 1.5rem 0;',
            '            scroll-margin-top: 100px;',
            '        }',
            '        ',
            '        h4 {',
            '            font-size: 1.375rem;',
            '            font-weight: 600;',
            '            color: var(--secondary);',
            '            margin: 2rem 0 1rem 0;',
            '            scroll-margin-top: 100px;',
            '        }',
            '        ',
            '        h5 {',
            '            font-size: 1.125rem;',
            '            font-weight: 600;',
            '            color: #3b82f6;',
            '            margin: 1.5rem 0 1rem 0;',
            '        }',
            '        ',
            '        p {',
            '            margin-bottom: 1.25rem;',
            '            line-height: 1.7;',
            '        }',
            '        ',
            '        .example {',
            '            background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);',
            '            border: 2px solid #fde047;',
            '            border-radius: 16px;',
            '            padding: 2rem;',
            '            margin: 2.5rem 0;',
            '            box-shadow: var(--shadow);',
            '            position: relative;',
            '        }',
            '        ',
            '        .example::before {',
            '            content: "";',
            '            position: absolute;',
            '            top: 0;',
            '            left: 0;',
            '            right: 0;',
            '            height: 4px;',
            '            background: linear-gradient(90deg, #f59e0b, #eab308);',
            '        }',
            '        ',
            '        .example h5 {',
            '            color: #92400e;',
            '            margin-top: 0;',
            '            font-weight: 700;',
            '        }',
            '        ',
            '        .production {',
            '            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);',
            '            border-left: 6px solid #6366f1;',
            '            border-radius: 8px;',
            '            padding: 1.5rem 2rem;',
            '            margin: 1.5rem 0;',
            '            font-family: "JetBrains Mono", Consolas, monospace;',
            '            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);',
            '        }',
            '        ',
            '        .prod-num {',
            '            color: #6366f1;',
            '            font-weight: 700;',
            '            margin-right: 1rem;',
            '        }',
            '        ',
            '        .legend {',
            '            background: #fef3c7;',
            '            border-left: 4px solid #f59e0b;',
            '            padding: 1.5rem;',
            '            margin: 1.5rem 0;',
            '            color: #92400e;',
            '            font-style: italic;',
            '            border-radius: 8px;',
            '        }',
            '        ',
            '        .error-block {',
            '            background: #fef2f2;',
            '            border-left: 4px solid #ef4444;',
            '            padding: 1.5rem;',
            '            margin: 1.5rem 0;',
            '            color: #dc2626;',
            '            font-weight: 600;',
            '            border-radius: 8px;',
            '        }',
            '        ',
            '        pre {',
            '            background: linear-gradient(135deg, #1e293b, #334155);',
            '            color: #e2e8f0;',
            '            padding: 2rem;',
            '            border-radius: 12px;',
            '            overflow-x: auto;',
            '            margin: 1.5rem 0;',
            '            font-family: "JetBrains Mono", Consolas, monospace;',
            '            border: 1px solid rgba(255, 255, 255, 0.1);',
            '        }',
            '        ',
            '        code {',
            '            background: #f1f5f9;',
            '            color: #475569;',
            '            padding: 0.25rem 0.5rem;',
            '            border-radius: 6px;',
            '            font-family: "JetBrains Mono", Consolas, monospace;',
            '        }',
            '        ',
            '        pre code {',
            '            background: transparent;',
            '            color: inherit;',
            '            padding: 0;',
            '        }',
            '        ',
            '        @media (max-width: 768px) {',
            '            .header-container {',
            '                flex-direction: column;',
            '                text-align: center;',
            '            }',
            '            main {',
            '                margin: 1rem;',
            '                padding: 1.5rem;',
            '            }',
            '            .toc-sidebar {',
            '                width: 100%;',
            '            }',
            '        }',
            '    </style>',
            '</head>',
            '<body>'
        ])

    def _generate_navigation(self) -> None:
        """Generate navigation header"""
        self.html_output.extend([
            '    <div class="main-header">',
            '        <div class="header-container">',
            '            <div class="header-brand">',
            '                <div class="brand-icon">Y</div>',
            '                <div class="brand-text">',
            '                    <h1>YAML 1.1 Specification</h1>',
            '                    <p class="brand-subtitle">Enhanced Complete Reference v2.0</p>',
            '                </div>',
            '            </div>',
            '            <div class="header-stats">',
            f'                <div class="stat-item">',
            f'                    <span class="stat-number">{self.stats.examples}</span>',
            f'                    <span class="stat-label">Examples</span>',
            f'                </div>',
            f'                <div class="stat-item">',
            f'                    <span class="stat-number">{self.stats.productions}</span>',
            f'                    <span class="stat-label">Productions</span>',
            f'                </div>',
            f'                <div class="stat-item">',
            f'                    <span class="stat-number">{self.stats.chapters}</span>',
            f'                    <span class="stat-label">Chapters</span>',
            f'                </div>',
            '            </div>',
            '        </div>',
            '    </div>',
            '',
            '    <button id="tocToggle" aria-label="Toggle table of contents">',
            '        ☰ Table of Contents',
            '    </button>'
        ])

    def _generate_main_content(self) -> None:
        """Generate main content from parsed blocks"""
        self.html_output.append('    <main>')
        
        current_chapter = None
        toc_items = []
        
        for block in self.blocks:
            if block.type == ContentType.CHAPTER:
                if current_chapter:
                    self.html_output.append('    </div>')
                
                self.html_output.extend([
                    '    <div class="chapter">',
                    f'        <h2 id="{block.metadata["id"]}">{self._escape_html(block.content)}</h2>'
                ])
                current_chapter = block.metadata['number']
                toc_items.append(block)
                
            elif block.type == ContentType.SECTION:
                self.html_output.append(
                    f'        <h3 id="{block.metadata["id"]}">{self._escape_html(block.content)}</h3>'
                )
                toc_items.append(block)
                
            elif block.type == ContentType.SUBSECTION:
                self.html_output.append(
                    f'        <h4 id="{block.metadata["id"]}">{self._escape_html(block.content)}</h4>'
                )
                toc_items.append(block)
                
            elif block.type == ContentType.EXAMPLE:
                self._render_example(block)
                
            elif block.type == ContentType.PRODUCTION:
                self._render_production(block)
                
            elif block.type == ContentType.LEGEND:
                self._render_legend(block)
                
            elif block.type == ContentType.ERROR:
                self._render_error(block)
                
            elif block.type == ContentType.PARAGRAPH:
                self.html_output.append(f'        <p>{self._escape_html(block.content)}</p>')
        
        if current_chapter:
            self.html_output.append('    </div>')
        
        self.html_output.append('    </main>')
        
        # Store TOC items for sidebar generation
        self.toc_items = toc_items

    def _render_example(self, block: ContentBlock) -> None:
        """Render an example block"""
        example = next((ex for ex in self.examples if ex.number == block.metadata['number']), None)
        
        self.html_output.extend([
            '        <div class="example">',
            f'            <h5>Example {block.metadata["number"]}. {self._escape_html(block.metadata["title"])}</h5>'
        ])
        
        if block.metadata.get('description'):
            self.html_output.append(f'            <p>{self._escape_html(block.metadata["description"])}</p>')
        
        if example and example.code:
            self.html_output.extend([
                '            <pre><code class="language-yaml">',
                self._escape_html(example.code),
                '</code></pre>'
            ])
        
        self.html_output.append('        </div>')

    def _render_production(self, block: ContentBlock) -> None:
        """Render a production rule"""
        self.html_output.extend([
            '        <div class="production">',
            f'            <span class="prod-num">[{block.metadata["number"]}]</span>',
            f'            <code>{self._escape_html(block.metadata["name"])} ::= {self._escape_html(block.metadata["definition"])}</code>',
            '        </div>'
        ])

    def _render_legend(self, block: ContentBlock) -> None:
        """Render a legend block"""
        self.html_output.extend([
            '        <div class="legend">',
            '            <strong>Legend:</strong><br>'
        ])
        
        for line in block.metadata.get('lines', []):
            self.html_output.append(f'            {self._escape_html(line)}<br>')
        
        self.html_output.append('        </div>')

    def _render_error(self, block: ContentBlock) -> None:
        """Render an error block"""
        self.html_output.extend([
            '        <div class="error-block">',
            f'            <strong>ERROR:</strong> {self._escape_html(block.metadata["error_text"])}',
            '        </div>'
        ])

    def _generate_toc_sidebar(self) -> None:
        """Generate table of contents sidebar"""
        toc_html = [
            '    <aside class="toc-sidebar" id="tocSidebar">',
            '        <h2>Table of Contents</h2>',
            '        <ol>'
        ]
        
        current_chapter = None
        for item in self.toc_items:
            if item.type == ContentType.CHAPTER:
                if current_chapter:
                    toc_html.append('            </ol></li>')
                toc_html.extend([
                    f'            <li><a href="#{item.metadata["id"]}">{item.content}</a>',
                    '                <ol>'
                ])
                current_chapter = item.metadata['number']
            elif item.type in [ContentType.SECTION, ContentType.SUBSECTION]:
                toc_html.append(f'                <li><a href="#{item.metadata["id"]}">{item.content}</a></li>')
        
        if current_chapter:
            toc_html.append('            </ol></li>')
        
        toc_html.extend(['        </ol>', '    </aside>'])
        
        # Insert TOC after body tag
        body_index = next(i for i, line in enumerate(self.html_output) if '<body>' in line)
        self.html_output[body_index+1:body_index+1] = toc_html

    def _generate_footer(self) -> None:
        """Generate footer"""
        self.html_output.extend([
            '    <footer style="text-align: center; padding: 2rem; background: #f9fafb; margin-top: 3rem;">',
            '        <p>&copy; 2001-2008 Oren Ben-Kiki, Clark Evans, Ingy döt Net</p>',
            f'        <p>Enhanced with YAML Spec Generator v2.0 | Build: {self.stats.processing_time:.2f}s</p>',
            '    </footer>'
        ])

    def _generate_scripts(self) -> None:
        """Generate JavaScript for enhanced functionality"""
        self.html_output.extend([
            '    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>',
            '    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-yaml.min.js"></script>',
            '    <script>',
            '        (function() {',
            '            const btn = document.getElementById("tocToggle");',
            '            const sidebar = document.getElementById("tocSidebar");',
            '            ',
            '            function toggle() {',
            '                document.body.classList.toggle("toc-open");',
            '            }',
            '            ',
            '            if (btn) btn.addEventListener("click", toggle);',
            '            ',
            '            document.addEventListener("keydown", function(e) {',
            '                if (e.key === "Escape") toggle();',
            '            });',
            '            ',
            '            if (sidebar) {',
            '                sidebar.addEventListener("click", function(e) {',
            '                    if (e.target.tagName === "A") {',
            '                        const href = e.target.getAttribute("href");',
            '                        if (href && href.startsWith("#")) {',
            '                            e.preventDefault();',
            '                            const target = document.querySelector(href);',
            '                            if (target) {',
            '                                target.scrollIntoView({ behavior: "smooth" });',
            '                            }',
            '                        }',
            '                    }',
            '                });',
            '            }',
            '            ',
            f'            console.log("🚀 YAML Spec Generator v2.0");',
            f'            console.log("📊 {self.stats.total_lines} lines → {self.stats.chapters} chapters, {self.stats.examples} examples");',
            '        })();',
            '    </script>',
            '</body>',
            '</html>'
        ])

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;'))

    def save_html(self) -> None:
        """Save generated HTML to file"""
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.html_output))
            
            logger.info(f"✅ Enhanced HTML saved to {self.output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save HTML: {e}")
            raise

    def run(self) -> None:
        """Run the complete generation process"""
        start_time = datetime.now()
        
        try:
            logger.info("🚀 Starting YAML Spec Generator v2.0")
            
            self.load_content()
            self.parse_content()  
            self.generate_html()
            self.save_html()
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n🎉 Enhanced YAML Specification Generated!")
            print(f"📁 Output: {self.output_path}")
            print(f"📊 Statistics:")
            print(f"   • Chapters: {self.stats.chapters}")
            print(f"   • Sections: {self.stats.sections}")
            print(f"   • Examples: {self.stats.examples}")
            print(f"   • Productions: {self.stats.productions}")
            print(f"   • Parse time: {self.stats.processing_time:.2f}s")
            print(f"   • Total time: {total_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise


def main():
    """Main entry point"""
    content_path = Path(r"c:\Users\owner\Desktop\DEV-DOCs\YAML\content.txt")
    output_path = Path(r"c:\Users\owner\Desktop\DEV-DOCs\YAML\yaml_enhanced.html")
    
    generator = YAMLSpecGenerator(content_path, output_path)
    generator.run()


if __name__ == "__main__":
    main()

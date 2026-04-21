"""
PDF ingestion pipeline — extracts text, structure, and metadata from style guide PDFs.
"""
import pdfplumber
import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ExtractedSection:
    title: str
    content: str
    page_number: int
    source_file: str


@dataclass
class ExtractedDocument:
    filename: str
    title: str
    total_pages: int
    sections: list[ExtractedSection] = field(default_factory=list)
    raw_text: str = ""


def _detect_title(first_page_text: str, filename: str) -> str:
    """Infer document title from first page or filename."""
    lines = [l.strip() for l in first_page_text.split("\n") if l.strip()]
    if lines:
        # Usually the title is the first non-empty line and is short
        candidate = lines[0]
        if len(candidate) < 100:
            return candidate
    # Fallback to filename
    return Path(filename).stem.replace(".", " ").replace("-", " ")


def _detect_sections(text: str, page_num: int, source: str) -> list[ExtractedSection]:
    """Split text into sections based on heading patterns."""
    # Patterns that indicate section headings in these style guides:
    # ALL CAPS lines, bold markers, numbered headings, Roman numeral headings
    heading_patterns = [
        r"^([A-Z][A-Z\s&,]{4,})$",  # ALL CAPS HEADINGS
        r"^((?:I{1,3}V?|VI{0,3}|IX|X{0,3})\.?\s+.+)$",  # Roman numeral headings (I. II. III.)
        r"^(\d+\.\s+.+)$",  # Numbered headings
        r"^([A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+and\s+[a-z]+)*)$",  # Title Case short headings
    ]

    sections = []
    current_title = "General"
    current_content_lines = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            current_content_lines.append("")
            continue

        is_heading = False
        for pattern in heading_patterns:
            if re.match(pattern, stripped) and len(stripped) < 80:
                # Save previous section
                content = "\n".join(current_content_lines).strip()
                if content:
                    sections.append(ExtractedSection(
                        title=current_title,
                        content=content,
                        page_number=page_num,
                        source_file=source,
                    ))
                current_title = stripped
                current_content_lines = []
                is_heading = True
                break

        if not is_heading:
            current_content_lines.append(stripped)

    # Don't forget the last section
    content = "\n".join(current_content_lines).strip()
    if content:
        sections.append(ExtractedSection(
            title=current_title,
            content=content,
            page_number=page_num,
            source_file=source,
        ))

    return sections


def extract_pdf(filepath: str) -> ExtractedDocument:
    """Extract structured content from a single PDF."""
    filename = Path(filepath).name
    all_text_parts = []
    all_sections = []

    with pdfplumber.open(filepath) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            all_text_parts.append(text)

            page_sections = _detect_sections(text, page_num=i + 1, source=filename)
            all_sections.extend(page_sections)

    raw_text = "\n\n".join(all_text_parts)
    title = _detect_title(all_text_parts[0] if all_text_parts else "", filename)

    # Merge very small consecutive sections with the same title
    merged = []
    for sec in all_sections:
        if merged and merged[-1].title == sec.title:
            merged[-1].content += "\n" + sec.content
        else:
            merged.append(sec)

    return ExtractedDocument(
        filename=filename,
        title=title,
        total_pages=total_pages,
        sections=merged,
        raw_text=raw_text,
    )


def extract_all_pdfs(directory: str) -> list[ExtractedDocument]:
    """Extract content from all PDFs in a directory."""
    pdf_dir = Path(directory)
    docs = []
    for pdf_file in sorted(pdf_dir.glob("*.pdf")):
        try:
            doc = extract_pdf(str(pdf_file))
            docs.append(doc)
        except Exception as e:
            print(f"Warning: Failed to parse {pdf_file.name}: {e}")
    return docs

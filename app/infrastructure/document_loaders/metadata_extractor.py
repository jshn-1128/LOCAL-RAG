"""
Metadata extraction for loaded documents.

Extracts file-level and content-level metadata:
  - File stats (size, creation time, modification time)
  - Content stats (word count, character count)
  - Format-specific metadata (PDF author, Markdown front matter, DOCX metadata)
"""

from __future__ import annotations

from typing import Any

from app.domain.models.document import DocumentMetadata


def extract_content_stats(content: str) -> DocumentMetadata:
    """Extract content-level metadata (word and character counts).

    Returns a DocumentMetadata with word/character counts populated.
    """
    word_count = len(content.split()) if content.strip() else 0
    char_count = len(content)

    return DocumentMetadata(
        word_count=word_count,
        character_count=char_count,
    )


def extract_pdf_metadata(pdf_metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Extract relevant fields from PyPDF metadata dict.

    PyPDF returns metadata as a dict with keys like '/Author', '/Title', etc.
    This normalises them to lowercase and filters known fields.
    """
    if not pdf_metadata:
        return {}

    result: dict[str, Any] = {}
    known_fields = {
        "/Author": "author",
        "/Title": "title",
        "/Subject": "subject",
        "/Keywords": "keywords",
        "/Creator": "creator",
        "/Producer": "producer",
    }
    for pdf_key, domain_key in known_fields.items():
        value = pdf_metadata.get(pdf_key)
        if value and str(value).strip():
            result[domain_key] = str(value).strip()
    return result


def extract_markdown_front_matter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML-like front matter from markdown content.

    Returns (metadata_dict, body_content).
    This simple implementation handles basic key: value pairs.
    More complex front matter parsing can be added later.
    """
    metadata: dict[str, Any] = {}
    body = content

    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            front = content[3:end_idx].strip()
            body = content[end_idx + 3 :].strip()
            for line in front.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    metadata[key.strip().lower()] = value.strip()

    return metadata, body


def extract_docx_metadata(core_properties: Any) -> dict[str, Any]:
    """Extract metadata from python-docx core properties.

    python-docx exposes CoreProperties with .author, .title, etc.
    """
    result: dict[str, Any] = {}
    if core_properties is None:
        return result
    if hasattr(core_properties, "author") and core_properties.author:
        result["author"] = core_properties.author
    if hasattr(core_properties, "title") and core_properties.title:
        result["title"] = core_properties.title
    return result

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pymupdf


def slugify(value: str) -> str:
    """
    Convert a filename or title into a simple stable identifier.

    Example:
        "Retrieval Augmented Generation" ->
        "retrieval-augmented-generation"
    """
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def extract_pdf(pdf_path: str | Path) -> dict[str, Any]:
    """
    Extract text from a PDF while preserving page boundaries.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.

    Returns
    -------
    dict
        Structured paper metadata and page-level text.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {pdf_path}")

    with pymupdf.open(pdf_path) as document:
        metadata = document.metadata or {}

        title = (metadata.get("title") or pdf_path.stem).strip()
        authors = (metadata.get("author") or "").strip()

        pages = []

        for page_index, page in enumerate(document):
            text = page.get_text("text").strip()

            pages.append(
                {
                    "page_number": page_index + 1,
                    "text": text,
                    "char_count": len(text),
                }
            )

        return {
            "paper_id": slugify(pdf_path.stem),
            "title": title,
            "authors": authors,
            "source_file": pdf_path.name,
            "page_count": len(document),
            "pages": pages,
        }


def save_extracted_pdf(
    pdf_path: str | Path,
    output_dir: str | Path = "data/processed",
) -> Path:
    """
    Extract a PDF and save the structured result as JSON.
    """

    paper = extract_pdf(pdf_path)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{paper['paper_id']}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            paper,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract page-aware text from a research paper."
    )

    parser.add_argument(
        "pdf",
        help="Path to the PDF file.",
    )

    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Directory where extracted JSON will be saved.",
    )

    args = parser.parse_args()

    output_path = save_extracted_pdf(
        pdf_path=args.pdf,
        output_dir=args.output_dir,
    )

    print(f"Extraction complete: {output_path}")


if __name__ == "__main__":
    main()
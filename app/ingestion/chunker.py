from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def normalize_text(text: str) -> str:
    """
    Clean common PDF extraction artifacts while preserving content.
    """

    # Join words split across line breaks:
    # "seman-\ntic" -> "semantic"
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)

    # Replace remaining line breaks and repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 180,
    overlap: int = 40,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = normalize_text(text).split()

    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

    return chunks


def chunk_paper(
    paper: dict[str, Any],
    chunk_size: int = 180,
    overlap: int = 40,
) -> dict[str, Any]:
    """
    Chunk every page while preserving paper and page metadata.
    """

    paper_id = paper["paper_id"]
    chunks = []

    for page in paper["pages"]:
        page_number = page["page_number"]

        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, text in enumerate(page_chunks, start=1):
            chunks.append(
                {
                    "chunk_id": (
                        f"{paper_id}-"
                        f"p{page_number:03d}-"
                        f"c{chunk_index:03d}"
                    ),
                    "paper_id": paper_id,
                    "title": paper.get("title", ""),
                    "authors": paper.get("authors", ""),
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": text,
                    "word_count": len(text.split()),
                }
            )

    return {
        "paper_id": paper_id,
        "title": paper.get("title", ""),
        "authors": paper.get("authors", ""),
        "source_file": paper.get("source_file", ""),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


def chunk_json_file(
    input_path: str | Path,
    output_dir: str | Path = "data/processed",
    chunk_size: int = 180,
    overlap: int = 40,
) -> Path:
    """
    Load an extracted PaperLens JSON file and save chunked output.
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input JSON not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as file:
        paper = json.load(file)

    chunked_paper = chunk_paper(
        paper,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{paper['paper_id']}-chunks.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            chunked_paper,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chunk an extracted PaperLens research paper."
    )

    parser.add_argument(
        "input",
        help="Path to extracted PaperLens JSON.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=180,
        help="Maximum words per chunk.",
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=40,
        help="Number of overlapping words.",
    )

    parser.add_argument(
        "--output-dir",
        default="data/processed",
    )

    args = parser.parse_args()

    output_path = chunk_json_file(
        input_path=args.input,
        output_dir=args.output_dir,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    print(f"Chunking complete: {output_path}")


if __name__ == "__main__":
    main()
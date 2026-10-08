import pytest

from app.ingestion.chunker import (
    chunk_paper,
    chunk_text,
    normalize_text,
)


def test_normalize_hyphenated_line_break():
    text = "This does not guarantee seman-\ntic integrity."

    cleaned = normalize_text(text)

    assert cleaned == "This does not guarantee semantic integrity."


def test_chunk_text_with_overlap():
    words = [f"word{i}" for i in range(250)]
    text = " ".join(words)

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) == 3

    first = chunks[0].split()
    second = chunks[1].split()

    assert len(first) == 100
    assert first[-20:] == second[:20]


def test_chunk_paper_preserves_page_metadata():
    paper = {
        "paper_id": "test-paper",
        "title": "Test Paper",
        "authors": "Researcher",
        "source_file": "test.pdf",
        "pages": [
            {
                "page_number": 1,
                "text": " ".join(["retrieval"] * 220),
            },
            {
                "page_number": 2,
                "text": " ".join(["hallucination"] * 220),
            },
        ],
    }

    result = chunk_paper(
        paper,
        chunk_size=100,
        overlap=20,
    )

    assert result["chunk_count"] == 6

    page_1_chunks = [
        chunk
        for chunk in result["chunks"]
        if chunk["page_number"] == 1
    ]

    page_2_chunks = [
        chunk
        for chunk in result["chunks"]
        if chunk["page_number"] == 2
    ]

    assert len(page_1_chunks) == 3
    assert len(page_2_chunks) == 3

    assert page_1_chunks[0]["chunk_id"] == "test-paper-p001-c001"
    assert page_2_chunks[0]["chunk_id"] == "test-paper-p002-c001"


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "some example text",
            chunk_size=100,
            overlap=100,
        )
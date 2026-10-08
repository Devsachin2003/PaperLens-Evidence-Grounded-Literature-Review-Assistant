import json

import pymupdf

from app.ingestion.pdf_loader import extract_pdf, save_extracted_pdf


def create_test_pdf(path):
    """
    Create a tiny two-page PDF for testing.
    """

    document = pymupdf.open()

    page_1 = document.new_page()
    page_1.insert_text(
        (72, 72),
        "Retrieval augmented generation improves access to external knowledge.",
    )

    page_2 = document.new_page()
    page_2.insert_text(
        (72, 72),
        "Hallucination remains possible when retrieved evidence is irrelevant.",
    )

    document.set_metadata(
        {
            "title": "Test RAG Paper",
            "author": "Test Researcher",
        }
    )

    document.save(path)
    document.close()


def test_extract_pdf_preserves_pages(tmp_path):
    pdf_path = tmp_path / "test_paper.pdf"

    create_test_pdf(pdf_path)

    paper = extract_pdf(pdf_path)

    assert paper["title"] == "Test RAG Paper"
    assert paper["authors"] == "Test Researcher"
    assert paper["page_count"] == 2

    assert paper["pages"][0]["page_number"] == 1
    assert paper["pages"][1]["page_number"] == 2

    assert "Retrieval augmented generation" in paper["pages"][0]["text"]
    assert "Hallucination" in paper["pages"][1]["text"]


def test_save_extracted_pdf(tmp_path):
    pdf_path = tmp_path / "test_paper.pdf"
    output_dir = tmp_path / "processed"

    create_test_pdf(pdf_path)

    output_path = save_extracted_pdf(
        pdf_path,
        output_dir,
    )

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data["page_count"] == 2
    assert len(saved_data["pages"]) == 2
"""Automated test suite for document_reader.py.

Tests PDF extraction, integrity verification, edge cases, scanned document detection,
and processing limits without requiring external network access.
"""

import io
import os
import pytest
from reportlab.pdfgen import canvas
import pypdf

from document_reader import extract_text_from_pdf, validate_document_pair
from schemas import DocumentInfo


def create_in_memory_pdf(text: str = "Hello World", num_pages: int = 1) -> bytes:
    """Helper to generate a valid PDF byte stream with specified text and pages."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    for i in range(num_pages):
        if text:
            c.drawString(100, 700, f"{text} (Page {i+1})")
        c.showPage()
    c.save()
    return buffer.getvalue()


def create_blank_pdf(num_pages: int = 1) -> bytes:
    """Helper to generate a PDF with no extractable text (simulating blank/scanned page)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    for _ in range(num_pages):
        # Draw a line or circle, no drawString
        c.circle(100, 100, 50)
        c.showPage()
    c.save()
    return buffer.getvalue()


def test_valid_pdf_extraction():
    """Verify that a valid text-based PDF is properly extracted."""
    pdf_bytes = create_in_memory_pdf("This is a policy requirement.", num_pages=2)
    doc_info = extract_text_from_pdf(pdf_bytes, "policy.pdf")

    assert doc_info.is_valid is True
    assert doc_info.filename == "policy.pdf"
    assert doc_info.page_count == 2
    assert doc_info.character_count > 0
    assert len(doc_info.pages) == 2
    assert "Page 1" in doc_info.pages[0].text
    assert "Page 2" in doc_info.pages[1].text
    assert doc_info.error_message is None


def test_sample_documents_extraction():
    """Verify extraction on bundled sample policy documents."""
    sample_a = os.path.join("sample_documents", "policy_v1.pdf")
    sample_b = os.path.join("sample_documents", "policy_v2.pdf")

    assert os.path.exists(sample_a), "policy_v1.pdf must exist"
    assert os.path.exists(sample_b), "policy_v2.pdf must exist"

    with open(sample_a, "rb") as f:
        doc_a = extract_text_from_pdf(f.read(), "policy_v1.pdf")
    with open(sample_b, "rb") as f:
        doc_b = extract_text_from_pdf(f.read(), "policy_v2.pdf")

    assert doc_a.is_valid is True
    assert doc_a.page_count == 2
    assert "$500.00" in doc_a.full_text

    assert doc_b.is_valid is True
    assert doc_b.page_count == 2
    assert "$750.00" in doc_b.full_text


def test_missing_document():
    """Verify that a None input is rejected with an informative error message."""
    doc_info = extract_text_from_pdf(None, "missing.pdf")
    assert doc_info.is_valid is False
    assert "No file was provided" in doc_info.error_message


def test_empty_zero_byte_file():
    """Verify that a 0-byte file is rejected."""
    doc_info = extract_text_from_pdf(b"", "empty.pdf")
    assert doc_info.is_valid is False
    assert "empty file" in doc_info.error_message.lower()


def test_unsupported_file_extension():
    """Verify that non-PDF extensions are rejected."""
    doc_info = extract_text_from_pdf(b"Dummy content", "document.docx")
    assert doc_info.is_valid is False
    assert "Only PDF (.pdf) files are supported" in doc_info.error_message


def test_invalid_pdf_bytes():
    """Verify that files without the %PDF- magic header are rejected."""
    fake_pdf = b"This is just plain text disguised as a PDF file."
    doc_info = extract_text_from_pdf(fake_pdf, "fake.pdf")
    assert doc_info.is_valid is False
    assert "not a valid PDF file" in doc_info.error_message


def test_corrupted_pdf_stream():
    """Verify corrupted PDF stream handling."""
    corrupted_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\nThis is corrupt data trailing."
    doc_info = extract_text_from_pdf(corrupted_bytes, "corrupt.pdf")
    assert doc_info.is_valid is False
    assert doc_info.error_message is not None


def test_scanned_image_only_pdf():
    """Verify that a PDF containing zero text characters alerts the user about OCR."""
    blank_pdf = create_blank_pdf(num_pages=1)
    doc_info = extract_text_from_pdf(blank_pdf, "scanned_invoice.pdf")

    assert doc_info.is_valid is False
    assert doc_info.character_count == 0
    assert doc_info.has_images_or_scanned_notice is True
    assert "scanned images" in doc_info.error_message.lower()
    assert "OCR is not supported" in doc_info.error_message


def test_file_size_limit_exceeded():
    """Verify that oversized files are rejected."""
    pdf_bytes = create_in_memory_pdf("Short text", num_pages=1)
    # Set max_file_size_mb to 0 so any file triggers limit
    doc_info = extract_text_from_pdf(pdf_bytes, "large.pdf", max_file_size_mb=0)
    assert doc_info.is_valid is False
    assert "exceeds the maximum allowed limit" in doc_info.error_message


def test_page_limit_exceeded():
    """Verify that documents exceeding the page count ceiling are caught."""
    pdf_bytes = create_in_memory_pdf("Text", num_pages=5)
    doc_info = extract_text_from_pdf(pdf_bytes, "long.pdf", max_pages=3)
    assert doc_info.is_valid is False
    assert "exceeds the limit of 3 pages" in doc_info.error_message


def test_character_limit_exceeded():
    """Verify that documents exceeding the character limit are rejected."""
    pdf_bytes = create_in_memory_pdf("A" * 500, num_pages=1)
    doc_info = extract_text_from_pdf(pdf_bytes, "verbose.pdf", max_chars=100)
    assert doc_info.is_valid is False
    assert "exceeds the supported limit of 100 characters" in doc_info.error_message


def test_validate_document_pair():
    """Verify pairing validation logic."""
    pdf_bytes_1 = create_in_memory_pdf("Doc A content", num_pages=1)
    pdf_bytes_2 = create_in_memory_pdf("Doc B content", num_pages=1)

    info_a = extract_text_from_pdf(pdf_bytes_1, "doc_a.pdf")
    info_b = extract_text_from_pdf(pdf_bytes_2, "doc_b.pdf")

    is_valid, err = validate_document_pair(info_a, info_b)
    assert is_valid is True
    assert err is None

    # Missing A
    is_valid_none, err_none = validate_document_pair(None, info_b)
    assert is_valid_none is False
    assert "Document A" in err_none

    # Combined char limit
    is_valid_lim, err_lim = validate_document_pair(info_a, info_b, max_total_chars=10)
    assert is_valid_lim is False
    assert "exceeds the supported comparison ceiling" in err_lim


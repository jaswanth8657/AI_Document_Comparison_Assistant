"""PDF Document Reader and Validation Module.

Extracts text from uploaded PDF files, conducts comprehensive integrity
checks, handles edge cases (scanned documents, empty files, encryption),
and tracks page-level citations.
"""

import io
import os
from typing import BinaryIO, Optional, Tuple, Union
import pypdf
from pypdf.errors import PdfReadError

from config import (
    MAX_CHARS_PER_DOC,
    MAX_FILE_SIZE_MB,
    MAX_PAGES_PER_DOC,
    MAX_TOTAL_CHARS,
)
from schemas import DocumentInfo, DocumentPage


def extract_text_from_pdf(
    file_input: Optional[Union[BinaryIO, bytes, io.BytesIO]],
    filename: str,
    max_file_size_mb: int = MAX_FILE_SIZE_MB,
    max_pages: int = MAX_PAGES_PER_DOC,
    max_chars: int = MAX_CHARS_PER_DOC,
) -> DocumentInfo:
    """Extracts text and page-level metadata from a PDF file with strict validation.
    
    Args:
        file_input: File stream or raw bytes of the PDF.
        filename: Original name of the uploaded file.
        max_file_size_mb: Upper limit for file size in megabytes.
        max_pages: Upper limit for total pages.
        max_chars: Upper limit for total extractable characters.
        
    Returns:
        DocumentInfo containing extraction status, text content, and page breakdown.
    """
    clean_filename = os.path.basename(filename or "Unnamed_Document.pdf")
    
    # 1. Missing file check
    if file_input is None:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message="No file was provided. Please upload a PDF document.",
        )
        
    # 2. File extension validation
    if not clean_filename.lower().endswith(".pdf"):
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"Unsupported file format for '{clean_filename}'. Only PDF (.pdf) files are supported.",
        )

    # Convert file_input to bytes
    try:
        if isinstance(file_input, bytes):
            raw_bytes = file_input
        elif hasattr(file_input, "getvalue"):
            raw_bytes = file_input.getvalue()
        elif hasattr(file_input, "read"):
            pos = file_input.tell() if hasattr(file_input, "tell") else None
            raw_bytes = file_input.read()
            # Reset pointer if possible
            if pos is not None and hasattr(file_input, "seek"):
                file_input.seek(pos)
        else:
            raw_bytes = bytes(file_input)
    except Exception as e:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"Failed to read file stream for '{clean_filename}': {str(e)}",
        )

    # 3. Zero-byte check
    file_size_bytes = len(raw_bytes)
    if file_size_bytes == 0:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"'{clean_filename}' is an empty file (0 bytes). Please upload a valid PDF.",
        )

    # 4. File size limit check
    max_bytes = max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        size_mb = file_size_bytes / (1024 * 1024)
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=(
                f"'{clean_filename}' is {size_mb:.1f} MB, which exceeds the maximum allowed "
                f"limit of {max_file_size_mb} MB."
            ),
        )

    # 5. PDF Header / Magic Bytes check
    if not raw_bytes.startswith(b"%PDF-"):
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=(
                f"'{clean_filename}' is not a valid PDF file. The file header does not match "
                "the standard PDF signature (%PDF-)."
            ),
        )

    # 6. Parse PDF using pypdf
    try:
        byte_stream = io.BytesIO(raw_bytes)
        reader = pypdf.PdfReader(byte_stream)
    except PdfReadError as e:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"'{clean_filename}' is corrupted or damaged and cannot be opened: {str(e)}",
        )
    except Exception as e:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"Unexpected error while opening '{clean_filename}': {str(e)}",
        )

    # 7. Encryption / Password protection check
    if reader.is_encrypted:
        try:
            # Check if decryptable with empty password (some PDFs are encrypted with blank password)
            decrypted = reader.decrypt("")
            if not decrypted:
                return DocumentInfo(
                    filename=clean_filename,
                    is_valid=False,
                    error_message=(
                        f"'{clean_filename}' is password-protected. Please remove password encryption "
                        "before uploading."
                    ),
                )
        except Exception:
            return DocumentInfo(
                filename=clean_filename,
                is_valid=False,
                error_message=(
                    f"'{clean_filename}' is password-protected or encrypted. Please upload an unprotected file."
                ),
            )

    # 8. Check page count
    try:
        total_pages = len(reader.pages)
    except Exception as e:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"Failed to read page tree of '{clean_filename}': {str(e)}",
        )

    if total_pages == 0:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=f"'{clean_filename}' contains zero pages. Please upload a PDF with content.",
        )

    # 9. Page limit check
    if total_pages > max_pages:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            error_message=(
                f"'{clean_filename}' contains {total_pages} pages, which exceeds the limit of "
                f"{max_pages} pages per document."
            ),
        )

    # 10. Extract text per page
    extracted_pages = []
    full_text_parts = []
    total_chars = 0

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        try:
            page_text = page.extract_text() or ""
        except Exception as e:
            page_text = f"[Warning: Text extraction failed on page {page_num}: {str(e)}]"
            
        clean_page_text = page_text.strip()
        page_chars = len(clean_page_text)
        total_chars += page_chars
        
        extracted_pages.append(
            DocumentPage(
                page_number=page_num,
                text=clean_page_text,
                character_count=page_chars,
            )
        )
        if clean_page_text:
            full_text_parts.append(f"--- Page {page_num} ---\n{clean_page_text}")

    full_text = "\n\n".join(full_text_parts).strip()
    word_count = len(full_text.split()) if full_text else 0

    # 11. Scanned document check (Zero readable text)
    if total_chars == 0:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            page_count=total_pages,
            character_count=0,
            word_count=0,
            has_images_or_scanned_notice=True,
            error_message=(
                f"'{clean_filename}' appears to contain only scanned images or unextractable text. "
                "OCR is not supported in the current version. No readable text could be analyzed."
            ),
        )

    # 12. Character limit check
    if total_chars > max_chars:
        return DocumentInfo(
            filename=clean_filename,
            is_valid=False,
            page_count=total_pages,
            character_count=total_chars,
            word_count=word_count,
            error_message=(
                f"'{clean_filename}' contains {total_chars:,} characters, which exceeds the supported "
                f"limit of {max_chars:,} characters per document."
            ),
        )

    return DocumentInfo(
        filename=clean_filename,
        is_valid=True,
        page_count=total_pages,
        character_count=total_chars,
        word_count=word_count,
        pages=extracted_pages,
        full_text=full_text,
        error_message=None,
        has_images_or_scanned_notice=False,
    )


def validate_document_pair(
    doc_a: Optional[DocumentInfo],
    doc_b: Optional[DocumentInfo],
    max_total_chars: int = MAX_TOTAL_CHARS,
) -> Tuple[bool, Optional[str]]:
    """Validates that two documents are ready for cross-comparison.
    
    Args:
        doc_a: Processed info for Document A.
        doc_b: Processed info for Document B.
        max_total_chars: Max allowed combined characters.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if doc_a is None or not doc_a.is_valid:
        err = doc_a.error_message if doc_a else "Document A has not been uploaded."
        return False, f"Document A Error: {err}"

    if doc_b is None or not doc_b.is_valid:
        err = doc_b.error_message if doc_b else "Document B has not been uploaded."
        return False, f"Document B Error: {err}"

    total_combined_chars = doc_a.character_count + doc_b.character_count
    if total_combined_chars > max_total_chars:
        return False, (
            f"The combined length of both documents ({total_combined_chars:,} characters) "
            f"exceeds the supported comparison ceiling of {max_total_chars:,} characters. "
            "Please upload shorter or excerpted versions."
        )

    return True, None

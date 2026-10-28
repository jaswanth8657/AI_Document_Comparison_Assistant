"""Automated test suite for comparison.py.

Tests Gemini API integration, prompt synthesis, mock model response handling,
schema validation, API error branches, and edge cases without making paid API calls.
"""

import json
from unittest.mock import MagicMock
import pytest
from google.genai import errors

from comparison import DocumentComparator, clean_json_response, build_comparison_prompt
from schemas import ComparisonResult, DocumentInfo, DocumentPage


@pytest.fixture
def sample_documents():
    """Provides a pair of processed DocumentInfo fixtures."""
    doc_a = DocumentInfo(
        filename="policy_2024.pdf",
        is_valid=True,
        page_count=2,
        character_count=500,
        word_count=80,
        pages=[
            DocumentPage(page_number=1, text="Tenure required: 6 months. Stipend: $500.", character_count=50),
            DocumentPage(page_number=2, text="Review date: December 15, 2024.", character_count=35),
        ],
        full_text="--- Page 1 ---\nTenure required: 6 months. Stipend: $500.\n\n--- Page 2 ---\nReview date: December 15, 2024.",
    )
    doc_b = DocumentInfo(
        filename="policy_2025.pdf",
        is_valid=True,
        page_count=2,
        character_count=550,
        word_count=90,
        pages=[
            DocumentPage(page_number=1, text="Tenure required: 3 months. Stipend: $750. Interns eligible.", character_count=65),
            DocumentPage(page_number=2, text="Review date: December 15, 2025.", character_count=35),
        ],
        full_text="--- Page 1 ---\nTenure required: 3 months. Stipend: $750. Interns eligible.\n\n--- Page 2 ---\nReview date: December 15, 2025.",
    )
    return doc_a, doc_b


@pytest.fixture
def mock_valid_json_payload():
    """Valid JSON payload matching ComparisonResult schema."""
    return {
        "document_a_summary": "Policy 2024 establishes remote work rules with 6-month tenure and a $500 stipend.",
        "document_b_summary": "Policy 2025 updates requirements with 3-month tenure, a $750 stipend, and intern eligibility.",
        "similarities": [
            {
                "topic": "Remote Work Authorization",
                "description": "Both policies govern remote work requirements.",
                "evidence_a": "Tenure required: 6 months",
                "evidence_b": "Tenure required: 3 months",
                "pages_a": [1],
                "pages_b": [1]
            }
        ],
        "differences": [
            {
                "topic": "Home Office Stipend",
                "change_type": "modified",
                "document_a_value": "$500",
                "document_b_value": "$750",
                "impact": "Increases employee equipment allowance by $250.",
                "evidence_a": "Stipend: $500",
                "evidence_b": "Stipend: $750",
                "pages_a": [1],
                "pages_b": [1]
            },
            {
                "topic": "Intern Eligibility",
                "change_type": "added",
                "document_a_value": "Not found in the provided text.",
                "document_b_value": "Interns eligible.",
                "impact": "Expands allowance access to interns.",
                "evidence_a": "Not found in the provided text.",
                "evidence_b": "Interns eligible.",
                "pages_a": [],
                "pages_b": [1]
            }
        ],
        "key_details": [
            {
                "field": "Review Date",
                "document_a_value": "December 15, 2024",
                "document_b_value": "December 15, 2025",
                "status": "changed",
                "evidence_a": "December 15, 2024",
                "evidence_b": "December 15, 2025",
                "pages_a": [2],
                "pages_b": [2]
            },
            {
                "field": "Gym Membership",
                "document_a_value": "Not found in the provided text.",
                "document_b_value": "Not found in the provided text.",
                "status": "same",
                "evidence_a": "",
                "evidence_b": "",
                "pages_a": [],
                "pages_b": []
            }
        ],
        "overall_conclusion": "Policy 2025 broadens eligibility and increases stipends compared to 2024.",
        "limitations": [
            "Both documents are brief policy excerpts."
        ]
    }


def test_clean_json_response_with_markdown_blocks():
    """Verify clean_json_response strips markdown json fences."""
    fenced = '```json\n{"test": 123}\n```'
    assert clean_json_response(fenced) == '{"test": 123}'

    bare = '{"test": 123}'
    assert clean_json_response(bare) == '{"test": 123}'


def test_build_comparison_prompt(sample_documents):
    """Verify prompt formatting isolates documents and includes page markers."""
    doc_a, doc_b = sample_documents
    prompt = build_comparison_prompt(doc_a, doc_b)

    assert "DOCUMENT A: policy_2024.pdf" in prompt
    assert "DOCUMENT B: policy_2025.pdf" in prompt
    assert "--- Page 1 ---" in prompt
    assert "Tenure required: 6 months" in prompt
    assert "COMPARISON TASK & SECTIONS REQUIRED" in prompt


def test_successful_mock_comparison(sample_documents, mock_valid_json_payload):
    """Verify successful comparison with a mocked Gemini client."""
    doc_a, doc_b = sample_documents

    # Mock response object
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(mock_valid_json_payload)

    # Mock client
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    comparator = DocumentComparator(
        api_key="test-api-key",
        model_name="gemini-2.5-flash",
        client_override=mock_client,
    )

    result = comparator.compare(doc_a, doc_b)

    assert isinstance(result, ComparisonResult)
    assert result.doc_a_name == "policy_2024.pdf"
    assert result.doc_b_name == "policy_2025.pdf"
    assert len(result.similarities) == 1
    assert len(result.differences) == 2
    assert result.differences[0].change_type == "modified"
    assert result.differences[1].change_type == "added"
    assert len(result.key_details) == 2
    assert result.key_details[0].status == "changed"
    assert result.key_details[1].document_a_value == "Not found in the provided text."


def test_missing_api_key_raises_error(sample_documents):
    """Verify that calling compare without an API key raises ValueError."""
    doc_a, doc_b = sample_documents
    comparator = DocumentComparator(api_key="")

    with pytest.raises(ValueError, match="Gemini API Key is missing"):
        comparator.compare(doc_a, doc_b)


def test_malformed_json_response_handling(sample_documents):
    """Verify that unparseable model response raises an informative RuntimeError."""
    doc_a, doc_b = sample_documents

    mock_resp = MagicMock()
    mock_resp.text = "This is not valid JSON at all!"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    comparator = DocumentComparator(
        api_key="test-api-key",
        client_override=mock_client,
    )

    with pytest.raises(RuntimeError, match="Failed to parse AI response as valid JSON"):
        comparator.compare(doc_a, doc_b)


def test_schema_validation_failure(sample_documents):
    """Verify that JSON missing mandatory fields raises a schema contract error."""
    doc_a, doc_b = sample_documents

    # Missing document_a_summary and overall_conclusion
    invalid_data = {
        "similarities": [],
        "differences": [],
    }

    mock_resp = MagicMock()
    mock_resp.text = json.dumps(invalid_data)

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    comparator = DocumentComparator(
        api_key="test-api-key",
        client_override=mock_client,
    )

    with pytest.raises(RuntimeError, match="did not meet the required schema contract"):
        comparator.compare(doc_a, doc_b)


def test_api_rate_limit_error(sample_documents):
    """Verify handling of 429 / RESOURCE_EXHAUSTED errors."""
    doc_a, doc_b = sample_documents

    mock_client = MagicMock()
    api_err = errors.APIError(code=429, response_json={"error": {"message": "RESOURCE_EXHAUSTED: Quota exceeded"}})
    mock_client.models.generate_content.side_effect = api_err

    comparator = DocumentComparator(
        api_key="test-api-key",
        client_override=mock_client,
    )

    with pytest.raises(RuntimeError, match="rate limit or quota exceeded"):
        comparator.compare(doc_a, doc_b)


def test_api_permission_denied_error(sample_documents):
    """Verify handling of 403 / API_KEY_INVALID errors."""
    doc_a, doc_b = sample_documents

    mock_client = MagicMock()
    api_err = errors.APIError(code=403, response_json={"error": {"message": "PERMISSION_DENIED: API_KEY_INVALID"}})
    mock_client.models.generate_content.side_effect = api_err

    comparator = DocumentComparator(
        api_key="test-api-key",
        client_override=mock_client,
    )

    with pytest.raises(RuntimeError, match="Invalid or unauthorized Gemini API key"):
        comparator.compare(doc_a, doc_b)


def test_combined_length_limit(sample_documents):
    """Verify that combined document length limit is enforced."""
    doc_a, doc_b = sample_documents
    doc_a.character_count = 100_000
    doc_b.character_count = 100_000  # Combined 200,000 > MAX_TOTAL_CHARS (120,000)

    comparator = DocumentComparator(api_key="test-key")
    with pytest.raises(ValueError, match="exceeds the processing limit"):
        comparator.compare(doc_a, doc_b)

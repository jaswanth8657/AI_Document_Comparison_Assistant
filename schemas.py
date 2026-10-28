"""Data schemas and Pydantic models for the AI Document Comparison Assistant.

Defines validated structures for document metadata, extraction outputs,
and AI-generated comparison results.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SimilarityItem(BaseModel):
    """Represents a similarity point found between both documents."""
    topic: str = Field(description="Short title of the common topic or policy rule.")
    description: str = Field(description="Explanation of what both documents agree on or share.")
    evidence_a: str = Field(default="", description="Supporting excerpt from Document A.")
    evidence_b: str = Field(default="", description="Supporting excerpt from Document B.")
    pages_a: List[int] = Field(default_factory=list, description="Page numbers where evidence appears in Document A.")
    pages_b: List[int] = Field(default_factory=list, description="Page numbers where evidence appears in Document B.")


ChangeType = Literal["added", "removed", "modified", "contradiction", "wording_only"]


class DifferenceItem(BaseModel):
    """Represents a meaningful difference between the two documents."""
    topic: str = Field(description="Specific topic or clause where the difference occurs.")
    change_type: ChangeType = Field(description="Category of change: added, removed, modified, contradiction, or wording_only.")
    document_a_value: str = Field(description="Exact value or statement in Document A (or 'Not present in Document A').")
    document_b_value: str = Field(description="Exact value or statement in Document B (or 'Not present in Document B').")
    impact: str = Field(default="", description="Practical consequence or significance of this difference.")
    evidence_a: str = Field(default="", description="Supporting quote or excerpt from Document A.")
    evidence_b: str = Field(default="", description="Supporting quote or excerpt from Document B.")
    pages_a: List[int] = Field(default_factory=list, description="Page numbers where evidence appears in Document A.")
    pages_b: List[int] = Field(default_factory=list, description="Page numbers where evidence appears in Document B.")


KeyDetailStatus = Literal["same", "changed", "only_in_a", "only_in_b", "unclear"]


class KeyDetailItem(BaseModel):
    """Represents a comparison of specific key facts (dates, fees, requirements, etc.)."""
    field: str = Field(description="Category/Field name (e.g., 'Core Working Hours', 'Equipment Stipend', 'Reimbursement Window').")
    document_a_value: str = Field(description="Value in Document A or 'Not found in the provided text.'")
    document_b_value: str = Field(description="Value in Document B or 'Not found in the provided text.'")
    status: KeyDetailStatus = Field(description="Comparison status: same, changed, only_in_a, only_in_b, or unclear.")
    evidence_a: str = Field(default="", description="Supporting text from Document A.")
    evidence_b: str = Field(default="", description="Supporting text from Document B.")
    pages_a: List[int] = Field(default_factory=list, description="Page numbers in Document A.")
    pages_b: List[int] = Field(default_factory=list, description="Page numbers in Document B.")


class ComparisonResult(BaseModel):
    """Complete structured output contract for document comparison."""
    document_a_summary: str = Field(description="Comprehensive, factual summary of Document A.")
    document_b_summary: str = Field(description="Comprehensive, factual summary of Document B.")
    similarities: List[SimilarityItem] = Field(default_factory=list, description="List of common elements and shared rules.")
    differences: List[DifferenceItem] = Field(default_factory=list, description="List of meaningful differences and modifications.")
    key_details: List[KeyDetailItem] = Field(default_factory=list, description="Side-by-side comparison of specific factual fields.")
    overall_conclusion: str = Field(description="Neutral, objective conclusion highlighting the primary shift between documents.")
    limitations: List[str] = Field(default_factory=list, description="Explicit notes on missing details, unreadable sections, or uncertainties.")
    
    # Metadata attributes (populated by application)
    doc_a_name: str = Field(default="", description="Filename of Document A.")
    doc_b_name: str = Field(default="", description="Filename of Document B.")
    timestamp: str = Field(default="", description="ISO formatted or readable timestamp of comparison.")
    model_used: str = Field(default="", description="Gemini model identifier used for comparison.")


class DocumentPage(BaseModel):
    """Page-level extraction details for citation tracing."""
    page_number: int
    text: str
    character_count: int


class DocumentInfo(BaseModel):
    """Inspection and validation results of a processed PDF file."""
    filename: str
    is_valid: bool
    page_count: int = 0
    character_count: int = 0
    word_count: int = 0
    pages: List[DocumentPage] = Field(default_factory=list)
    full_text: str = ""
    error_message: Optional[str] = None
    has_images_or_scanned_notice: bool = False

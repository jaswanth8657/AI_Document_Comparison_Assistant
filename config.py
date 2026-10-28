"""Configuration settings for the AI Document Comparison Assistant.

Loads environment variables from .env and defines runtime constants and limits.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini Model Configuration
# Dedicated supported model for Google GenAI SDK
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY_ENV = os.getenv("GEMINI_API_KEY", "")

# Supported Models List (Only gemini-2.5-flash is supported)
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
]

# Processing Limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "15"))
MAX_PAGES_PER_DOC = int(os.getenv("MAX_PAGES_PER_DOC", "50"))
MAX_CHARS_PER_DOC = int(os.getenv("MAX_CHARS_PER_DOC", "60000"))
MAX_TOTAL_CHARS = int(os.getenv("MAX_TOTAL_CHARS", "120000"))

# Generation parameters
DEFAULT_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
DEFAULT_TOP_P = float(os.getenv("GEMINI_TOP_P", "0.95"))

# Application Metadata
APP_TITLE = "AI Document Comparison Assistant"
APP_SUBTITLE = "Upload two text-based PDF documents to extract content, generate summaries, identify meaningful similarities and differences, and download a professional report."
APP_DISCLAIMER = (
    "Disclaimer: This application is an informational document-analysis tool. "
    "It does not provide legal advice and does not determine legal validity, compliance, or equivalence."
)


def get_gemini_api_key(user_provided_key: Optional[str] = None) -> str:
    """Retrieve the Gemini API key from user input or environment variable.
    
    User-provided input from the UI takes priority over .env for flexibility.
    """
    if user_provided_key and user_provided_key.strip():
        return user_provided_key.strip()
    return GEMINI_API_KEY_ENV.strip()


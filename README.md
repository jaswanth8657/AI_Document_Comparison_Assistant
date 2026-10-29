# AI Document Comparison Assistant

A Streamlit application for comparing two text-based PDF documents using Google Gemini. It extracts page-labelled text using `pypdf`, summarizes both documents, identifies similarities and differences with supporting evidence, compares key details, and exports a formatted DOCX report.

## Features

- Upload and validate two PDF files.
- Preview extracted text and page/character counts.
- Generate separate document summaries.
- Identify similarities, additions, removals, modifications, and contradictions based on extracted text.
- Compare dates, amounts, eligibility requirements, names, and other important details.
- Display evidence excerpts and page references where available.
- Download a DOCX comparison report.
- Handle invalid PDFs, missing inputs, unreadable/scanned PDFs, size limits, and API errors.

## Technology

- Python
- Streamlit
- Google GenAI Python SDK (`google-genai`)
- `pypdf`
- `python-dotenv`
- Pydantic
- `python-docx`
- pytest

## Setup on Windows

1. Install Python 3.11+ and Git.
2. Clone the repository:

   ```bash
   git clone https://github.com/jaswanth8657/AI_Document_Comparison_Assistant.git
   cd AI_Document_Comparison_Assistant
   ```

3. Create and activate a virtual environment:

   ```bat
   py -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Configure a Gemini API key using `.env` (copy `.env.example` to `.env`) or use the app's sidebar key input if enabled. Never commit `.env` or share the key.
6. Run the app:

   ```bat
   python -m streamlit run app.py
   ```

## Sample demo

Use `sample_documents/policy_v1.pdf` and `sample_documents/policy_v2.pdf` to try the app. The sample policies intentionally include changed details for demonstration.

## Tests

Run `pytest -q` from the project root. Unit tests should mock external AI calls; a real Gemini API key is only needed for a manual integration test.

## Limitations and privacy

- Scanned/image-only PDFs are not OCR processed in this version.
- Complex tables and diagrams may not extract perfectly.
- Document text submitted for comparison is sent to the configured Gemini API; only upload documents you are authorized to share.
- AI findings should be checked against the original PDFs. This tool is informational and does not determine legal validity or compliance.

## Project structure

```text
app.py
comparison.py
document_reader.py
report_generator.py
requirements.txt
.env.example
.gitignore
run_windows.bat
sample_documents/
tests/
```

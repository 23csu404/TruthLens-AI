
# TruthLens AI
### Turning Documents into Verified Knowledge

**Live Demo:** https://truthlens-ai-23csu404.streamlit.app/

**GitHub Repository:** https://github.com/23csu404/TruthLens-AI

TruthLens AI is an AI-powered fact-checking web application that analyses PDF documents, extracts verifiable factual claims, searches the live web for supporting evidence, and generates evidence-based verification reports.

## Features

- **PDF Text Extraction:** Extracts readable text from uploaded PDF documents using PyMuPDF.
- **AI Claim Detection:** Uses Google Gemini to identify factual claims, including statistics, dates, historical information, and technical or financial figures.
- **Live Web Research:** Uses Tavily Search API to retrieve relevant online evidence for each claim.
- **Batch Fact Verification:** Analyses multiple claims and their retrieved evidence in a single Gemini request.
- **Four Verification Categories:**
  - Verified
  - Inaccurate
  - False
  - Insufficient Evidence
- **Evidence Display:** Displays retrieved source links alongside individual claim results.
- **Report Export:** Allows users to download the fact-checking results as a CSV file.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming Language | Python |
| PDF Processing | PyMuPDF |
| Claim Extraction | Google Gemini API |
| Web Search | Tavily API |
| Verification | Google Gemini API |
| Data Processing | Pandas |

## Project Structure

```text
TruthLens_AI/
│
├── app.py
├── extractor.py
├── claim_detector.py
├── web_search.py
├── verifier.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env
```

The `.env` file contains private API credentials and must not be uploaded to GitHub.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd TruthLens_AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API credentials

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Obtain credentials from:

- Google AI Studio: https://aistudio.google.com/
- Tavily: https://tavily.com/

Never share or commit API keys.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Application Workflow

1. User uploads a PDF document.
2. PyMuPDF extracts readable document text.
3. Gemini identifies individual factual claims.
4. Tavily performs live web searches for the extracted claims.
5. Search results are collected and passed to Gemini for batch analysis.
6. Each claim receives a verification verdict and explanation.
7. The application displays available source links and corrected facts.
8. Users can download the final report in CSV format.

## Verification Approach

TruthLens AI uses four verdict categories:

- **Verified:** Retrieved evidence supports the claim.
- **Inaccurate:** The claim is outdated, partially correct, misleading, or missing important context.
- **False:** Reliable evidence directly contradicts the claim.
- **Insufficient Evidence:** Available evidence is inadequate to establish accuracy.

Absence of evidence is not automatically treated as proof that a claim is false.

## Limitations

- Scanned PDFs without a readable text layer may require OCR.
- Verification quality depends on search-result relevance and source reliability.
- AI-generated explanations and corrections should be checked against the original sources.
- API availability, rate limits, and usage quotas may affect processing.

## Future Improvements

- OCR support for scanned documents.
- Source credibility ranking.
- Improved identification of outdated statistics.
- PDF report export.
- Claim-level confidence indicators.
- Support for larger documents and multilingual content.

## Project Purpose

TruthLens AI aims to improve the reliability of information in documents by combining AI-based claim extraction, live web research, and evidence-based verification.

**TruthLens AI — Turning Documents into Verified Knowledge.**

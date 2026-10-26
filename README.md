# AIDOCUMENTCOMPARISONASSISTANT
AI Document Comparison Assistant – Description  The AI Document Comparison Assistant is an application that compares two PDF documents using Artificial Intelligence. It finds similarities, differences, and missing information between the documents.  Technologies Used: Python, Streamlit, AI/LLM, PyPDF, HTML, and CSS.
# AI Document Comparison Assistant

## Project Description
The AI Document Comparison Assistant is a Python-based application that compares two PDF documents using Artificial Intelligence. It identifies similarities, differences, and missing or changed information between the documents. It helps users compare documents easily and saves time.

## Features
- Upload two PDF documents.
- Extract text from PDF files.
- Compare documents using AI.
- Identify similarities and differences.
- Find missing or changed information.
- Display comparison results in a simple interface.
- Generate a comparison report.

## Technologies Used
- Python
- Streamlit
- Artificial Intelligence (AI)
- Large Language Models (LLMs)
- PyPDF
- HTML and CSS

## Installation

1. Clone or download the project.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate the environment on Windows:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

6. Configure your AI API key if required by the application.

## How to Run

Run the following command in the terminal:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal to use the application.

## How to Use
1. Open the application.
2. Upload the first PDF document.
3. Upload the second PDF document.
4. Click the compare button.
5. View the similarities, differences, and missing information.
6. Generate or download the comparison report if supported.

## Project Structure

```text
AI-Document-Comparison-Assistant/
├── app.py
├── document_reader.py
├── comparison.py
├── report_generator.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── sample_documents/
```

*Note: The project structure may vary depending on your implementation.*

## Objective
The main objective of this project is to make document comparison faster, easier, and more efficient with the help of Artificial Intelligence.

## Future Enhancements
- Support for Word documents.
- Improved comparison accuracy.
- Highlight differences between documents.
- Export detailed reports as PDF.
- Add support for scanned documents using OCR.

## Conclusion
The AI Document Comparison Assistant reduces manual work by automatically comparing two documents and presenting the important differences in an easy-to-understand format.

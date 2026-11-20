
import fitz


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF document.
    """

    try:
        pdf_document = fitz.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        )

        extracted_text = ""

        for page_number, page in enumerate(pdf_document):
            page_text = page.get_text()
            extracted_text += (
                f"\n--- Page {page_number + 1} ---\n"
                + page_text
            )

        pdf_document.close()

        if not extracted_text.strip():
            return None

        return extracted_text

    except Exception as error:
        print(f"PDF extraction error: {error}")
        return None

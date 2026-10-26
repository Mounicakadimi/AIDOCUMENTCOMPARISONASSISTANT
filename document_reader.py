
import io
from pypdf import PdfReader


def extract_pdf_text(data: bytes) -> str:
    """Extract readable text from a PDF document."""

    try:
        reader = PdfReader(io.BytesIO(data), strict=True)
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if text:
                pages.append(f"[Page {page_number}]\n{text}")

        extracted_text = "\n\n".join(pages).strip()

        if not extracted_text:
            raise ValueError(
                "No readable text found. This PDF may be scanned "
                "or image-only. OCR is required."
            )

        return extracted_text

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            f"Could not read the PDF. It may be damaged or "
            f"password-protected: {error}"
        )

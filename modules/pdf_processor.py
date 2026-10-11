import pymupdf


def extract_pdf_text(pdf_path):
    """
    Extract selectable text from a PDF.

    Scanned/image-only PDFs are not supported.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text("text").strip()

        if text:
            pages.append({
                "page": page_number + 1,
                "text": text
            })

    document.close()

    return pages

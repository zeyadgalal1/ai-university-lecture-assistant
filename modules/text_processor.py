import re


def clean_text(text):
    """
    Clean unnecessary whitespace from text.
    """

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def chunk_text(text, chunk_size=800, overlap=100):
    """
    Split text into overlapping chunks.
    """

    text = clean_text(text)

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        if end >= len(text):
            break

        start = end - overlap

    return chunks
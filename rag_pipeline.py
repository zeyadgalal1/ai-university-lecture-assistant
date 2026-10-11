from modules.text_processor import chunk_text
from modules.vector_store import (
    clear_collection,
    add_documents
)
from api_client import create_embeddings


def build_lecture_text(
    transcription_result,
    pdf_pages
):
    """
    Combine the lecture transcript and optional PDF
    into one text source.
    """

    texts = []

    # --------------------------------------------------------
    # Add transcript
    # --------------------------------------------------------

    segments = transcription_result.get(
        "segments",
        []
    )

    for segment in segments:

        text = segment.get(
            "text",
            ""
        ).strip()

        if text:
            texts.append(text)

    # --------------------------------------------------------
    # Add optional PDF
    # --------------------------------------------------------

    for page in pdf_pages:

        text = page.get(
            "text",
            ""
        ).strip()

        if text:
            texts.append(text)

    return "\n\n".join(texts)


def process_lecture(
    transcription_result,
    pdf_pages
):
    """
    Process the lecture and create the local
    ChromaDB knowledge base.

    Flow:

    Transcript + PDF
            ↓
        Clean/chunk
            ↓
        BGE-M3 embeddings
            ↓
        ChromaDB
    """

    # --------------------------------------------------------
    # 1. Combine lecture sources
    # --------------------------------------------------------

    lecture_text = build_lecture_text(
        transcription_result,
        pdf_pages
    )

    if not lecture_text.strip():

        raise ValueError(
            "No lecture text was found."
        )

    # --------------------------------------------------------
    # 2. Split into chunks
    # --------------------------------------------------------

    chunks = chunk_text(
        lecture_text,
        chunk_size=800,
        overlap=100
    )

    if not chunks:

        raise ValueError(
            "Could not create lecture chunks."
        )

    # --------------------------------------------------------
    # 3. Clear previous lecture
    # --------------------------------------------------------

    clear_collection()

    # --------------------------------------------------------
    # 4. Generate embeddings using BGE-M3
    #    on the Kaggle GPU backend
    # --------------------------------------------------------

    embedding_result = create_embeddings(
        chunks
    )

    if not embedding_result.get(
        "success",
        False
    ):

        raise RuntimeError(
            embedding_result.get(
                "error",
                "Embedding generation failed."
            )
        )

    embeddings = embedding_result[
        "embeddings"
    ]

    # --------------------------------------------------------
    # 5. Create metadata
    # --------------------------------------------------------

    metadatas = []

    for i in range(len(chunks)):

        metadatas.append(
            {
                "chunk_id": i,
                "source": "lecture"
            }
        )

    # --------------------------------------------------------
    # 6. Store chunks + embeddings
    #    inside local ChromaDB
    # --------------------------------------------------------

    add_documents(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "success": True,
        "chunks": len(chunks)
    }

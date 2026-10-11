from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ==============================
# Configuration
# ==============================

EMBEDDING_MODEL = "BAAI/bge-m3"

CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "lecture_assistant"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


# ==============================
# Embedding Model
# ==============================

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)


# ==============================
# ChromaDB
# ==============================

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)


# ==============================
# Text Splitter
# ==============================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        "? ",
        "! ",
        " ",
        ""
    ]
)


# ==============================
# Create Lecture Documents
# ==============================

def create_documents(
    transcript,
    pdf_text=""
):

    documents = []

    if transcript.strip():

        transcript_document = Document(
            page_content=transcript,
            metadata={
                "source": "transcript"
            }
        )

        documents.append(transcript_document)

    if pdf_text.strip():

        pdf_document = Document(
            page_content=pdf_text,
            metadata={
                "source": "pdf"
            }
        )

        documents.append(pdf_document)

    return documents


# ==============================
# Split Lecture
# ==============================

def split_documents(documents):

    chunks = text_splitter.split_documents(
        documents
    )

    return chunks


# ==============================
# Store Lecture
# ==============================

def index_lecture(
    transcript,
    pdf_text=""
):

    documents = create_documents(
        transcript,
        pdf_text
    )

    chunks = split_documents(
        documents
    )

    if not chunks:
        return 0

    # Remove previous lecture data
    try:
        existing = vector_store.get()

        ids = existing.get("ids", [])

        if ids:
            vector_store.delete(
                ids=ids
            )

    except Exception:
        pass

    vector_store.add_documents(
        documents=chunks
    )

    return len(chunks)


# ==============================
# Retrieve Relevant Chunks
# ==============================

def retrieve_lecture_context(
    query,
    k=6
):

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


# ==============================
# Convert Results to Text
# ==============================

def build_context(
    documents
):

    if not documents:
        return ""

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        source = document.metadata.get(
            "source",
            "lecture"
        )

        context_parts.append(
            f"""
--- Lecture Chunk {index} ---
Source: {source}

{document.page_content}
"""
        )

    return "\n".join(
        context_parts
    )
    
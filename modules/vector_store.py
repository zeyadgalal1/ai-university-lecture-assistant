import chromadb


# Persistent local ChromaDB database
client = chromadb.PersistentClient(
    path="chroma_db"
)


collection = client.get_or_create_collection(
    name="lecture_knowledge"
)


def clear_collection():
    """
    Delete all existing lecture data.
    """

    global collection

    client.delete_collection(
        name="lecture_knowledge"
    )

    collection = client.get_or_create_collection(
        name="lecture_knowledge"
    )


def add_documents(
    documents,
    embeddings,
    metadatas=None
):
    """
    Add lecture chunks and their embeddings to ChromaDB.
    """

    if not documents:
        return

    ids = [
        f"chunk_{i}"
        for i in range(len(documents))
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search_documents(
    query_embedding,
    n_results=5
):
    """
    Retrieve the most relevant lecture chunks.
    """

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results
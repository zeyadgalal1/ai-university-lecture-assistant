from api_client import create_embeddings, generate_answer

from modules.prompts import (
    SYSTEM_PROMPT,
    build_explanation_prompt,
    build_important_points_prompt,
    build_exam_questions_prompt,
    build_revision_prompt
)

from modules.vector_store import search_documents


def get_embedding(text):
    """
    Generate an embedding for a single text
    using BGE-M3 on the Kaggle GPU.
    """

    result = create_embeddings([text])

    return result["embeddings"][0]


def retrieve_context(question, n_results=5):
    """
    Retrieve the most relevant lecture chunks
    from ChromaDB.
    """

    query_embedding = get_embedding(question)

    results = search_documents(
        query_embedding,
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]

    return "\n\n".join(documents)


def generate_explanation(question):
    """
    Answer a student's question using RAG.
    """

    context = retrieve_context(question)

    prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + build_explanation_prompt(
            context,
            question
        )
    )

    result = generate_answer(
        prompt,
        max_new_tokens=700,
        temperature=0.3
    )

    return result["answer"]


def generate_important_points():
    """
    Generate important lecture points.
    """

    context = retrieve_context(
        "What are the most important points in this lecture?"
    )

    prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + build_important_points_prompt(context)
    )

    result = generate_answer(
        prompt,
        max_new_tokens=700,
        temperature=0.2
    )

    return result["answer"]


def generate_exam_questions():
    """
    Generate exam-style questions.
    """

    context = retrieve_context(
        "What topics and concepts should I study for the exam?"
    )

    prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + build_exam_questions_prompt(context)
    )

    result = generate_answer(
        prompt,
        max_new_tokens=900,
        temperature=0.4
    )

    return result["answer"]


def generate_revision():
    """
    Generate a revision summary.
    """

    context = retrieve_context(
        "Give me the complete important information I need for revision."
    )

    prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + build_revision_prompt(context)
    )

    result = generate_answer(
        prompt,
        max_new_tokens=900,
        temperature=0.3
    )

    return result["answer"]
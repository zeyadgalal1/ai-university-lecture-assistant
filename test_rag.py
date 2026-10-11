from api_client import transcribe_file
from modules.rag_pipeline import (
    index_lecture,
    retrieve_lecture_context,
    build_context,
)

# Your lecture recording

audio_path = r"C:\Users\Lenovo\Downloads\lecture_chunks"

# STEP 1: Transcribe the audio using Faster-Whisper on Kaggle
print("=" * 60)
print("STEP 1: TRANSCRIBING LECTURE")
print("=" * 60)

result = transcribe_file(audio_path)

transcript = "\n".join(
    segment["text"]
    for segment in result["segments"]
    if segment.get("text", "").strip()
)

print("Detected language:", result["language"])
print("Language probability:", result["language_probability"])
print("Transcript characters:", len(transcript))
print("\nTranscript preview (first 1500 characters):\n")
print(transcript[:1500])

if not transcript.strip():
    raise ValueError(
        "No transcript was returned. Check the audio file and transcription API."
    )


# STEP 2: Store the transcript in ChromaDB
print("\n" + "=" * 60)
print("STEP 2: INDEXING TRANSCRIPT IN CHROMADB")
print("=" * 60)

number_of_chunks = index_lecture(
    transcript=transcript,
    pdf_text=""
)

print("Chunks created:", number_of_chunks)

if number_of_chunks == 0:
    raise ValueError("No chunks were created from the transcript.")


# STEP 3: Search for relevant lecture content
print("\n" + "=" * 60)
print("STEP 3: RETRIEVING RELEVANT CONTENT")
print("=" * 60)

query = "Explain the main topic and important concepts of the Zener diode lecture."

results = retrieve_lecture_context(
    query=query,
    k=6
)

context = build_context(results)

print("\n===== RETRIEVED LECTURE CONTEXT =====\n")

if context.strip():
    print(context)
else:
    print("No relevant lecture content was retrieved.")


# STEP 4: Summary of the test
print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
print("Audio transcription: SUCCESS")
print("ChromaDB indexing: SUCCESS")
print("Context retrieval:", "SUCCESS" if context.strip() else "NO RESULTS")
print("\nNote: This test does not generate a Qwen answer yet.")


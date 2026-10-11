# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> 🎓 This project was built during the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field            | Value                                          |
| ---------------- | ---------------------------------------------- |
| Full Name        | Zeyad Galal                                    |
| Project Name     | AI University Lecture Assistant                |
| GitHub Username  | [@zeyadgalal1](https://github.com/zeyadgalal1) |
| Internship Batch | August–October 2026                            |
| Training Program | Large Language Models (LLMs) Program           |
| Organization     | [**Edrak for AI**](https://edrak4ai.com/en)    |

---

# 📖 Project Overview

**AI University Lecture Assistant** is an AI-powered application designed to help university students understand lectures and prepare for exams more efficiently.

Students can upload lecture recordings, which are transcribed and processed to generate structured explanations and study materials. An optional digital PDF containing selectable text can also provide additional context.

The project is designed for different university disciplines, including engineering, medicine, business, and mathematics. It also aims to handle Arabic lectures containing English technical terminology, depending on audio and transcription quality.

The application combines speech recognition, Retrieval-Augmented Generation (RAG), vector search, and large language models to turn lecture materials into useful learning resources.

---

# ✨ Features

* 🎙️ **Lecture Transcription:** Converts lecture recordings into text using Faster-Whisper with the `large-v3` model.
* 🎞️ **Multiple Recording Formats:** Supports MP3, MP4, and OGG uploads.
* 🌍 **Multilingual Lecture Support:** Designed for Arabic speech mixed with English technical terminology.
* 📄 **Optional PDF Support:** Extracts selectable text from PDF documents using PyMuPDF. Scanned PDFs requiring OCR are not supported.
* 🧠 **AI-Powered Explanations:** Uses Qwen2.5-7B-Instruct to generate structured explanations and study notes.
* 🎯 **Important Concepts:** Helps identify key concepts and potentially exam-relevant points mentioned in the lecture.
* 🔎 **Semantic Retrieval:** Uses BGE-M3 embeddings and ChromaDB to retrieve relevant lecture content.
* 📚 **Revision on Demand:** Generates revision material when the student requests it.
* 🖥️ **Interactive Interface:** Provides a Streamlit interface for uploading lecture materials and viewing results.
* 🔒 **Lecture-Based Responses:** Designed to use the uploaded recording and optional PDF rather than external web research.

---

# 🛠️ Technologies Used

| Technology                  | Purpose                                          |
| --------------------------- | ------------------------------------------------ |
| Python                      | Main programming language                        |
| Streamlit                   | User interface                                   |
| FastAPI                     | Backend API for model inference                  |
| Faster-Whisper (`large-v3`) | Lecture transcription                            |
| Qwen2.5-7B-Instruct         | Lecture explanations and revision generation     |
| 4-bit NF4 Quantization      | Reduces language-model memory requirements       |
| LangChain                   | Supports retrieval and text-processing workflows |
| BGE-M3                      | Creates semantic text embeddings                 |
| ChromaDB                    | Stores and retrieves vector embeddings           |
| PyMuPDF                     | Extracts selectable text from PDFs               |
| FFmpeg                      | Audio processing and conversion                  |
| Requests                    | Frontend-to-backend HTTP communication           |
| Kaggle GPU                  | Development environment for model inference      |
| ngrok                       | Exposes the development backend through a tunnel |
| Git and GitHub              | Version control and project hosting              |

### System Architecture

```text
Lecture Recording             Optional PDF
(MP3 / MP4 / OGG)             (Selectable Text)
       |                            |
       v                            v
     FFmpeg                      PyMuPDF
       |                            |
       v                            |
Faster-Whisper                     |
       |                            |
       v                            v
   Transcript + PDF Text
             |
             v
     Text Processing
      and Chunking
             |
             v
      BGE-M3 Embeddings
             |
             v
          ChromaDB
             |
             v
      FastAPI Backend
       (Kaggle GPU)
             |
             v
    Qwen2.5-7B-Instruct
             |
       +-----+------+
       |            |
       v            v
Lecture Analysis  Revision
                   (On Demand)
       |            |
       +-----+------+
             |
             v
     Streamlit Interface
```

---

# ⚙️ Installation

## Prerequisites

Make sure you have:

* Python installed.
* Git installed.
* FFmpeg installed and available in your system `PATH`.
* A configured Kaggle GPU notebook running the FastAPI backend.
* ngrok configured to expose the backend during development.

## 1. Clone the Repository

```bash
git clone https://github.com/zeyadgalal1/ai-university-lecture-assistant.git
cd ai-university-lecture-assistant
```

## 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure the Backend

Start the FastAPI model backend in your Kaggle GPU notebook and establish the ngrok tunnel.

Configure the frontend with your active backend URL according to the settings supported by your `api_client.py` file. Replace any example URL with your actual ngrok URL.

## 5. Run the Application

From the project directory, run:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

**Note:** The backend must be running and accessible for lecture processing to work.

---

# 🚀 Usage

1. Open the application in your browser.
2. Upload a lecture recording in a supported format.
3. Optionally upload a PDF containing selectable text.
4. Process the recording to generate a transcript.
5. Review the transcript and available lecture content.
6. Select the lecture-analysis action to generate explanations and study material.
7. Review the important concepts identified from the lecture.
8. Select the revision action when you are ready to generate revision material.

The application is designed to base its output on the uploaded lecture materials. Revision content is generated on demand when requested by the student.

---

# 📸 Demo

Watch the demonstration video to see the AI University Lecture Assistant interface and workflow.

🎥 **[Watch the Lecture Assistant Demo Video](demo/video_AI_compressed.mp4)**

**GitHub Repository:** [zeyadgalal1/ai-university-lecture-assistant](https://github.com/zeyadgalal1/ai-university-lecture-assistant)

> **Important:** Make sure the video filename and path above match the actual file in your `demo` folder.

---

# 📈 Results

The project brings several AI technologies together in a single university study workflow.

* Converts lecture recordings into text.
* Supports additional context from selectable-text PDFs.
* Combines semantic retrieval with an LLM to generate lecture-based study materials.
* Allows students to request revision material when needed.
* Provides a browser-based interface for interacting with the system.

The project demonstrates practical integration of speech recognition, embeddings, vector databases, RAG workflows, LLM inference, and web application development.

**Current limitations:** Processing speed depends on recording length, model inference, and available GPU resources. The application has not yet been fully optimized or evaluated using a formal accuracy benchmark.

---

# 🔮 Future Improvements

* Optimize transcription and generation speed for longer lectures.
* Improve handling of noisy audio and unclear speech.
* Deploy the model backend on a more stable, always-available hosting service.
* Improve processing-status tracking and recovery from failures.
* Add export options for notes, summaries, and revision questions.
* Add automated tests for the frontend and backend.
* Evaluate transcription and generated explanations using structured quality tests.

---

# 📚 About the Internship

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for AI**](https://edrak4ai.com/en). The internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the [official Tips Hindawi website](https://www.tipshindawi.com/).

---

# 📄 License

This project is shared for educational and portfolio purposes.

Unless a specific license is added to the repository, no additional permissions should be assumed for redistribution or reuse.

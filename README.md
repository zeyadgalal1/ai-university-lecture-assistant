# 🎓 LectureAI — AI University Lecture Assistant

**Transform university lecture recordings into structured, AI-powered study material.**

LectureAI is an AI-powered study assistant that helps students understand university lectures by transcribing recordings, analyzing lecture content, identifying important concepts, and generating revision material on demand.

Built with **Streamlit, FastAPI, Faster-Whisper, Qwen2.5, and ChromaDB**, the project combines speech recognition, retrieval, and large language models in one study workflow.

---

## ✨ Features

* 🎙️ **Lecture Transcription:** Converts lecture recordings into text using Faster-Whisper (`large-v3`).
* 🎞️ **Multiple Recording Formats:** Supports MP3, MP4, and OGG uploads.
* 🌍 **Multilingual Lectures:** Designed to handle Arabic speech mixed with English technical terminology, subject to recording and transcription quality.
* 📄 **Optional PDF Support:** Extracts selectable text from lecture PDFs using PyMuPDF.
* 🧠 **AI-Powered Lecture Analysis:** Uses Qwen2.5-7B-Instruct to generate structured explanations and study notes from supplied lecture materials.
* 🎯 **Important Concepts:** Helps surface key ideas and potentially exam-relevant points mentioned in the lecture.
* 🔎 **Retrieval-Augmented Workflow:** Uses ChromaDB to index lecture text for retrieval.
* 📚 **Revision on Demand:** Generates revision material only when the student selects the revision action.
* ⚡ **GPU-Backed Inference:** Runs model inference through a FastAPI backend hosted in a Kaggle GPU notebook during development.
* 🖥️ **Interactive Interface:** Provides a Streamlit interface for uploading materials and viewing results.

## 🏗️ System Architecture

```text
          Lecture Recording                Optional PDF
          (MP3 / MP4 / OGG)          (Selectable Text)
                  │                         │
                  ▼                         ▼
             FFmpeg Audio                PyMuPDF
               Chunking               Text Extraction
                  │                         │
                  ▼                         │
         Faster-Whisper large-v3              │
                  │                         │
                  ▼                         ▼
             Transcript ─────────── Lecture Text
                  │                         │
                  └────────────┬────────────┘
                               ▼
                    ChromaDB Indexing
                       and Retrieval
                               │
                               ▼
                    FastAPI Model Backend
                       (Kaggle GPU)
                               │
                               ▼
                      Qwen2.5-7B-Instruct
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
          Lecture Analysis            Revision Material
                                      (On Demand)
                 │                           │
                 └─────────────┬─────────────┘
                               ▼
                       Streamlit Interface
```

## 🛠️ Technology Stack

| Technology                  | Purpose                                                 |
| --------------------------- | ------------------------------------------------------- |
| Python                      | Main programming language                               |
| Streamlit                   | Interactive frontend                                    |
| FastAPI                     | Backend API for model inference                         |
| Faster-Whisper (`large-v3`) | Lecture speech transcription                            |
| Qwen2.5-7B-Instruct         | Lecture analysis and revision generation                |
| 4-bit NF4 quantization      | Reduces language-model memory requirements              |
| ChromaDB                    | Vector database for lecture text retrieval              |
| PyMuPDF                     | Extracts selectable text from PDFs                      |
| FFmpeg                      | Audio conversion and chunking                           |
| Requests                    | HTTP communication between frontend and backend         |
| Kaggle GPU                  | Development environment for model inference             |
| ngrok                       | Tunnel between the local application and remote backend |

## 🔄 How It Works

1. **Upload:** The student uploads a lecture recording.
2. **Transcribe:** Faster-Whisper converts the audio into timestamped text segments.
3. **Extract:** If a PDF is provided, PyMuPDF extracts its selectable text.
4. **Index:** Lecture text is divided into chunks and indexed for retrieval using ChromaDB.
5. **Analyze:** When requested, Qwen2.5 generates study material based on the available lecture content.
6. **Revise:** The student can separately request revision material when ready.

The application is designed to use the student's supplied lecture materials rather than relying on external web research.

## 🚀 Getting Started

### Prerequisites

* Python installed on your computer
* FFmpeg installed and available on your system `PATH`
* Git
* A configured Kaggle GPU notebook running the FastAPI backend
* ngrok configured to expose the backend during development

### 1. Clone the Repository

```bash
git clone https://github.com/zeyadgalal1/ai-university-lecture-assistant.git
cd ai-university-lecture-assistant
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Backend URL

The frontend needs the URL of your active FastAPI backend.

If your `api_client.py` reads the `LECTURE_API_URL` environment variable, set it in PowerShell:

```powershell
$env:LECTURE_API_URL = "https://YOUR-ACTIVE-NGROK-URL"
```

Replace the example with your active tunnel URL. Do not commit authentication tokens or other secrets to GitHub.

### 5. Start the Application

Make sure your Kaggle notebook has loaded the models, started FastAPI, and established the ngrok tunnel.

Then run:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## 📖 How to Use

1. Open LectureAI in your browser.
2. Upload an MP3, MP4, or OGG lecture recording.
3. Optionally upload a PDF containing selectable text.
4. Process the lecture and wait for transcription to finish.
5. Review the available transcript.
6. Select **Analyze Lecture** to generate study material.
7. Select **Generate Revision** whenever you want revision content.

## 📁 Project Structure

```text
AI_University_Lecture_Assistant/
│
├── app.py
├── api_client.py
├── requirements.txt
│
├── modules/
│   ├── __init__.py
│   ├── pdf_processor.py
│   └── rag_pipeline.py
│
├── data/
│   ├── uploads/
│   └── processed/
│
└── .streamlit/
    └── config.toml
```

The model-loading code and FastAPI service may be maintained in a separate Kaggle notebook, depending on the deployment setup.

## 🔌 Backend API

The development backend uses endpoints for health checks, transcription jobs, analysis jobs, and revision jobs.

| Endpoint                      | Method | Purpose                           |
| ----------------------------- | ------ | --------------------------------- |
| `/`                           | GET    | Check backend status              |
| `/transcribe/start`           | POST   | Start a transcription job         |
| `/transcribe/status/{job_id}` | GET    | Retrieve transcription job status |
| `/analyze/start`              | POST   | Start lecture analysis            |
| `/analyze/status/{job_id}`    | GET    | Retrieve analysis job status      |
| `/revision/start`             | POST   | Start revision generation         |
| `/revision/status/{job_id}`   | GET    | Retrieve revision job status      |

These endpoints describe the current development architecture. Keep the frontend API client synchronized with the backend route definitions.

## ⚠️ Limitations

* The development backend requires an active Kaggle session and ngrok tunnel.
* Free notebook sessions and tunnels may disconnect or change availability.
* Only selectable-text PDFs are supported; scanned PDFs require OCR, which is not included in this version.
* Transcription quality depends on audio clarity, background noise, accents, and technical terminology.
* AI-generated explanations and revision material may contain mistakes and should be checked against the original lecture.
* Exam-focused points are suggestions generated from the available content, not guarantees about future exam questions.
* Processing time depends on recording length, model generation, and available GPU resources.

## 🔐 Privacy and Responsible Use

* Do not upload lecture recordings or documents without appropriate permission.
* Do not commit API tokens, ngrok credentials, private recordings, or other sensitive information.
* Review generated study material before relying on it for exams or other important academic decisions.
* Review dependency licenses before redistributing or deploying the project.

## 🗺️ Future Improvements

* More reliable background-job recovery and status tracking.
* Stable, always-available model hosting.
* Better handling and reporting of inaudible or low-confidence transcript sections.
* Exportable lecture notes, summaries, and revision questions.
* Automated tests for the frontend and backend.
* More robust deployment and configuration management.

## 👨‍💻 Author

**Zeyad Galal**

Computer Engineering student interested in AI engineering, machine learning, and practical LLM applications.

* **GitHub:** [@zeyadgalal1](https://github.com/zeyadgalal1)

---

*LectureAI — Learn from your lectures. Understand the concepts. Prepare with confidence.*

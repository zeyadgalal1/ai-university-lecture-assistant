import os
import tempfile

import streamlit as st

from api_client import (
    check_api,
    transcribe_file,
    analyze_lecture,
    generate_revision,
)
from modules.pdf_processor import extract_pdf_text
from modules.rag_pipeline import index_lecture, retrieve_lecture_context, build_context


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LectureAI | University Lecture Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL UI THEME
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #152238;
        --muted: #63738A;
        --teal: #0F9B8E;
        --teal-dark: #087F75;
        --canvas: #F4F7FB;
        --line: #E1E8F0;
        --white: #FFFFFF;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--canvas);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(244, 247, 251, 0.92);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1240px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        padding: 38px 42px;
        margin-bottom: 26px;
        border-radius: 24px;
        color: #FFFFFF;
        background: linear-gradient(120deg, #101B2D 0%, #18344D 62%, #087F75 100%);
        box-shadow: 0 16px 38px rgba(16, 27, 45, 0.13);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -80px;
        top: -115px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(255,255,255,0.035),
                    0 0 0 58px rgba(255,255,255,0.025);
        pointer-events: none;
    }

    .hero-kicker {
        color: #99F6E4;
        text-transform: uppercase;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2.2px;
        margin-bottom: 13px;
    }

    .hero-title {
        color: #FFFFFF;
        font-size: clamp(29px, 4vw, 43px);
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -1.4px;
        margin: 0 0 13px 0;
    }

    .hero-copy {
        color: #D7E5F1;
        font-size: 15px;
        line-height: 1.8;
        max-width: 760px;
        margin: 0;
    }

    .hero-pill {
        display: inline-block;
        margin: 20px 7px 0 0;
        padding: 7px 11px;
        color: #E1FCF7;
        font-size: 11px;
        font-weight: 600;
        border-radius: 100px;
        background: rgba(255,255,255,0.09);
        border: 1px solid rgba(255,255,255,0.17);
    }

    /* Section headings and cards */
    .section-heading {
        margin: 26px 0 5px;
        color: var(--ink);
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.65px;
    }

    .section-copy {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.75;
        margin-bottom: 16px;
    }

    .upload-card {
        min-height: 112px;
        padding: 18px 20px 12px;
        border: 1px solid var(--line);
        border-radius: 17px;
        background: var(--white);
        box-shadow: 0 4px 16px rgba(21, 34, 56, 0.035);
        margin-bottom: 10px;
    }

    .upload-card-title {
        color: var(--ink);
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .upload-card-copy {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.65;
    }

    .info-strip {
        padding: 13px 16px;
        margin: 14px 0 20px;
        border: 1px solid #C9EEE8;
        border-radius: 12px;
        background: #ECFDF9;
        color: #17665F;
        font-size: 12px;
        line-height: 1.7;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 16px 18px;
        box-shadow: 0 4px 15px rgba(21, 34, 56, 0.035);
    }

    .metric-label {
        color: var(--muted);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .7px;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .metric-value {
        color: var(--ink);
        font-size: 25px;
        font-weight: 800;
    }

    .panel-heading {
        color: var(--ink);
        font-size: 19px;
        font-weight: 800;
        letter-spacing: -.4px;
        margin: 8px 0 4px;
    }

    .panel-copy {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.7;
        margin-bottom: 12px;
    }

    /* Streamlit file uploader */
    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 12px;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #B7C8D8;
        border-radius: 11px;
        background: #F8FAFD;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--teal);
    }

    /* Consistent teal buttons: process, analyze, revision, and file upload */
    .stButton > button {
        width: 100%;
        min-height: 45px;
        border-radius: 11px;
        font-weight: 700;
        color: #FFFFFF !important;
        background: var(--teal) !important;
        border: 1px solid var(--teal) !important;
        box-shadow: 0 5px 14px rgba(15, 155, 142, .15);
        transition: all .18s ease;
    }

    .stButton > button:hover {
        color: #FFFFFF !important;
        background: var(--teal-dark) !important;
        border-color: var(--teal-dark) !important;
        transform: translateY(-1px);
    }

    /* Streamlit's Browse files / upload picker buttons */
    [data-testid="stFileUploader"] button {
        color: #FFFFFF !important;
        background: var(--teal) !important;
        border: 1px solid var(--teal) !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        transition: all .18s ease;
    }

    [data-testid="stFileUploader"] button:hover {
        color: #FFFFFF !important;
        background: var(--teal-dark) !important;
        border-color: var(--teal-dark) !important;
    }

    /* Expanders, status, alerts */
    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #FFFFFF;
        overflow: hidden;
    }

    [data-testid="stStatusWidget"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #FFFFFF;
        padding: 8px;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #101B2D;
        border-right: 1px solid #24364D;
    }

    [data-testid="stSidebar"] * {
        color: #E5EDF7;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.75;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        color: #FFFFFF;
        background: #1A3048;
        border-color: #36516B;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        border-color: #5EEAD4;
        color: #99F6E4;
    }

    /* Readable generated content */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        line-height: 1.8;
    }

    h1, h2, h3 {
        color: var(--ink);
        letter-spacing: -.5px;
    }

    hr {
        border-color: var(--line);
    }

    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1rem 1rem 3rem;
        }

        .hero {
            padding: 27px 23px;
            border-radius: 18px;
        }

        .hero-title {
            font-size: 29px;
        }

        .hero-copy {
            font-size: 13px;
        }

        .section-heading {
            font-size: 21px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "lecture_processed": False,
    "transcript": None,
    "pdf_text": "",
    "analysis": None,
    "revision": None,
    "indexed_chunks": 0,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Your personal study workspace</div>
        <div class="hero-title">Turn lectures into understanding.</div>
        <p class="hero-copy">
            Upload a lecture recording and transform it into a searchable transcript,
            structured explanations, important concepts, and revision material —
            all grounded in the material you provide.
        </p>
        <span class="hero-pill">🎙️ Lecture transcription</span>
        <span class="hero-pill">📚 PDF support</span>
        <span class="hero-pill">🧠 AI-powered analysis</span>
        <span class="hero-pill">✦ On-demand revision</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🎓 LectureAI")
    st.caption("UNIVERSITY STUDY ASSISTANT")
    st.divider()

    st.markdown("### ⚙️ System status")
    if st.button("Check GPU backend", key="check_backend"):
        try:
            with st.spinner("Connecting to the GPU backend..."):
                status = check_api()
            st.success("GPU backend is online.")
            st.json(status)
        except Exception as e:
            st.error("Could not connect to the GPU backend.")
            st.caption(str(e))

    st.divider()
    st.markdown("### 🗺️ Your workflow")
    st.markdown(
        """
        **01 · Upload**

        Add your lecture recording and optional PDF.

        **02 · Transcribe**

        Faster-Whisper converts speech into text.

        **03 · Index**

        Lecture text is indexed in ChromaDB.

        **04 · Analyze**

        Generate explanations from the uploaded material.

        **05 · Revise**

        Create revision material only when you request it.
        """
    )
    st.divider()
    st.caption("Built with Streamlit, ChromaDB and a Kaggle GPU backend.")


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown('<div class="section-heading">Start with your lecture</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Upload the recording first. A selectable-text PDF is optional and can provide additional lecture context.</div>',
    unsafe_allow_html=True,
)

audio_col, pdf_col = st.columns(2, gap="large")

with audio_col:
    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-card-title">🎙️ Lecture recording <span style="color:#D9485F">*</span></div>
            <div class="upload-card-copy">Required · MP3, MP4 or OGG<br>For best results, use audio where the lecturer can be heard clearly.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    audio_file = st.file_uploader(
        "Upload recording",
        type=["mp3", "mp4", "ogg"],
        help="Upload the lecture recording as MP3, MP4, or OGG.",
        key="lecture_audio_uploader",
    )

with pdf_col:
    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-card-title">📄 Lecture material</div>
            <div class="upload-card-copy">Optional · PDF only<br>Use a digital PDF with selectable text. Scanned/image-only PDFs are not supported.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    pdf_file = st.file_uploader(
        "Upload PDF (optional)",
        type=["pdf"],
        help="Optional selectable-text PDF. Scanned/image-only PDFs are not supported.",
        key="lecture_pdf_uploader",
    )

if audio_file:
    size_mb = len(audio_file.getbuffer()) / (1024 * 1024)
    st.markdown(
        f"""
        <div class="info-strip">
            <strong>Recording selected:</strong> {audio_file.name}
            &nbsp; · &nbsp; {size_mb:.1f} MB
            <br>When you process the lecture, the app will check the backend, transcribe the recording, extract any PDF text, and index the lecture.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="info-strip">
            <strong>Ready when you are.</strong> Choose a lecture recording to begin.
            You can use the app without uploading a PDF.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROCESS LECTURE
# ============================================================

st.markdown('<div class="section-heading">Process your materials</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">This step transcribes the recording and indexes the available lecture text for later use.</div>',
    unsafe_allow_html=True,
)

if audio_file:
    if st.button("🚀  Process lecture", type="primary", key="process_lecture"):
        st.session_state.lecture_processed = False
        st.session_state.transcript = None
        st.session_state.pdf_text = ""
        st.session_state.analysis = None
        st.session_state.revision = None
        st.session_state.indexed_chunks = 0

        audio_path = None
        pdf_path = None

        try:
            audio_suffix = os.path.splitext(audio_file.name)[1] or ".mp3"
            with tempfile.NamedTemporaryFile(delete=False, suffix=audio_suffix) as temp_audio:
                temp_audio.write(audio_file.getbuffer())
                audio_path = temp_audio.name

            with st.status("Checking GPU backend...", expanded=True) as status:
                check_api()
                st.write("GPU backend connection confirmed.")
                status.update(label="GPU backend connected", state="complete")

            with st.status("Transcribing lecture with Faster-Whisper...", expanded=True) as status:
                transcription_result = transcribe_file(audio_path)
                st.session_state.transcript = transcription_result

                language = transcription_result.get("language", "unknown")
                segments = transcription_result.get("segments", [])

                st.write(f"Detected language: **{language}**")
                st.write(f"Transcript segments: **{len(segments)}**")
                status.update(label="Transcription completed", state="complete")

            if pdf_file:
                with st.status("Extracting selectable PDF text...", expanded=True) as status:
                    pdf_suffix = os.path.splitext(pdf_file.name)[1] or ".pdf"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=pdf_suffix) as temp_pdf:
                        temp_pdf.write(pdf_file.getbuffer())
                        pdf_path = temp_pdf.name

                    pdf_pages = extract_pdf_text(pdf_path)
                    if not pdf_pages:
                        raise ValueError(
                            "The PDF does not contain selectable text. "
                            "Scanned/image-only PDFs are not supported."
                        )

                    pdf_text_parts = []
                    for page in pdf_pages:
                        if isinstance(page, dict):
                            page_text = page.get("text", "")
                        else:
                            page_text = str(page)
                        if page_text.strip():
                            pdf_text_parts.append(page_text)

                    st.session_state.pdf_text = "\n\n".join(pdf_text_parts)
                    if not st.session_state.pdf_text.strip():
                        raise ValueError(
                            "No selectable text was found in this PDF. "
                            "Please use a digital PDF containing text."
                        )

                    st.write(f"Extracted text from **{len(pdf_pages)} pages**.")
                    status.update(label="PDF text extracted", state="complete")
            else:
                st.session_state.pdf_text = ""

            with st.status("Indexing lecture in ChromaDB...", expanded=True) as status:
                transcript_data = st.session_state.transcript or {}
                segments = transcript_data.get("segments", [])
                transcript_text = "\n".join(
                    segment.get("text", "")
                    for segment in segments
                    if segment.get("text", "").strip()
                )

                indexed_chunks = index_lecture(
                    transcript=transcript_text,
                    pdf_text=st.session_state.pdf_text,
                )

                if indexed_chunks == 0:
                    raise ValueError("No lecture text was available to index.")

                st.session_state.indexed_chunks = indexed_chunks
                st.write(f"Indexed **{indexed_chunks} lecture chunks**.")
                status.update(label="Lecture indexed successfully", state="complete")

            st.session_state.lecture_processed = True
            st.success("Lecture processed successfully.")
            st.info("Your transcript and materials are ready for analysis.")

        except Exception as e:
            st.error("Something went wrong while processing the lecture.")
            st.exception(e)

        finally:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)


# ============================================================
# RESULTS DASHBOARD
# ============================================================

if st.session_state.lecture_processed:
    st.divider()
    st.markdown('<div class="section-heading">Your lecture workspace</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Explore the transcript, generate an explanation, or prepare revision notes when you are ready.</div>',
        unsafe_allow_html=True,
    )

    transcript_data = st.session_state.transcript or {}
    segments = transcript_data.get("segments", [])
    language = transcript_data.get("language", "Unknown")
    segment_count = len(segments)
    transcript_text = "\n".join(
        segment.get("text", "")
        for segment in segments
        if segment.get("text", "").strip()
    )

    metric1, metric2, metric3 = st.columns(3, gap="medium")
    with metric1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Transcript segments</div><div class="metric-value">{segment_count}</div></div>',
            unsafe_allow_html=True,
        )
    with metric2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Indexed chunks</div><div class="metric-value">{st.session_state.indexed_chunks}</div></div>',
            unsafe_allow_html=True,
        )
    with metric3:
        pdf_status = "Added" if st.session_state.pdf_text.strip() else "Not added"
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">PDF material</div><div class="metric-value" style="font-size:21px">{pdf_status}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    with st.expander("📝  View full transcript", expanded=False):
        st.caption(f"Detected language: {language}")
        if segments:
            for segment in segments:
                start = segment.get("start", 0)
                end = segment.get("end", 0)
                text = segment.get("text", "").strip()
                if text:
                    st.markdown(f"**{start:.1f}s – {end:.1f}s**  \n{text}")
        else:
            st.info("No transcript segments were returned.")

    st.divider()
    analysis_col, revision_col = st.columns(2, gap="large")

    with analysis_col:
        st.markdown('<div class="panel-heading">🧠 Lecture analysis</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-copy">Create a structured explanation based on your uploaded lecture materials.</div>',
            unsafe_allow_html=True,
        )
        if st.button("✨  Analyze lecture", type="primary", key="analyze_lecture"):
            with st.spinner("Qwen is analyzing the lecture materials..."):
                try:
                    result = analyze_lecture(
                        transcript=transcript_text,
                        pdf_text=st.session_state.pdf_text,
                    )
                    st.session_state.analysis = result.get("response", "")
                    if not st.session_state.analysis:
                        st.warning("The backend returned an empty analysis.")
                except Exception as e:
                    st.error("Could not analyze the lecture.")
                    st.exception(e)

        if st.session_state.analysis:
            with st.container(border=True):
                st.markdown("#### Analysis")
                st.markdown(st.session_state.analysis)

    with revision_col:
        st.markdown('<div class="panel-heading">📘 Revision studio</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-copy">Prepare revision material for your next study session. It runs only when you press the button.</div>',
            unsafe_allow_html=True,
        )
        if st.button("🔄  Generate revision", key="generate_revision"):
            with st.spinner("Preparing your revision material..."):
                try:
                    result = generate_revision(
                        transcript=transcript_text,
                        pdf_text=st.session_state.pdf_text,
                    )
                    st.session_state.revision = result.get("response", "")
                    if not st.session_state.revision:
                        st.warning("The backend returned empty revision material.")
                except Exception as e:
                    st.error("Could not generate revision.")
                    st.exception(e)

        if st.session_state.revision:
            with st.container(border=True):
                st.markdown("#### Revision material")
                st.markdown(st.session_state.revision)


# ============================================================
# EMPTY STATE / FOOTER
# ============================================================

if not audio_file and not st.session_state.lecture_processed:
    st.markdown(
        """
        <div style="
            text-align:center;
            padding:28px 18px;
            border:1px dashed #C8D5E3;
            border-radius:18px;
            background:rgba(255,255,255,.62);
            margin-top:10px;">
            <div style="font-size:30px;margin-bottom:8px;">📂</div>
            <div style="font-weight:750;color:#152238;font-size:16px;">Your study space is ready</div>
            <div style="color:#63738A;font-size:13px;margin-top:7px;line-height:1.7;">
                Upload an MP3, MP4, or OGG lecture recording above to get started.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="
        margin-top:42px;
        padding-top:16px;
        border-top:1px solid #E1E8F0;
        text-align:center;
        color:#8190A4;
        font-size:11px;">
        LECTUREAI · AI UNIVERSITY LECTURE ASSISTANT
        <br>Designed to help you learn from your own lecture materials.
    </div>
    """,
    unsafe_allow_html=True,
)

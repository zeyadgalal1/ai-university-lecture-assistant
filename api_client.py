
import os
import time
import glob
import tempfile
import subprocess

import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "https://splurge-hydrated-idly.ngrok-free.dev"



CHUNK_SECONDS = 300  # 5 minutes

STATUS_RETRY_DELAY = 5
STATUS_REQUEST_TIMEOUT = (10, 60)
MAX_STATUS_RETRIES = 12
TRANSCRIPTION_TIMEOUT = 1800  # 30 minutes per chunk

ANALYSIS_TIMEOUT = (30, 1800)


# ============================================================
# API HEALTH CHECK
# ============================================================

def check_api():
    """Check whether the Kaggle API is reachable."""
    try:
        response = requests.get(
            f"{API_URL}/",
            timeout=(10, 90)
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout as exc:
        raise TimeoutError(
            "The Kaggle API did not respond in time. "
            "Check that the Kaggle notebook is running and "
            "the ngrok tunnel is active."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise ConnectionError(
            f"Could not connect to the Kaggle API at {API_URL}. "
            "Check the API URL, Kaggle server, and ngrok tunnel."
        ) from exc


# ============================================================
# AUDIO / VIDEO CHUNKING
# ============================================================

def _prepare_chunks(file_path, temp_dir):
    """
    Return audio chunks from a folder or split one audio/video file
    into 5-minute MP3 chunks using FFmpeg.

    Returns:
        (chunks, temporary_chunks_created)
    """
    if os.path.isdir(file_path):
        chunks = sorted(
            glob.glob(os.path.join(file_path, "chunk_*.mp3"))
        )

        if not chunks:
            raise FileNotFoundError(
                f"No chunk_*.mp3 files found in: {file_path}"
            )

        return chunks, False

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Audio/video file not found: {file_path}"
        )

    if not temp_dir:
        raise ValueError(
            "temp_dir is required when splitting a single file."
        )

    output_pattern = os.path.join(
        temp_dir,
        "chunk_%03d.mp3"
    )

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", file_path,
        "-map", "0:a:0",
        "-vn",
        "-f", "segment",
        "-segment_time", str(CHUNK_SECONDS),
        "-reset_timestamps", "1",
        "-c:a", "libmp3lame",
        "-b:a", "64k",
        "-ar", "16000",
        "-ac", "1",
        output_pattern,
    ]

    print("Splitting lecture into 5-minute audio chunks...")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3600,
            check=False
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg was not found. Install FFmpeg and make sure "
            "it is available on your system PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            "FFmpeg took too long to split the lecture."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg could not split the lecture. "
            "The file may not contain an audio stream.\n"
            + result.stderr[-3000:]
        )

    chunks = sorted(
        glob.glob(os.path.join(temp_dir, "chunk_*.mp3"))
    )

    if not chunks:
        raise RuntimeError(
            "FFmpeg did not create any audio chunks. "
            "Check that the uploaded file contains audio."
        )

    print(f"Created {len(chunks)} audio chunks.")

    return chunks, True


# ============================================================
# TRANSCRIBE ONE CHUNK THROUGH THE BACKGROUND API
# ============================================================

def _transcribe_one_chunk(chunk_path):
    """Upload one audio chunk and poll until transcription finishes."""
    filename = os.path.basename(chunk_path)

    print(f"Uploading {filename}...")

    # Avoid blindly retrying the POST: the server may have created
    # a job even if the client loses the response.
    try:
        with open(chunk_path, "rb") as audio_file:
            response = requests.post(
                f"{API_URL}/transcribe/start",
                files={
                    "file": (
                        filename,
                        audio_file,
                        "audio/mpeg"
                    )
                },
                timeout=(30, 180)
            )

        response.raise_for_status()
        start_data = response.json()

    except requests.exceptions.RequestException as exc:
        raise ConnectionError(
            f"Could not start transcription for {filename}. "
            "Check the Kaggle API and ngrok connection. "
            "The server may have received the upload even if "
            "the client did not receive its response."
        ) from exc

    job_id = start_data.get("job_id")

    if not job_id:
        raise RuntimeError(
            f"The API did not return a job ID for {filename}. "
            f"Response: {start_data}"
        )

    print(f"Transcription started for {filename}.")
    print(f"Job ID: {job_id}")

    start_time = time.monotonic()
    consecutive_status_errors = 0

    while True:
        elapsed = time.monotonic() - start_time

        if elapsed > TRANSCRIPTION_TIMEOUT:
            raise TimeoutError(
                f"Transcription exceeded "
                f"{TRANSCRIPTION_TIMEOUT} seconds for {filename}. "
                "The Kaggle job may still be running."
            )

        try:
            response = requests.get(
                f"{API_URL}/transcribe/status/{job_id}",
                timeout=STATUS_REQUEST_TIMEOUT
            )

            response.raise_for_status()
            data = response.json()

            consecutive_status_errors = 0

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as exc:
            consecutive_status_errors += 1

            print(
                f"Temporary connection problem for {filename} "
                f"({consecutive_status_errors}/{MAX_STATUS_RETRIES})."
            )

            if consecutive_status_errors >= MAX_STATUS_RETRIES:
                raise ConnectionError(
                    f"Could not retrieve the status of {filename} "
                    f"after {MAX_STATUS_RETRIES} consecutive failures. "
                    "Check the Kaggle notebook and ngrok tunnel."
                ) from exc

            time.sleep(STATUS_RETRY_DELAY)
            continue

        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"The transcription status API returned an HTTP error "
                f"for {filename}: {exc}"
            ) from exc

        status = data.get("status")

        if status == "completed":
            segments = data.get("segments", [])

            # Support both the current API response and versions
            # that already return these convenience fields.
            data.setdefault("segments_count", len(segments))
            data.setdefault(
                "message",
                f"Transcription completed for {filename}."
            )

            print(
                f"Completed {filename}: "
                f"{data['segments_count']} segments."
            )

            return data

        if status == "failed":
            error_message = (
                data.get("error")
                or data.get("message")
                or "Unknown transcription error"
            )

            raise RuntimeError(
                f"Transcription failed for {filename}: "
                f"{error_message}"
            )

        if status not in ("queued", "processing"):
            raise RuntimeError(
                f"Unexpected status for {filename}: {status!r}. "
                f"API response: {data}"
            )

        progress = data.get("progress", 0)

        print(
            f"{filename}: status={status}, "
            f"progress={progress}%"
        )

        time.sleep(5)


# ============================================================
# TRANSCRIBE THE COMPLETE LECTURE
# ============================================================

def transcribe_file(file_path):
    """
    Transcribe a complete lecture from a single audio/video file
    or a directory of existing chunk_*.mp3 files.

    Returns a combined transcript, segments, and language metadata.
    """
    total_start = time.monotonic()

    if os.path.isdir(file_path):
        chunks, _ = _prepare_chunks(file_path, None)
        return _transcribe_chunks(chunks, total_start)

    with tempfile.TemporaryDirectory(
        prefix="lecture_chunks_"
    ) as temp_dir:
        chunks, _ = _prepare_chunks(file_path, temp_dir)
        return _transcribe_chunks(chunks, total_start)


def _transcribe_chunks(chunks, total_start):
    """Transcribe chunks sequentially and restore lecture timestamps."""
    all_segments = []
    languages = []
    probabilities = []

    for index, chunk_path in enumerate(chunks):
        print(
            f"\nProcessing chunk {index + 1} of {len(chunks)}..."
        )

        result = _transcribe_one_chunk(chunk_path)

        language = result.get("language")
        if language:
            languages.append(language)

        probability = result.get("language_probability")
        if probability is not None:
            probabilities.append(float(probability))

        # The chunk index corresponds to its 5-minute position
        # in the original lecture.
        time_offset = index * CHUNK_SECONDS

        for segment in result.get("segments", []):
            adjusted_segment = dict(segment)

            adjusted_segment["start"] = (
                float(segment["start"]) + time_offset
            )
            adjusted_segment["end"] = (
                float(segment["end"]) + time_offset
            )

            all_segments.append(adjusted_segment)

    all_segments.sort(
        key=lambda segment: segment["start"]
    )

    transcript = " ".join(
        segment.get("text", "").strip()
        for segment in all_segments
        if segment.get("text", "").strip()
    ).strip()

    print("\nFull lecture transcription completed.")

    return {
        "status": "completed",
        "message": "All lecture chunks transcribed successfully",
        "transcript": transcript,
        "segments": all_segments,
        "segments_count": len(all_segments),
        "language": (
            max(set(languages), key=languages.count)
            if languages else None
        ),
        "language_probability": (
            sum(probabilities) / len(probabilities)
            if probabilities else None
        ),
        "elapsed_seconds": round(
            time.monotonic() - total_start,
            2
        ),
    }


# ============================================================
# LONG-RUNNING ANALYSIS / REVISION BACKGROUND JOBS
# ============================================================

ANALYSIS_POLL_DELAY = 3
ANALYSIS_JOB_TIMEOUT = 3 * 60 * 60  # 3 hours total
ANALYSIS_STATUS_MAX_RETRIES = 20


def _run_background_generation(operation, transcript, pdf_text=""):
    """
    Start a background analysis/revision job, then poll its short status
    endpoint until the result is ready. Never re-POST the start request
    automatically, because that could create duplicate jobs.
    """
    if operation not in ("analyze", "revision"):
        raise ValueError(f"Unsupported generation operation: {operation}")

    base_url = API_URL.rstrip("/")
    payload = {
        "transcript": transcript,
        "pdf_text": pdf_text or "",
    }

    # Starting a job should return quickly with a job_id.
    try:
        start_response = requests.post(
            f"{base_url}/{operation}/start",
            json=payload,
            timeout=(15, 120),
        )
        if start_response.status_code >= 400:
            raise RuntimeError(
                f"Could not start {operation} job "
                f"(HTTP {start_response.status_code}): "
                f"{start_response.text[:3000]}"
            )
        start_data = start_response.json()
    except requests.exceptions.Timeout as exc:
        raise TimeoutError(
            f"Timed out while starting {operation}. The server may have "
            "received the request; check Kaggle before retrying to avoid "
            "creating duplicate jobs."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(
            f"Could not connect to the Kaggle API to start {operation}: {exc}"
        ) from exc

    job_id = start_data.get("job_id")
    if not job_id:
        raise RuntimeError(
            f"The {operation} start endpoint did not return a job_id. "
            f"Response: {start_data}"
        )

    print(f"{operation.capitalize()} job started: {job_id}")
    started_at = time.monotonic()
    consecutive_errors = 0

    while True:
        if time.monotonic() - started_at > ANALYSIS_JOB_TIMEOUT:
            raise TimeoutError(
                f"The {operation} job {job_id} exceeded "
                f"{ANALYSIS_JOB_TIMEOUT // 3600} hours. "
                "The Kaggle job may still be running; check its status "
                "before starting another job."
            )

        try:
            status_response = requests.get(
                f"{base_url}/{operation}/status/{job_id}",
                timeout=STATUS_REQUEST_TIMEOUT,
            )

            if status_response.status_code >= 400:
                # Include the response body so ngrok/API errors are visible.
                raise RuntimeError(
                    f"Status check failed for {operation} job {job_id} "
                    f"(HTTP {status_response.status_code}): "
                    f"{status_response.text[:2000]}"
                )

            job = status_response.json()
            consecutive_errors = 0

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as exc:
            consecutive_errors += 1
            print(
                f"Temporary status connection error "
                f"({consecutive_errors}/{ANALYSIS_STATUS_MAX_RETRIES}): {exc}"
            )
            if consecutive_errors >= ANALYSIS_STATUS_MAX_RETRIES:
                raise ConnectionError(
                    f"Could not retrieve {operation} job {job_id} status "
                    f"after {ANALYSIS_STATUS_MAX_RETRIES} consecutive failures. "
                    "Check that Kaggle and ngrok are still running. The job "
                    "may still be processing on Kaggle."
                ) from exc
            time.sleep(STATUS_RETRY_DELAY)
            continue
        except requests.exceptions.RequestException as exc:
            raise ConnectionError(
                f"Could not retrieve {operation} job status: {exc}"
            ) from exc

        status = job.get("status")
        if status == "completed":
            result = job.get("result")
            if isinstance(result, dict) and "response" in result:
                return result
            raise RuntimeError(
                f"The completed {operation} job returned an unexpected "
                f"result format: {str(result)[:2000]}"
            )

        if status == "failed":
            raise RuntimeError(
                f"{operation.capitalize()} job failed on Kaggle: "
                f"{job.get('error') or 'No error details were returned.'}"
            )

        if status not in ("queued", "running", "processing", "pending"):
            raise RuntimeError(
                f"Unexpected status for {operation} job {job_id}: "
                f"{status!r}. Response: {job}"
            )

        print(f"{operation.capitalize()} status: {status}")
        time.sleep(ANALYSIS_POLL_DELAY)


# ============================================================
# LECTURE ANALYSIS
# ============================================================

def analyze_lecture(transcript, pdf_text=""):
    """Analyze a lecture using the Kaggle background-job endpoint."""
    return _run_background_generation("analyze", transcript, pdf_text)


# ============================================================
# REVISION GENERATION
# ============================================================

def generate_revision(transcript, pdf_text=""):
    """Generate a revision guide using the Kaggle background-job endpoint."""
    return _run_background_generation("revision", transcript, pdf_text)

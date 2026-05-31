import ffmpeg
import math
import os
import yt_dlp

import re

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _is_valid_youtube_url(url: str) -> bool:
    return bool(re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url))


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as exc:
            raise ValueError(
                f"YouTube download failed for URL {url}. "
                f"Please check the URL and try again. Original error: {exc}"
            ) from exc
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using ffmpeg."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    (
        ffmpeg
        .input(input_path)
        .output(output_path, ac=1, ar=16000, format="wav")
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Split a WAV file into chunks of `chunk_minutes` minutes and return list of paths."""
    info = ffmpeg.probe(wav_path)
    duration = float(info["format"]["duration"])
    chunk_length = chunk_minutes * 60.0

    chunks = []
    count = math.ceil(duration / chunk_length)

    for i in range(count):
        start = i * chunk_length
        length = min(chunk_length, duration - start)
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        (
            ffmpeg
            .input(wav_path, ss=start, t=length)
            .output(chunk_path, ac=1, ar=16000, format="wav")
            .overwrite_output()
            .run(quiet=True)
        )
        chunks.append(chunk_path)

    return chunks


def process_input(source: str, chunk_minutes: int = 1) -> list:
    """Download or convert input source to WAV, then chunk the result."""
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected remote URL. Checking YouTube URL support...")
        if not _is_valid_youtube_url(source):
            raise ValueError(
                "Only full YouTube URLs are supported for remote input. "
                "Please provide a valid https://www.youtube.com/watch?v=<VIDEO_ID> or https://youtu.be/<VIDEO_ID>."
            )
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Local input file not found: {source}")

        if source.lower().endswith(".wav"):
            print("Detected local WAV file. Skipping conversion...")
            wav_path = source
        else:
            print("Detected local file. Converting to WAV...")
            wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path, chunk_minutes=chunk_minutes)
    print(f"Audio ready - {len(chunks)} chunk(s) created.")
    return chunks


if __name__ == "__main__":
    import sys

    source = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=7HSSR1n8dgc"
    process_input(source, chunk_minutes=1)

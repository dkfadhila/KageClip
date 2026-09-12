#!/usr/bin/env python3
"""KageClip Local Engine.

Small, browser-agnostic local worker for KageClip. It reads newline-delimited
JSON from stdin and writes newline-delimited JSON to stdout, making it suitable
for a Native Messaging host or another local bridge.

Protocol:
  {"type":"info","id":"...","url":"https://..."}
  {"type":"download","id":"...","url":"https://...","mode":"video","quality":"best"}

Responses:
  {"type":"info","id":"...","status":"ok", ...}
  {"type":"progress","id":"...","percent":42.1,"status":"downloading"}
  {"type":"done","id":"...","filename":"...","path":"..."}
  {"type":"error","id":"...","message":"..."}

Security: only http/https URLs are accepted; subprocesses use argument arrays
(no shell), and output is kept inside the user's KageClip Downloads directory.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DOWNLOAD_DIR = Path.home() / "Downloads" / "KageClip"
MAX_TITLE_LENGTH = 180


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def error(job_id: str, message: str) -> None:
    emit({"type": "error", "id": job_id, "message": message})


def valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def safe_name(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", name).strip(" .")
    return (name or "kageclip")[:MAX_TITLE_LENGTH]


def progress_hook(job_id: str):
    def hook(data: dict[str, Any]) -> None:
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            percent = round(downloaded * 100 / total, 1) if total else None
            emit({
                "type": "progress",
                "id": job_id,
                "percent": percent,
                "speed": data.get("speed"),
                "eta": data.get("eta"),
                "status": "downloading",
            })
        elif status == "finished":
            emit({"type": "progress", "id": job_id, "percent": 100, "status": "processing"})
    return hook


def make_ydl_opts(job_id: str, mode: str, quality: str) -> dict[str, Any]:
    import yt_dlp

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if mode == "audio":
        return {
            "format": "bestaudio/best",
            "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress_hook(job_id)],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

    # Quality is deliberately converted to a constrained yt-dlp selector.
    if quality in {"144", "240", "360", "480", "720", "1080"}:
        fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
    else:
        fmt = "bestvideo+bestaudio/best"
    return {
        "format": fmt,
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_hook(job_id)],
    }


def handle_info(job_id: str, url: str) -> None:
    import yt_dlp

    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        data = ydl.extract_info(url, download=False)
    formats = []
    for item in data.get("formats", []):
        height = item.get("height")
        if item.get("vcodec") != "none" and height:
            formats.append({"format_id": item.get("format_id"), "height": height, "ext": item.get("ext")})
    emit({
        "type": "info",
        "id": job_id,
        "status": "ok",
        "title": data.get("title"),
        "duration": data.get("duration"),
        "thumbnail": data.get("thumbnail"),
        "formats": formats,
    })


def handle_download(job_id: str, url: str, mode: str, quality: str) -> None:
    import yt_dlp

    opts = make_ydl_opts(job_id, mode, quality)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        requested = Path(ydl.prepare_filename(info))

    candidates = list(DOWNLOAD_DIR.glob(f"{safe_name(info.get('title') or 'kageclip')}.*"))
    if not candidates and requested.exists():
        candidates = [requested]
    output = candidates[0] if candidates else requested
    emit({"type": "done", "id": job_id, "filename": output.name, "path": str(output)})


def handle(message: dict[str, Any]) -> None:
    job_id = str(message.get("id") or "unknown")
    kind = message.get("type")
    url = message.get("url")
    if kind not in {"info", "download"}:
        return error(job_id, "Unsupported request type")
    if not valid_url(url):
        return error(job_id, "Only valid http/https URLs are accepted")
    try:
        if kind == "info":
            handle_info(job_id, url.strip())
        else:
            mode = message.get("mode", "video")
            quality = str(message.get("quality", "best"))
            if mode not in {"video", "audio"}:
                return error(job_id, "mode must be video or audio")
            handle_download(job_id, url.strip(), mode, quality)
    except Exception as exc:
        error(job_id, str(exc)[:500])


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            if isinstance(message, dict):
                handle(message)
            else:
                error("unknown", "Request must be a JSON object")
        except json.JSONDecodeError:
            error("unknown", "Invalid JSON")


if __name__ == "__main__":
    main()

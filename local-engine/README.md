# KageClip Local Engine

Local worker for the KageClip browser extension.

## Purpose

The engine runs on the user's machine so downloaded media is written directly to:

`~/Downloads/KageClip/`

It is intentionally independent of Flask/Vercel. The browser side can communicate
with it through a Native Messaging host in the next step.

## Protocol

One JSON object per line on stdin; one JSON object per line on stdout.

### Inspect a URL

```json
{"type":"info","id":"job-1","url":"https://example.com/video"}
```

### Download video

```json
{"type":"download","id":"job-2","url":"https://example.com/video","mode":"video","quality":"720"}
```

### Download audio

```json
{"type":"download","id":"job-3","url":"https://example.com/video","mode":"audio"}
```

The engine emits `info`, `progress`, `done`, and `error` messages.

## Local test

Install dependencies from the project environment, then run:

```bash
python local-engine/kageclip_engine.py
```

Paste one JSON request and press Enter. The engine requires `yt-dlp`; video/audio
post-processing also requires FFmpeg to be available to yt-dlp.

## Next step

Add browser-specific Native Messaging manifests and a small extension background
worker that forwards KageClip requests to this engine. The native host should
invoke this script without a shell and should not expose an unauthenticated HTTP
command endpoint.

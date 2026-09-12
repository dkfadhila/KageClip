<div align="center">

  <img src="assets/banner.svg" alt="KageClip — 影で、残す。" width="780">

  ### **Clip the web, keep what matters.**

  **KageClip** is a self-hosted, open-source media downloader with a quiet, Japanese-inspired soul.
  Paste a link from YouTube, TikTok, Instagram, X, or 1000+ other sites — keep it as **MP4 video** or **MP3 audio**. Your links never leave your machine.

  [![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white&labelColor=292929)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-3.x-9B9B9B?style=flat&logo=flask&logoColor=white&labelColor=292929)](https://flask.palletsprojects.com/)
  [![yt-dlp](https://img.shields.io/badge/Powered%20by-yt--dlp-F15A32?style=flat&labelColor=292929)](https://github.com/yt-dlp/yt-dlp)
  [![License](https://img.shields.io/badge/License-MIT-F15A32?style=flat&labelColor=292929)](LICENSE)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-35784A?style=flat&labelColor=292929)](#)


</div>

<br>

## 影 The idea

**Kage** (かげ) means *shadow* in Japanese.

A shadow asks for nothing — it follows quietly, keeps its shape, and leaves nothing behind. That is the whole philosophy of KageClip: a downloader that stays out of your way. No accounts, no tracking, no noise. You give it a link; it hands you back your media.

> *影で、残す。* — **"In the shadow, we keep."**

## Why KageClip

| | |
|---|---|
| ⚡ **Fast** | Get your media in seconds — fetch info, pick a quality, done. |
| 🙈 **No registration** | 100% free and open. No account, no API key, no sign-in wall. |
| 🔒 **Private** | Self-hosted by design. Your links and downloads are yours only. |
| 🌐 **All platforms** | Anything [yt-dlp](https://github.com/yt-dlp/yt-dlp) supports — 1000+ sites and counting. |

And the details that make it feel calm rather than busy:

- **Bulk friendly** — paste multiple URLs at once (spaces, commas, or newlines); duplicates are removed automatically.
- **Quality picker** — choose the exact resolution per video, or just grab the best.
- **MP3 mode** — extract clean audio from any video.
- **Whole playlists** — drop a YouTube playlist link and it expands for you.
- **One file frontend** — vanilla HTML/CSS/JS. No build step, no framework, no node_modules.

## Supported platforms

<div align="center">

![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=flat-square&logo=youtube&logoColor=white)
![TikTok](https://img.shields.io/badge/TikTok-010101?style=flat-square&logo=tiktok&logoColor=white)
![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=flat-square&logo=instagram&logoColor=white)
![X](https://img.shields.io/badge/X-0F1419?style=flat-square&logo=x&logoColor=white)
![Reddit](https://img.shields.io/badge/Reddit-FF4500?style=flat-square&logo=reddit&logoColor=white)
![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=flat-square&logo=facebook&logoColor=white)
![Vimeo](https://img.shields.io/badge/Vimeo-1AB7EA?style=flat-square&logo=vimeo&logoColor=white)
![Twitch](https://img.shields.io/badge/Twitch-9146FF?style=flat-square&logo=twitch&logoColor=white)
![SoundCloud](https://img.shields.io/badge/SoundCloud-FF5500?style=flat-square&logo=soundcloud&logoColor=white)
![Dailymotion](https://img.shields.io/badge/Dailymotion-0F6CDA?style=flat-square&logo=dailymotion&logoColor=white)

…plus Loom, Pinterest, Tumblr, Threads, LinkedIn, Streamable — and every other site in [yt-dlp's supported list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

</div>

## How it feels to use

```
  Paste one or more URLs →  [ MP4 | MP3 ]  →  Fetch
                                    ↓
                     pick a quality (or Download All)
                                    ↓
                          keep what matters 🌙
```

No dashboards to learn and nothing to configure — the downloader *is* the interface. One large input, one orange button, and a little shadow watching over it.

<div align="center">
  <img src="assets/preview-mp3.png" alt="KageClip in MP3 mode" width="720">
</div>

## Under the hood

| Layer | Choice |
|---|---|
| **Backend** | Python + Flask — a single ~150-line file |
| **Download engine** | [yt-dlp](https://github.com/yt-dlp/yt-dlp) (+ ffmpeg for merging & audio) |
| **Frontend** | Single-file vanilla HTML/CSS/JS — no build step |
| **Deployment** | Ships with a Dockerfile & docker-compose for one-command self-hosting |

## Disclaimer

For personal use only — respect copyright and the terms of service of each platform. The authors are not responsible for misuse.


## License

[MIT](LICENSE) — do what you like, quietly. 🌑

<div align="center">
  <sub>Built with 影 (kage) for a more open internet.</sub>
</div>

import os
import uuid
import glob
import json
import subprocess
import threading
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
jobs = {}

SUPPORTED_SITES = [
    {"name":"YouTube","domain":"youtube.com","url":"https://www.youtube.com","category":"Video & Social","short":"YT","color":"#ff0000"}, {"name":"TikTok","domain":"tiktok.com","url":"https://www.tiktok.com","category":"Video & Social","short":"TT","color":"#111111"}, {"name":"Instagram","domain":"instagram.com","url":"https://www.instagram.com","category":"Video & Social","short":"IG","color":"#d94675"}, {"name":"X / Twitter","domain":"x.com","url":"https://x.com","category":"Video & Social","short":"X","color":"#111111"}, {"name":"Facebook","domain":"facebook.com","url":"https://www.facebook.com","category":"Video & Social","short":"f","color":"#1877f2"}, {"name":"Reddit","domain":"reddit.com","url":"https://www.reddit.com","category":"Video & Social","short":"r","color":"#ff4500"}, {"name":"Vimeo","domain":"vimeo.com","url":"https://vimeo.com","category":"Video & Social","short":"V","color":"#1ab7ea"}, {"name":"Twitch","domain":"twitch.tv","url":"https://www.twitch.tv","category":"Video & Social","short":"TW","color":"#9146ff"}, {"name":"Dailymotion","domain":"dailymotion.com","url":"https://www.dailymotion.com","category":"Video & Social","short":"DM","color":"#1671db"}, {"name":"Loom","domain":"loom.com","url":"https://www.loom.com","category":"Video & Social","short":"L","color":"#625df5"},
    {"name":"Pinterest","domain":"pinterest.com","url":"https://www.pinterest.com","category":"Publishing & Creative","short":"P","color":"#bd081c"}, {"name":"Tumblr","domain":"tumblr.com","url":"https://www.tumblr.com","category":"Publishing & Creative","short":"T","color":"#36465d"}, {"name":"Threads","domain":"threads.net","url":"https://www.threads.net","category":"Publishing & Creative","short":"TH","color":"#111111"}, {"name":"LinkedIn","domain":"linkedin.com","url":"https://www.linkedin.com","category":"Publishing & Creative","short":"in","color":"#0a66c2"}, {"name":"Bilibili","domain":"bilibili.com","url":"https://www.bilibili.com","category":"Publishing & Creative","short":"B","color":"#00aeec"}, {"name":"VK","domain":"vk.com","url":"https://vk.com","category":"Publishing & Creative","short":"VK","color":"#0077ff"}, {"name":"Rumble","domain":"rumble.com","url":"https://rumble.com","category":"Publishing & Creative","short":"R","color":"#85c742"}, {"name":"Streamable","domain":"streamable.com","url":"https://streamable.com","category":"Publishing & Creative","short":"S","color":"#2f7cff"}, {"name":"Kick","domain":"kick.com","url":"https://kick.com","category":"Publishing & Creative","short":"K","color":"#53fc18"},
    {"name":"SoundCloud","domain":"soundcloud.com","url":"https://soundcloud.com","category":"Music & Audio","short":"SC","color":"#ff5500"}, {"name":"Bandcamp","domain":"bandcamp.com","url":"https://bandcamp.com","category":"Music & Audio","short":"BC","color":"#629aa9"}, {"name":"Audiomack","domain":"audiomack.com","url":"https://audiomack.com","category":"Music & Audio","short":"AM","color":"#ffa200"}, {"name":"Mixcloud","domain":"mixcloud.com","url":"https://www.mixcloud.com","category":"Music & Audio","short":"M","color":"#5000ff"},
    {"name":"9GAG","domain":"9gag.com","url":"https://9gag.com","category":"More Platforms","short":"9G","color":"#111111"}, {"name":"Imgur","domain":"imgur.com","url":"https://imgur.com","category":"More Platforms","short":"IM","color":"#1bb76e"}, {"name":"Archive.org","domain":"archive.org","url":"https://archive.org","category":"More Platforms","short":"IA","color":"#333333"}, {"name":"OK.ru","domain":"ok.ru","url":"https://ok.ru","category":"More Platforms","short":"OK","color":"#ee8208"}, {"name":"Bitchute","domain":"bitchute.com","url":"https://www.bitchute.com","category":"More Platforms","short":"BC","color":"#ef4444"}, {"name":"Rutube","domain":"rutube.ru","url":"https://rutube.ru","category":"More Platforms","short":"RT","color":"#111111"}, {"name":"Coub","domain":"coub.com","url":"https://coub.com","category":"More Platforms","short":"C","color":"#111111"}, {"name":"Vidyard","domain":"vidyard.com","url":"https://www.vidyard.com","category":"More Platforms","short":"VY","color":"#1f2937"},
]

def parse_ytdlp_json(stdout):
    for line in stdout.splitlines():
        line = line.strip()
        if line: return json.loads(line)
    raise ValueError("yt-dlp returned no data")

def run_download(job_id, url, format_choice, format_id):
    job = jobs[job_id]; out_template = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    cmd = ["yt-dlp", "--no-playlist", "-o", out_template]
    if format_choice == "audio": cmd += ["-x", "--audio-format", "mp3"]
    elif format_id: cmd += ["-f", f"{format_id}+bestaudio/best", "--merge-output-format", "mp4"]
    else: cmd += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]
    cmd.append(url)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0: job.update(status="error", error=result.stderr.strip().split("\n")[-1]); return
        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{job_id}.*"))
        if not files: job.update(status="error", error="Download completed but no file was found"); return
        target = [f for f in files if f.endswith(".mp3" if format_choice == "audio" else ".mp4")]; chosen = target[0] if target else files[0]
        for f in files:
            if f != chosen:
                try: os.remove(f)
                except OSError: pass
        job["status"]="done"; job["file"]=chosen; ext=os.path.splitext(chosen)[1]; title=job.get("title","").strip(); safe_title="".join(c for c in title if c not in r'\/:*?"<>|').strip()[:100].strip(); job["filename"]=f"{safe_title}{ext}" if safe_title else os.path.basename(chosen)
    except subprocess.TimeoutExpired: job.update(status="error", error="Download timed out (5 min limit)")
    except Exception as e: job.update(status="error", error=str(e))

@app.route("/")
def index():
    html = render_template("index.html")
    return html.replace("</head>", '<link rel="stylesheet" href="/static/kage-theme.css">\n</head>', 1)

@app.route("/supported")
def supported():
    return render_template("supported.html", sites=SUPPORTED_SITES)

@app.route("/api/info", methods=["POST"])
def get_info():
    data=request.json or {}; url=data.get("url","").strip()
    if not url:return jsonify({"error":"No URL provided"}),400
    try:
        result=subprocess.run(["yt-dlp","--no-playlist","-j",url],capture_output=True,text=True,timeout=60)
        if result.returncode!=0:return jsonify({"error":result.stderr.strip().split("\n")[-1]}),400
        info=parse_ytdlp_json(result.stdout); best={}
        for f in info.get("formats",[]):
            h=f.get("height")
            if h and f.get("vcodec","none")!="none" and (h not in best or (f.get("tbr") or 0)>(best[h].get("tbr") or 0)):best[h]=f
        formats=[{"id":f["format_id"],"label":f"{h}p","height":h} for h,f in best.items()];formats.sort(key=lambda x:x["height"],reverse=True)
        return jsonify({"title":info.get("title",""),"thumbnail":info.get("thumbnail",""),"duration":info.get("duration"),"uploader":info.get("uploader",""),"formats":formats})
    except subprocess.TimeoutExpired:return jsonify({"error":"Timed out fetching video info"}),400
    except Exception as e:return jsonify({"error":str(e)}),400

@app.route("/api/playlist",methods=["POST"])
def get_playlist_info():
    data=request.json or {};url=data.get("url","").strip()
    if not url:return jsonify({"error":"No URL provided"}),400
    try:
        result=subprocess.run(["yt-dlp","--flat-playlist","-J",url],capture_output=True,text=True,timeout=60)
        if result.returncode!=0:return jsonify({"error":result.stderr.strip().split("\n")[-1]}),400
        info=json.loads(result.stdout);return jsonify({"urls":[e.get("url") for e in info.get("entries",[]) if e.get("url")]})
    except subprocess.TimeoutExpired:return jsonify({"error":"Timed out fetching playlist info"}),400
    except Exception as e:return jsonify({"error":str(e)}),400

@app.route("/api/download",methods=["POST"])
def start_download():
    data=request.json or {};url=data.get("url","").strip()
    if not url:return jsonify({"error":"No URL provided"}),400
    job_id=uuid.uuid4().hex[:10];jobs[job_id]={"status":"downloading","url":url,"title":data.get("title","")}
    threading.Thread(target=run_download,args=(job_id,url,data.get("format","video"),data.get("format_id")),daemon=True).start();return jsonify({"job_id":job_id})

@app.route("/api/status/<job_id>")
def check_status(job_id):
    job=jobs.get(job_id)
    if not job:return jsonify({"error":"Job not found"}),404
    return jsonify({"status":job["status"],"error":job.get("error"),"filename":job.get("filename")})

@app.route("/api/file/<job_id>")
def download_file(job_id):
    job=jobs.get(job_id)
    if not job or job["status"]!="done":return jsonify({"error":"File not ready"}),404
    return send_file(job["file"],as_attachment=True,download_name=job["filename"])

if __name__=="__main__":
    port=int(os.environ.get("PORT",8899));host=os.environ.get("HOST","127.0.0.1");app.run(host=host,port=port)

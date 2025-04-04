from flask import Flask, request, render_template, redirect, url_for, flash
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key for production

def is_fair_use(info):
    """
    Checks if the video is available for reuse.
    For this example, we assume that a Creative Commons license means it's acceptable.
    """
    license_str = info.get("license", "")
    return "Creative Commons" in license_str

def download_clip(clip_url):
    # Create a downloads folder if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clip_url, download=False)
            
            if not is_fair_use(info):
                return None, "Video is not available under a fair use license (Creative Commons)."
            
            ydl.download([clip_url])
            downloaded_file = os.path.join("downloads", f"{info.get('title')}.{info.get('ext', 'mp4')}")
            return downloaded_file, None
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        clip_url = request.form.get('clip_url')
        if not clip_url:
            flash("Please provide a valid URL.")
            return redirect(url_for('index'))
        
        file_path, error = download_clip(clip_url)
        if error:
            flash(f"Error: {error}")
        else:
            flash(f"Download complete! File saved as: {file_path}")
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    # Glitch uses the PORT environment variable.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

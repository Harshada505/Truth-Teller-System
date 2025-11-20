import yt_dlp
import os
from werkzeug.utils import secure_filename

def download_youtube_video_480p(url, output_folder):
    output_folder = os.path.expanduser("~/YTdownloads")
    os.makedirs(output_folder, exist_ok=True)

    # We'll first get video info (without download)
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')

        # Sanitize and shorten title
        safe_title = secure_filename(video_title)[:50]

        # Now set output template with the safe title
        ydl_opts = {
            'format': 'best[height<=480][ext=mp4]/best[ext=mp4]',
            'outtmpl': os.path.join(output_folder, f"{safe_title}.mp4"),
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_path = os.path.join(output_folder, f"{safe_title}.mp4")

        return video_path, safe_title

    except yt_dlp.utils.DownloadError as e:
        print("Download error:", str(e))
        return None, None
    except Exception as e:
        print("General error:", str(e))
        return None, None

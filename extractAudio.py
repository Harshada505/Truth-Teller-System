import os
import uuid
from moviepy.editor import VideoFileClip

def extractAudio(filename, file_path):
    """
    Extracts audio from the given video file and saves it as a WAV file.
    Returns the path to the saved audio file or None if failed.
    """
    # Generate a unique audio filename
    audio_filename = f"{os.path.splitext(filename)[0]}_{uuid.uuid4().hex}.wav"
    output_dir = "uploads/audio"
    os.makedirs(output_dir, exist_ok=True)  # Ensure audio directory exists
    output_audio_path = os.path.join(output_dir, audio_filename)

    # Normalize the path for Windows compatibility
    output_audio_path = os.path.normpath(output_audio_path)

    # Remove existing file with same name (just in case)
    if os.path.exists(output_audio_path):
        try:
            os.remove(output_audio_path)
        except PermissionError:
            print(f"[Audio Extraction Error] Permission denied while removing existing file: {output_audio_path}")
            return None

    try:
        video_clip = VideoFileClip(file_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_path)
        video_clip.close()
        audio_clip.close()
        return output_audio_path
    except Exception as e:
        print("[Audio Extraction Error]", str(e))
        return None

import os
import uuid
import whisper
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

r = sr.Recognizer()

# Google-based transcription (for Hindi)
def transcribe_with_google(audio_path, lang='hi-IN'):
    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
        try:
            return r.recognize_google(audio_data, language=lang)
        except Exception as e:
            print(f"[Google SR Error] {e}")
            return ""

# Whisper-based transcription (for English)
def transcribe_with_whisper(audio_path):
    model = whisper.load_model("base")  # You can change to "small", "medium", etc.
    result = model.transcribe(audio_path)
    return result['text'].split(". ")  # Rough sentence splitting

# For Hindi: split and transcribe each chunk with Google SR
def get_large_audio_transcription_google(path, language="hi-IN"):
    folder = "uploads/audio_chunks"
    os.makedirs(folder, exist_ok=True)

    # Clean previous chunks
    for f in os.listdir(folder):
        if f.endswith(".wav"):
            try:
                os.remove(os.path.join(folder, f))
            except:
                pass

    sound = AudioSegment.from_file(path)
    chunks = split_on_silence(
        sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS - 14,
        keep_silence=300,
    )

    results = []
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(folder, f"chunk_{uuid.uuid4().hex}.wav")
        chunk.export(chunk_path, format="wav")
        text = transcribe_with_google(chunk_path, lang=language)
        if text:
            results.append(text.capitalize())
    return results

# Unified interface
def get_large_audio_transcription(path, language="en"):
    """
    language = 'en' → use Whisper
    language = 'hi' → use Google Speech Recognition
    """
    if language.lower().startswith("en"):
        print("🔊 Using Whisper for English transcription...")
        return transcribe_with_whisper(path)
    else:
        print("🗣️ Using Google Speech Recognition for Hindi transcription...")
        return get_large_audio_transcription_google(path, language="hi-IN")

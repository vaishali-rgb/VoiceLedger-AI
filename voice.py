import os
import requests
import base64
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, WISPR_API_KEY

os.makedirs("audio", exist_ok=True)
AUDIO_PATH = "audio/temp_recording.wav"

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-flash-lite-latest"


def save_audio_bytes(audio_bytes):
    """Save audio bytes directly from browser mic recording to file."""
    with open(AUDIO_PATH, "wb") as f:
        f.write(audio_bytes)
    return AUDIO_PATH


def transcribe_with_gemini(audio_path, language="hi"):
    """
    Direct multimodal audio transcription using Gemini 3.8 Flash!
    Processes browser audio bytes directly without needing wave/pyaudio headers.
    Supports Hindi, Gujarati, English, and code-mixed speech.
    """
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        lang_name = "Hindi" if language == "hi" else ("Gujarati" if language == "gu" else "English")
        
        prompt = (
            f"You are a precise speech-to-text transcriber for an Indian Kirana business app. "
            f"Listen to this audio carefully and transcribe exactly what was spoken in {lang_name} or Hinglish/vernacular. "
            f"Return ONLY the plain transcribed text sentence. Do not add quotes, explanations, or punctuation summaries."
        )

        # First attempt as audio/wav
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    ),
                    prompt
                ]
            )
            text = response.text.strip() if response.text else ""
            if text:
                return text
        except Exception:
            pass

        # Second attempt as audio/webm
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/webm"
                    ),
                    prompt
                ]
            )
            text = response.text.strip() if response.text else ""
            if text:
                return text
        except Exception:
            pass

        # Third attempt as audio/mp3
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/mp3"
                ),
                prompt
            ]
        )
        return response.text.strip() if response.text else ""

    except Exception as e:
        print(f"Gemini audio transcription error: {e}")
        return None


def process_audio_file(audio_path, language_code="hi"):
    """
    Process audio using Gemini direct multimodal audio engine.
    Fast, robust, handles all browser audio codecs natively!
    """
    return transcribe_with_gemini(audio_path, language=language_code)

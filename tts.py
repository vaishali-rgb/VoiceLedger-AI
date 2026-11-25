from gtts import gTTS
import tempfile
import os
import subprocess
import sys


def speak(text: str, language: str = "hi"):
    """
    Convert text → speech and play it.
    Uses Windows built-in media player — no pygame/playsound needed.
    Falls back to printing if audio fails.
    language: 'hi' = Hindi, 'gu' = Gujarati, 'en' = English
    """
    if not text:
        return

    gtts_lang_map = {"hi": "hi", "gu": "hi", "en": "en"}
    gtts_lang = gtts_lang_map.get(language, "hi")

    try:
        tts = gTTS(text=text, lang=gtts_lang, slow=False)

        # Save to a temp mp3 file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp.name
        tmp.close()
        tts.save(tmp_path)

        # Play using Windows built-in PowerShell media player (no install needed)
        subprocess.run(
            [
                "powershell", "-c",
                f"(New-Object Media.SoundPlayer).PlaySync(); "
                f"Add-Type -AssemblyName presentationCore; "
                f"$mp = New-Object System.Windows.Media.MediaPlayer; "
                f"$mp.Open([System.Uri]'{tmp_path}'); "
                f"$mp.Play(); Start-Sleep -Seconds 4; $mp.Stop()"
            ],
            capture_output=True, timeout=15
        )

        try:
            os.remove(tmp_path)
        except Exception:
            pass

    except Exception as e:
        print(f"🔇  TTS error: {e}")
        print(f"[VoiceLedger says]: {text}")


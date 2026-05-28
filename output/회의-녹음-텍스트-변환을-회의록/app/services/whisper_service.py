import os
import tempfile
from pathlib import Path

import whisper


_model: whisper.Whisper | None = None


def _get_model() -> whisper.Whisper:
    global _model
    if _model is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        _model = whisper.load_model(model_name)
    return _model


def transcribe_audio(audio_path: Path) -> dict:
    model = _get_model()
    result = model.transcribe(str(audio_path), language="ko", task="transcribe")
    return {
        "transcript": result["text"].strip(),
        "language": result.get("language", "ko"),
        "segments": [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"].strip()}
            for seg in result.get("segments", [])
        ],
    }

"""Audio transcriber using OpenAI Whisper (local model)."""

import math
from pathlib import Path

import whisper

from .models import AudioResult, AudioSegment


def transcribe_audio(
    audio_path: Path,
    model_size: str = "base",
    language: str | None = None,
) -> AudioResult:
    """Transcribe audio to text using Whisper.

    Args:
        audio_path: Path to WAV audio file (16kHz, mono).
        model_size: Whisper model size: "tiny", "base", "small", "medium", "large".
        language: Optional ISO 639-1 language code (e.g., "te", "hi", "ta").
                  If None, Whisper auto-detects.

    Returns:
        AudioResult with transcribed segments and confidence score.

    Raises:
        FileNotFoundError: If audio file does not exist.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    transcribe_kwargs: dict = {
        "fp16": False,  # CPU-safe
    }
    if language is not None:
        transcribe_kwargs["language"] = language

    print(f"Transcribing audio: {audio_path}")
    result = model.transcribe(str(audio_path), **transcribe_kwargs)

    segments = []
    for seg in result.get("segments", []):
        avg_logprob = seg.get("avg_logprob", -1.0)
        no_speech_prob = seg.get("no_speech_prob", 1.0)

        # Convert log probability to confidence (0-1)
        seg_confidence = min(1.0, max(0.0, math.exp(avg_logprob)))

        # Skip segments that are likely silence/noise
        if no_speech_prob > 0.8:
            continue

        segments.append(
            AudioSegment(
                text=seg["text"].strip(),
                start=float(seg["start"]),
                end=float(seg["end"]),
                confidence=round(seg_confidence, 3),
            )
        )

    # Overall confidence: average of segment confidences
    if segments:
        overall_confidence = sum(s.confidence for s in segments) / len(segments)
    else:
        overall_confidence = 0.0

    detected_language = result.get("language", language or "unknown")

    print(f"  Transcribed {len(segments)} segments, confidence={overall_confidence:.2f}")

    return AudioResult(
        segments=segments,
        language=detected_language,
        confidence=round(overall_confidence, 3),
    )

"""Visual text analyzer using LLaVA multimodal model."""

from pathlib import Path

from PIL import Image

from .models import VisualFrame, VisualResult

# Module-level pipeline cache
_pipeline = None

# Phrases that indicate LLaVA found no meaningful text
_NO_TEXT_PHRASES = [
    "no text",
    "no visible text",
    "i don't see any text",
    "there is no text",
    "cannot identify any text",
    "image does not contain",
]


def _load_pipeline(model_name: str = "llava-hf/llava-1.5-7b-hf"):
    """Load (and cache) the LLaVA pipeline.

    Uses transformers pipeline API for simplicity.
    The model is loaded once and reused across calls.
    """
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    from transformers import pipeline

    print(f"Loading LLaVA model: {model_name}")
    _pipeline = pipeline(
        "image-to-text",
        model=model_name,
        device_map="auto",
    )
    return _pipeline


def _is_meaningful_text(text: str) -> bool:
    """Check if extracted text is meaningful (not a "no text found" response)."""
    text_lower = text.lower().strip()
    if not text_lower:
        return False
    for phrase in _NO_TEXT_PHRASES:
        if phrase in text_lower:
            return False
    return True


def _analyze_single_frame(
    pipe,
    frame_path: Path,
    frame_index: int,
    timestamp: float,
) -> VisualFrame:
    """Analyze a single frame for text content."""
    image = Image.open(frame_path).convert("RGB")

    prompt = (
        "Extract all text visible in this image. "
        "Return only the text content, nothing else. "
        "If there is no text, say 'No text visible'."
    )

    try:
        result = pipe(image, prompt=prompt, generate_kwargs={"max_new_tokens": 200})
        generated = result[0].get("generated_text", "").strip()

        if _is_meaningful_text(generated):
            confidence = 0.9  # High confidence when text is detected
        else:
            generated = ""
            confidence = 0.1  # Low confidence when no text found
    except Exception as e:
        print(f"  Warning: Frame {frame_index} analysis failed: {e}")
        generated = ""
        confidence = 0.0

    return VisualFrame(
        frame_index=frame_index,
        timestamp=timestamp,
        text=generated,
        confidence=confidence,
    )


def analyze_frames(
    frame_paths: list[Path],
    frame_rate: int = 1,
    model_name: str = "llava-hf/llava-1.5-7b-hf",
) -> VisualResult:
    """Analyze video frames for on-screen text using LLaVA.

    Args:
        frame_paths: List of paths to extracted JPEG frames.
        frame_rate: Frames per second (used to compute timestamps).
        model_name: HuggingFace model identifier for LLaVA.

    Returns:
        VisualResult with per-frame text and overall confidence.
    """
    if not frame_paths:
        return VisualResult(frames=[], confidence=0.0)

    pipe = _load_pipeline(model_name)

    frames: list[VisualFrame] = []
    for i, frame_path in enumerate(frame_paths):
        timestamp = float(i) / frame_rate
        print(f"  Analyzing frame {i + 1}/{len(frame_paths)} ({timestamp:.1f}s)...")
        frame = _analyze_single_frame(pipe, frame_path, i, timestamp)
        frames.append(frame)

    # Overall confidence: average of frames that had text, or 0 if none
    text_frames = [f for f in frames if f.text]
    if text_frames:
        overall_confidence = sum(f.confidence for f in text_frames) / len(text_frames)
    else:
        overall_confidence = 0.0

    return VisualResult(
        frames=frames,
        confidence=round(overall_confidence, 3),
    )

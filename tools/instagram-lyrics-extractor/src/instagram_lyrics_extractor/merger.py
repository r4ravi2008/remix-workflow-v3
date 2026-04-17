"""Confidence-weighted merger for visual + audio results."""

from .models import (
    AudioResult,
    LineTimestamp,
    MergedResult,
    VisualResult,
    WordTimestamp,
)


def _visual_to_lines(visual: VisualResult) -> list[LineTimestamp]:
    """Convert visual frames with text into LineTimestamp entries."""
    lines = []
    for frame in visual.frames:
        if not frame.text:
            continue
        lines.append(
            LineTimestamp(
                text=frame.text.strip(),
                start=frame.timestamp,
                end=frame.timestamp + 1.0,
                words=[],
            )
        )
    return lines


def _audio_to_lines(audio: AudioResult) -> list[LineTimestamp]:
    """Convert audio segments into LineTimestamp entries with word-level data."""
    lines = []
    for seg in audio.segments:
        text = seg.text.strip()
        if not text:
            continue

        words_raw = text.split()
        duration = seg.end - seg.start
        word_duration = duration / len(words_raw) if words_raw else 0

        words = []
        for i, word_text in enumerate(words_raw):
            w_start = seg.start + i * word_duration
            w_end = w_start + word_duration
            words.append(
                WordTimestamp(
                    text=word_text,
                    start=round(w_start, 3),
                    end=round(w_end, 3),
                )
            )

        lines.append(
            LineTimestamp(
                text=text,
                start=seg.start,
                end=seg.end,
                words=words,
            )
        )
    return lines


def _normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip whitespace)."""
    return " ".join(text.lower().split())


def _deduplicate_lines(lines: list[LineTimestamp]) -> list[LineTimestamp]:
    """Remove duplicate lines that overlap in time and text."""
    if not lines:
        return []

    sorted_lines = sorted(lines, key=lambda l: l.start)
    deduplicated = [sorted_lines[0]]

    for line in sorted_lines[1:]:
        prev = deduplicated[-1]
        prev_norm = _normalize_text(prev.text)
        curr_norm = _normalize_text(line.text)

        if prev_norm == curr_norm and abs(line.start - prev.start) < 2.0:
            if len(line.words) > len(prev.words):
                deduplicated[-1] = line
            continue

        deduplicated.append(line)

    return deduplicated


def merge_results(visual: VisualResult, audio: AudioResult) -> MergedResult:
    """Merge visual and audio results with confidence weighting."""
    visual_lines = _visual_to_lines(visual)
    audio_lines = _audio_to_lines(audio)

    has_visual = len(visual_lines) > 0 and visual.confidence > 0.3
    has_audio = len(audio_lines) > 0 and audio.confidence > 0.3

    if has_visual and has_audio:
        source = "both"
        all_lines = visual_lines + audio_lines
        combined = _deduplicate_lines(all_lines)
        confidence = visual.confidence * 0.4 + audio.confidence * 0.6
    elif has_visual:
        source = "visual"
        combined = visual_lines
        confidence = visual.confidence
    elif has_audio:
        source = "audio"
        combined = audio_lines
        confidence = audio.confidence
    else:
        source = "audio"
        if audio_lines:
            combined = audio_lines
            confidence = audio.confidence
        elif visual_lines:
            combined = visual_lines
            confidence = visual.confidence
            source = "visual"
        else:
            combined = []
            confidence = 0.0

    language = audio.language if audio.language else "unknown"

    return MergedResult(
        lines=combined,
        confidence=round(confidence, 3),
        source=source,
        language=language,
    )

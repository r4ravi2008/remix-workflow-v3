"""Tests for output formatter (plain text + timestamped JSON)."""

import json
import pytest
from pathlib import Path
from instagram_lyrics_extractor.formatter import format_plain_text, format_timestamped_json, write_outputs
from instagram_lyrics_extractor.models import (
    MergedResult,
    LineTimestamp,
    WordTimestamp,
)


def _make_merged() -> MergedResult:
    """Create a sample MergedResult for testing."""
    return MergedResult(
        lines=[
            LineTimestamp(
                text="first line of lyrics",
                start=0.0,
                end=2.5,
                words=[
                    WordTimestamp(text="first", start=0.0, end=0.5),
                    WordTimestamp(text="line", start=0.5, end=1.0),
                    WordTimestamp(text="of", start=1.0, end=1.3),
                    WordTimestamp(text="lyrics", start=1.3, end=2.5),
                ],
            ),
            LineTimestamp(
                text="second line here",
                start=3.0,
                end=5.0,
                words=[
                    WordTimestamp(text="second", start=3.0, end=3.8),
                    WordTimestamp(text="line", start=3.8, end=4.2),
                    WordTimestamp(text="here", start=4.2, end=5.0),
                ],
            ),
        ],
        confidence=0.9,
        source="both",
        language="te",
    )


class TestFormatPlainText:
    def test_basic(self):
        merged = _make_merged()
        text = format_plain_text(merged)
        assert "first line of lyrics" in text
        assert "second line here" in text

    def test_lines_separated_by_newline(self):
        merged = _make_merged()
        text = format_plain_text(merged)
        lines = [l for l in text.strip().split("\n") if l.strip()]
        assert len(lines) == 2

    def test_empty_result(self):
        merged = MergedResult(lines=[], confidence=0.0, source="audio", language="te")
        text = format_plain_text(merged)
        assert text.strip() == ""


class TestFormatTimestampedJson:
    def test_has_required_keys(self):
        merged = _make_merged()
        data = format_timestamped_json(merged, audio_duration=10.0)
        assert "audio_duration" in data
        assert "lyrics" in data
        assert "sections" in data
        assert data["audio_duration"] == 10.0

    def test_lyrics_structure(self):
        merged = _make_merged()
        data = format_timestamped_json(merged, audio_duration=10.0)
        lyrics = data["lyrics"]
        assert len(lyrics) == 2
        first = lyrics[0]
        assert "text" in first
        assert "start_time" in first
        assert "end_time" in first
        assert "words" in first
        assert first["text"] == "first line of lyrics"

    def test_word_timestamps_present(self):
        merged = _make_merged()
        data = format_timestamped_json(merged, audio_duration=10.0)
        words = data["lyrics"][0]["words"]
        assert len(words) == 4
        assert words[0]["text"] == "first"
        assert words[0]["start_time"] == 0.0

    def test_empty_result(self):
        merged = MergedResult(lines=[], confidence=0.0, source="audio", language="te")
        data = format_timestamped_json(merged, audio_duration=5.0)
        assert data["lyrics"] == []
        assert data["audio_duration"] == 5.0


class TestWriteOutputs:
    def test_writes_both_files(self, tmp_path: Path):
        merged = _make_merged()
        text_path = tmp_path / "lyrics.txt"
        json_path = tmp_path / "lyrics-timestamps.json"
        write_outputs(merged, text_path, json_path, audio_duration=10.0)

        assert text_path.exists()
        assert json_path.exists()

        text_content = text_path.read_text(encoding="utf-8")
        assert "first line of lyrics" in text_content

        json_content = json.loads(json_path.read_text(encoding="utf-8"))
        assert len(json_content["lyrics"]) == 2

    def test_creates_parent_dirs(self, tmp_path: Path):
        merged = _make_merged()
        text_path = tmp_path / "sub" / "dir" / "lyrics.txt"
        json_path = tmp_path / "sub" / "dir" / "lyrics-timestamps.json"
        write_outputs(merged, text_path, json_path, audio_duration=10.0)
        assert text_path.exists()
        assert json_path.exists()

    def test_json_ensure_ascii_false(self, tmp_path: Path):
        """Ensure Indic characters are not escaped in JSON output."""
        merged = MergedResult(
            lines=[
                LineTimestamp(text="తెలుగు పాట", start=0.0, end=2.0, words=[]),
            ],
            confidence=0.9,
            source="audio",
            language="te",
        )
        json_path = tmp_path / "lyrics-timestamps.json"
        text_path = tmp_path / "lyrics.txt"
        write_outputs(merged, text_path, json_path, audio_duration=5.0)

        raw = json_path.read_text(encoding="utf-8")
        assert "తెలుగు" in raw  # Not escaped as \uXXXX

"""Tests for CLI entry point."""

from instagram_lyrics_extractor.cli import parse_args


class TestParseArgs:
    def test_required_video_arg(self):
        args = parse_args(["video.mp4"])
        assert args.video == "video.mp4"

    def test_default_output_dir(self):
        args = parse_args(["video.mp4"])
        assert args.output_dir == "."

    def test_custom_output_dir(self):
        args = parse_args(["video.mp4", "--output-dir", "/tmp/out"])
        assert args.output_dir == "/tmp/out"

    def test_language_flag(self):
        args = parse_args(["video.mp4", "--language", "te"])
        assert args.language == "te"

    def test_default_language_is_none(self):
        args = parse_args(["video.mp4"])
        assert args.language is None

    def test_frame_rate_flag(self):
        args = parse_args(["video.mp4", "--frame-rate", "2"])
        assert args.frame_rate == 2

    def test_default_frame_rate(self):
        args = parse_args(["video.mp4"])
        assert args.frame_rate == 1

    def test_whisper_model_flag(self):
        args = parse_args(["video.mp4", "--whisper-model", "small"])
        assert args.whisper_model == "small"

    def test_default_whisper_model(self):
        args = parse_args(["video.mp4"])
        assert args.whisper_model == "base"

    def test_default_mode(self):
        args = parse_args(["video.mp4"])
        assert args.mode == "both"

    def test_visual_mode_flag(self):
        args = parse_args(["video.mp4", "--mode", "visual"])
        assert args.mode == "visual"

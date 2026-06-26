import json
from pathlib import Path

import numpy as np

from acapella_extractor import prepare as prepare_module


def make_workspace(tmp_path: Path, slug: str = "bella-bella-lofi") -> Path:
    workspace = tmp_path / slug
    workspace.mkdir()
    (workspace / "meta.json").write_text(
        json.dumps({"slug": slug, "files": {}, "status": {}}),
        encoding="utf-8",
    )
    (workspace / f"{slug}-original.mp3").write_bytes(b"original")
    (workspace / f"{slug}-acapella.mp3").write_bytes(b"acapella")
    return workspace


def test_pitch_ratio_from_semitones():
    assert prepare_module.pitch_ratio_from_semitones(0) == 1
    assert round(prepare_module.pitch_ratio_from_semitones(12), 6) == 2
    assert round(prepare_module.pitch_ratio_from_semitones(-12), 6) == 0.5


def test_detect_key_candidates_ranks_matching_profile():
    chroma = np.repeat(prepare_module.MINOR_PROFILE.reshape(12, 1), 4, axis=1)

    candidates = prepare_module.detect_key_candidates(chroma, limit=1)

    assert candidates == [{"key": "C minor", "confidence": 1.0}]


def test_prepare_defaults_to_detected_bpm_and_preserves_pitch(monkeypatch, tmp_path):
    workspace = make_workspace(tmp_path)
    calls = []

    monkeypatch.setattr(
        prepare_module,
        "analyze_audio",
        lambda path: prepare_module.AudioAnalysis(
            detected_bpm=89.1,
            key_candidates=[{"key": "D minor", "confidence": 0.97}],
        ),
    )

    def fake_runner(command, check):
        calls.append(command)
        Path(command[-1]).write_bytes(b"prepped")

    result = prepare_module.prepare_acapella(
        workspace,
        "bella-bella-lofi",
        runner=fake_runner,
    )

    assert (
        result.output_audio
        == workspace.resolve() / "bella-bella-lofi-acapella-prepped.mp3"
    )
    assert result.report["detected_bpm"] == 89.1
    assert result.report["target_bpm"] == 89.1
    assert result.report["tempo_ratio"] == 1.0
    assert result.report["pitch_semitones"] == 0.0
    assert result.report["pitch_ratio"] == 1.0
    assert "-af" not in calls[0]

    meta = json.loads((workspace / "meta.json").read_text(encoding="utf-8"))
    assert (
        meta["files"]["acapella_prepped"]
        == "bella-bella-lofi/bella-bella-lofi-acapella-prepped.mp3"
    )
    assert (
        meta["files"]["acapella_prep_report"]
        == "bella-bella-lofi/bella-bella-lofi-acapella-prep.json"
    )
    assert meta["status"]["acapella_prepped"] is True
    assert meta["audio_analysis"] == {
        "detected_bpm": 89.1,
        "target_bpm": 89.1,
        "detected_key": "D minor",
        "pitch_semitones": 0.0,
    }


def test_prepare_applies_explicit_target_bpm_and_pitch(monkeypatch, tmp_path):
    workspace = make_workspace(tmp_path)
    calls = []

    monkeypatch.setattr(
        prepare_module,
        "analyze_audio",
        lambda path: prepare_module.AudioAnalysis(
            detected_bpm=100.0,
            key_candidates=[{"key": "A minor", "confidence": 0.94}],
        ),
    )

    def fake_runner(command, check):
        calls.append(command)
        Path(command[-1]).write_bytes(b"prepped")

    result = prepare_module.prepare_acapella(
        workspace,
        "bella-bella-lofi",
        target_bpm=125,
        pitch_semitones=-2,
        runner=fake_runner,
    )

    assert result.report["tempo_ratio"] == 1.25
    assert result.report["pitch_ratio"] == round(2 ** (-2 / 12), 8)
    filter_index = calls[0].index("-af") + 1
    assert "rubberband=tempo=1.25000000" in calls[0][filter_index]
    assert "formant=preserved" in calls[0][filter_index]
    assert "pitchq=quality" in calls[0][filter_index]


def test_build_rubberband_filter_formats_ratios():
    assert prepare_module.build_rubberband_filter(1.25, 0.8908987) == (
        "rubberband=tempo=1.25000000:pitch=0.89089870:formant=preserved:pitchq=quality"
    )

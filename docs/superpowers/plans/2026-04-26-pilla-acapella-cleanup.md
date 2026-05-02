# Pilla Acapella Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate reversible cleaned vocal candidates for the original `Pilla Ayithey Keka Undhi` acapella and leave a clear path to promote the workflow into the acapella toolbox.

**Architecture:** Add a small local cleanup module under `tools/acapella-extractor` that wraps deterministic FFmpeg filters into named presets. Use it immediately against the workspace stem to create light, medium, and strong candidates plus a manifest, without mutating existing workspace files or `meta.json`.

**Tech Stack:** Python 3.12, FFmpeg, pytest, existing `tools/acapella-extractor` package.

---

## File Structure

- Create `tools/acapella-extractor/src/acapella_extractor/clean.py`: reusable cleanup module and CLI for preset filter chains, output naming, manifest writing, and FFmpeg invocation.
- Create `tools/acapella-extractor/tests/test_clean.py`: unit tests for preset definitions, output naming, FFmpeg command construction, and manifest content.
- Modify `tools/acapella-extractor/pyproject.toml`: add an optional console script entry point `acapella-clean` for future toolbox use.
- Create workspace outputs under `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/`: three cleaned MP3 candidates and `vocal-cleanup-settings.json`.

## Task 1: Add Cleanup Command Surface

**Files:**
- Create: `tools/acapella-extractor/tests/test_clean.py`
- Create: `tools/acapella-extractor/src/acapella_extractor/clean.py`
- Modify: `tools/acapella-extractor/pyproject.toml`

- [ ] **Step 1: Write failing tests for presets, output names, and command construction**

Create `tools/acapella-extractor/tests/test_clean.py` with this content:

```python
import json
from pathlib import Path

from acapella_extractor import clean as clean_module


def test_candidate_path_inserts_preset_before_extension(tmp_path):
    source = tmp_path / "song-acapella.mp3"

    result = clean_module.candidate_path(source, "medium")

    assert result == tmp_path / "song-acapella-cleaned-medium.mp3"


def test_build_ffmpeg_command_uses_expected_filter_and_bitrate(tmp_path):
    source = tmp_path / "song-acapella.mp3"
    output = tmp_path / "song-acapella-cleaned-light.mp3"

    command = clean_module.build_ffmpeg_command(source, output, "light")

    assert command[:4] == ["ffmpeg", "-y", "-i", str(source)]
    assert "-af" in command
    assert "highpass=f=90" in command
    assert "loudnorm=I=-16:TP=-1.5:LRA=11" in command
    assert command[-4:] == ["-codec:a", "libmp3lame", "-b:a", "192k"] + [str(output)]


def test_clean_candidates_writes_manifest(monkeypatch, tmp_path):
    source = tmp_path / "song-acapella.mp3"
    source.write_bytes(b"audio")
    commands = []

    def fake_run(command, check):
        commands.append(command)
        Path(command[-1]).write_bytes(b"cleaned")

    monkeypatch.setattr(clean_module.subprocess, "run", fake_run)

    outputs = clean_module.clean_candidates(source, ["light", "medium"])

    assert outputs == [
        tmp_path / "song-acapella-cleaned-light.mp3",
        tmp_path / "song-acapella-cleaned-medium.mp3",
    ]
    assert len(commands) == 2
    assert all(path.exists() for path in outputs)

    manifest = json.loads((tmp_path / "vocal-cleanup-settings.json").read_text())
    assert manifest["input"] == str(source)
    assert [item["preset"] for item in manifest["outputs"]] == ["light", "medium"]
    assert manifest["outputs"][0]["path"] == str(outputs[0])
```

- [ ] **Step 2: Run tests to verify they fail**

Run from the repository root:

```bash
PYTHONPATH=tools/acapella-extractor/src uv run --python tools/acapella-extractor/.venv/bin/python pytest tools/acapella-extractor/tests/test_clean.py -v
```

Expected: FAIL because `acapella_extractor.clean` does not exist yet.

- [ ] **Step 3: Implement the cleanup module**

Create `tools/acapella-extractor/src/acapella_extractor/clean.py` with this content:

```python
#!/usr/bin/env python3
"""Clean extracted vocal stems with deterministic FFmpeg filter presets."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


PRESETS: dict[str, str] = {
    "light": ",".join(
        [
            "highpass=f=90",
            "lowpass=f=14500",
            "equalizer=f=250:t=q:w=1.1:g=-1.5",
            "equalizer=f=3200:t=q:w=1.0:g=1.5",
            "acompressor=threshold=-22dB:ratio=1.8:attack=15:release=180:makeup=1",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
        ]
    ),
    "medium": ",".join(
        [
            "highpass=f=120",
            "lowpass=f=12500",
            "equalizer=f=250:t=q:w=1.2:g=-3",
            "equalizer=f=450:t=q:w=1.0:g=-1.5",
            "equalizer=f=3500:t=q:w=1.0:g=2",
            "acompressor=threshold=-24dB:ratio=2.4:attack=12:release=140:makeup=1.5",
            "afftdn=nf=-28:tn=1",
            "loudnorm=I=-16:TP=-1.5:LRA=10",
        ]
    ),
    "strong": ",".join(
        [
            "highpass=f=150",
            "lowpass=f=10500",
            "equalizer=f=220:t=q:w=1.3:g=-4.5",
            "equalizer=f=500:t=q:w=1.1:g=-2.5",
            "equalizer=f=3800:t=q:w=1.0:g=2.5",
            "acompressor=threshold=-26dB:ratio=3:attack=8:release=110:makeup=2",
            "afftdn=nf=-24:tn=1",
            "loudnorm=I=-16:TP=-1.5:LRA=9",
        ]
    ),
}


def candidate_path(input_path: Path, preset: str) -> Path:
    return input_path.with_name(f"{input_path.stem}-cleaned-{preset}.mp3")


def build_ffmpeg_command(input_path: Path, output_path: Path, preset: str) -> list[str]:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset '{preset}'. Expected one of: {', '.join(PRESETS)}")

    return [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-af",
        PRESETS[preset],
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(output_path),
    ]


def clean_candidates(input_path: Path, presets: list[str]) -> list[Path]:
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    outputs: list[Path] = []
    manifest_outputs = []

    for preset in presets:
        output_path = candidate_path(input_path, preset)
        command = build_ffmpeg_command(input_path, output_path, preset)
        subprocess.run(command, check=True)
        outputs.append(output_path)
        manifest_outputs.append(
            {
                "preset": preset,
                "path": str(output_path),
                "filter": PRESETS[preset],
                "command": command,
            }
        )

    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "input": str(input_path),
        "outputs": manifest_outputs,
    }
    manifest_path = input_path.parent / "vocal-cleanup-settings.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    return outputs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean an extracted vocal stem with FFmpeg presets")
    parser.add_argument("input", type=Path, help="Input vocal stem")
    parser.add_argument(
        "--preset",
        action="append",
        choices=sorted(PRESETS),
        dest="presets",
        help="Preset to generate. Repeat to generate multiple presets.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    presets = args.presets or ["light", "medium", "strong"]
    outputs = clean_candidates(args.input, presets)
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Add the future toolbox script entry point**

Modify `tools/acapella-extractor/pyproject.toml` so `[project.scripts]` becomes:

```toml
[project.scripts]
acapella-extract = "acapella_extractor.extract:main"
acapella-clean = "acapella_extractor.clean:main"
```

- [ ] **Step 5: Run tests to verify they pass**

Run:

```bash
PYTHONPATH=tools/acapella-extractor/src uv run --python tools/acapella-extractor/.venv/bin/python pytest tools/acapella-extractor/tests/test_clean.py -v
```

Expected: PASS for all tests in `test_clean.py`.

- [ ] **Step 6: Run existing extractor tests**

Run:

```bash
PYTHONPATH=tools/acapella-extractor/src uv run --python tools/acapella-extractor/.venv/bin/python pytest tools/acapella-extractor/tests -v
```

Expected: PASS for existing and new acapella-extractor tests.

## Task 2: Generate One-Off Cleaned Candidates

**Files:**
- Read: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella.mp3`
- Create: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-light.mp3`
- Create: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-medium.mp3`
- Create: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-strong.mp3`
- Create: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/vocal-cleanup-settings.json`

- [ ] **Step 1: Verify the input audio exists and capture its metadata**

Run:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella.mp3"
```

Expected: MP3, 44.1 kHz, stereo, about 179 seconds, 192 kbps.

- [ ] **Step 2: Generate the three candidates**

Run:

```bash
PYTHONPATH=tools/acapella-extractor/src uv run --python tools/acapella-extractor/.venv/bin/python python -m acapella_extractor.clean "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella.mp3"
```

Expected: command prints the three cleaned output paths and writes `vocal-cleanup-settings.json`.

- [ ] **Step 3: Verify candidate metadata**

Run this once per output file:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-light.mp3"
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-medium.mp3"
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-strong.mp3"
```

Expected: each file is MP3, 44.1 kHz, stereo or valid FFmpeg output channels, about 179 seconds, 192 kbps.

- [ ] **Step 4: Verify the manifest records exact commands**

Read `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/vocal-cleanup-settings.json` and confirm:

```json
{
  "input": "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella.mp3",
  "outputs": [
    {"preset": "light"},
    {"preset": "medium"},
    {"preset": "strong"}
  ]
}
```

The actual file also includes `created_at`, full output paths, filter strings, and full FFmpeg command arrays.

- [ ] **Step 5: Confirm the original input remains unchanged**

Run:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella.mp3"
```

Expected: same metadata as Task 2 Step 1.

## Task 3: Handoff For Listening Review

**Files:**
- Read: generated candidate MP3s
- Do not modify: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/meta.json`

- [ ] **Step 1: List the generated files for user review**

Run:

```bash
ls -lh "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-light.mp3" "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-medium.mp3" "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-strong.mp3" "workspaces/pilla-ayithey-keka-undhi-deep-house-trap/vocal-cleanup-settings.json"
```

Expected: all four files exist and have non-zero sizes.

- [ ] **Step 2: Report listening guidance**

Tell the user to compare these in order:

```text
1. cleaned-light: least artifact risk; may leave some room sound.
2. cleaned-medium: likely best first choice if the light version is still roomy.
3. cleaned-strong: use only if the echo is still distracting and artifacts are acceptable.
```

- [ ] **Step 3: Do not update pipeline state yet**

Confirm no changes were made to `meta.json`. The cleaned output should only replace or augment pipeline state after the user picks a candidate.

## Self-Review

- Spec coverage: The plan creates three reversible candidates, writes a manifest, preserves existing files, avoids `meta.json` mutation, and defines a feature path through `acapella_extractor.clean`.
- Placeholder scan: No placeholders, TBDs, or undefined behavior remain.
- Type consistency: The functions `candidate_path`, `build_ffmpeg_command`, `clean_candidates`, `parse_args`, and `main` are consistently named across tests and implementation steps.

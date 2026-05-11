# ACE-Step Local Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local ACE-Step generation backend that can replace Suno Step 5 while preserving the existing two-candidate remix contract.

**Architecture:** Add a focused Python tool under `tools/ace-step-generator/` that validates workspace inputs, builds ACE-Step generation parameters, optionally runs direct ACE-Step inference, normalizes candidate outputs, and writes a generation report. Add a new pipeline prompt for ACE-Step Step 5 and update docs to describe backend selection while leaving Suno and downstream steps intact.

**Tech Stack:** Python 3.12, pytest, ACE-Step Python inference API, FFmpeg for optional MP3 transcoding, existing Markdown prompt pipeline.

---

## File Structure

- Create `tools/ace-step-generator/pyproject.toml`: package metadata, pytest dev dependency, console script.
- Create `tools/ace-step-generator/ace_step_generator/__init__.py`: package marker and exported version.
- Create `tools/ace-step-generator/ace_step_generator/generate.py`: CLI, workspace validation, ACE-Step import/bootstrap, generation orchestration, output normalization, report writing.
- Create `tools/ace-step-generator/tests/test_generate.py`: unit tests for workspace loading, parameter building, output normalization, dry-run behavior, and report writing.
- Create `prompts/step-5-generate-with-ace-step.md`: agent-facing execution guide for the local backend.
- Modify `prompts/README.md`: document Step 5 backend choices.
- Modify `README.md`: add ACE-Step to tech stack and describe local generation path.
- Modify `prompts/references/workspace-conventions.md`: add ACE-Step metadata/file keys while preserving existing Suno keys.

---

### Task 1: Create ACE-Step Tool Skeleton And Workspace Validation

**Files:**
- Create: `tools/ace-step-generator/pyproject.toml`
- Create: `tools/ace-step-generator/ace_step_generator/__init__.py`
- Create: `tools/ace-step-generator/ace_step_generator/generate.py`
- Create: `tools/ace-step-generator/tests/test_generate.py`

- [ ] **Step 1: Write failing tests for workspace validation**

Create `tools/ace-step-generator/tests/test_generate.py` with:

```python
import json
from pathlib import Path

import pytest

from ace_step_generator import generate


def make_workspace(tmp_path: Path, slug: str = "bella-bella-lofi") -> Path:
    workspace = tmp_path / slug
    workspace.mkdir()
    (workspace / "meta.json").write_text(
        json.dumps(
            {
                "slug": slug,
                "genre": "Lo-Fi",
                "language": "Telugu",
                "tempo": "medium",
                "song_length": "full",
                "workspace": f"{slug}/",
                "files": {},
                "status": {},
            }
        ),
        encoding="utf-8",
    )
    (workspace / f"{slug}-lyrics.txt").write_text("పల్లవి\nచరణం\n", encoding="utf-8")
    (workspace / f"{slug}-suno-style.txt").write_text(
        "[lo-fi hip hop, nostalgic, Telugu, soft male vocal, 75 bpm]",
        encoding="utf-8",
    )
    (workspace / f"{slug}-acapella.mp3").write_bytes(b"fake audio")
    return workspace


def test_load_workspace_inputs_prefers_acapella(tmp_path):
    workspace = make_workspace(tmp_path)

    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")

    assert inputs.slug == "bella-bella-lofi"
    assert inputs.language == "Telugu"
    assert inputs.caption == "lo-fi hip hop, nostalgic, Telugu, soft male vocal, 75 bpm"
    assert inputs.lyrics == "పల్లవి\nచరణం"
    assert inputs.source_audio == workspace / "bella-bella-lofi-acapella.mp3"


def test_load_workspace_inputs_requires_original_approval_for_fallback(tmp_path):
    workspace = make_workspace(tmp_path)
    (workspace / "bella-bella-lofi-acapella.mp3").unlink()
    (workspace / "bella-bella-lofi-original.mp3").write_bytes(b"full mix")

    with pytest.raises(generate.GenerationError, match="Acapella is missing"):
        generate.load_workspace_inputs(workspace, "bella-bella-lofi")

    inputs = generate.load_workspace_inputs(
        workspace,
        "bella-bella-lofi",
        allow_original_fallback=True,
    )

    assert inputs.source_audio == workspace / "bella-bella-lofi-original.mp3"


def test_load_workspace_inputs_reports_missing_required_files(tmp_path):
    workspace = make_workspace(tmp_path)
    (workspace / "bella-bella-lofi-suno-style.txt").unlink()

    with pytest.raises(generate.GenerationError, match="Missing required file"):
        generate.load_workspace_inputs(workspace, "bella-bella-lofi")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: FAIL because `pyproject.toml` and `ace_step_generator` do not exist yet.

- [ ] **Step 3: Add package skeleton and workspace validation implementation**

Create `tools/ace-step-generator/pyproject.toml`:

```toml
[project]
name = "ace-step-generator"
version = "0.1.0"
description = "Generate local remix candidates with ACE-Step"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
ace-step-generate = "ace_step_generator.generate:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]
```

Create `tools/ace-step-generator/ace_step_generator/__init__.py`:

```python
__version__ = "0.1.0"
```

Create `tools/ace-step-generator/ace_step_generator/generate.py`:

```python
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


class GenerationError(RuntimeError):
    pass


@dataclass(frozen=True)
class WorkspaceInputs:
    workspace_dir: Path
    slug: str
    meta: dict
    language: str
    caption: str
    lyrics: str
    lyrics_file: Path
    style_file: Path
    source_audio: Path


def strip_style_brackets(style_text: str) -> str:
    text = style_text.strip()
    if text.startswith("[") and text.endswith("]"):
        return text[1:-1].strip()
    return text


def require_file(path: Path) -> Path:
    if not path.exists():
        raise GenerationError(f"Missing required file: {path}")
    return path


def load_workspace_inputs(
    workspace_dir: Path,
    slug: str,
    *,
    allow_original_fallback: bool = False,
) -> WorkspaceInputs:
    workspace_dir = workspace_dir.resolve()
    meta_path = require_file(workspace_dir / "meta.json")
    lyrics_file = require_file(workspace_dir / f"{slug}-lyrics.txt")
    style_file = require_file(workspace_dir / f"{slug}-suno-style.txt")

    with meta_path.open("r", encoding="utf-8") as file:
        meta = json.load(file)

    acapella = workspace_dir / f"{slug}-acapella.mp3"
    original = workspace_dir / f"{slug}-original.mp3"
    if acapella.exists():
        source_audio = acapella
    elif original.exists() and allow_original_fallback:
        source_audio = original
    elif original.exists():
        raise GenerationError(
            "Acapella is missing. Re-run Step 2 or pass --allow-original-fallback "
            "to use the full original mix."
        )
    else:
        raise GenerationError(f"Missing required file: {acapella}")

    caption = strip_style_brackets(style_file.read_text(encoding="utf-8"))
    lyrics = lyrics_file.read_text(encoding="utf-8").strip()

    return WorkspaceInputs(
        workspace_dir=workspace_dir,
        slug=slug,
        meta=meta,
        language=str(meta.get("language") or "unknown"),
        caption=caption,
        lyrics=lyrics,
        lyrics_file=lyrics_file,
        style_file=style_file,
        source_audio=source_audio,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate remix candidates with ACE-Step")
    parser.add_argument("--workspace-dir", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--ace-step-root", type=Path, default=None)
    parser.add_argument("--task-type", choices=["cover", "text2music"], default="cover")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--output-format", default="mp3")
    parser.add_argument("--allow-original-fallback", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_workspace_inputs(
        args.workspace_dir,
        args.slug,
        allow_original_fallback=args.allow_original_fallback,
    )
    if args.dry_run:
        return 0
    raise GenerationError("ACE-Step inference is not implemented yet")


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: PASS for all three tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly requested commits for this implementation session. If committing, run:

```bash
git add tools/ace-step-generator/pyproject.toml tools/ace-step-generator/ace_step_generator/__init__.py tools/ace-step-generator/ace_step_generator/generate.py tools/ace-step-generator/tests/test_generate.py
git commit -m "feat: add ace-step workspace validation"
```

---

### Task 2: Add Generation Parameter Building And Dry-Run Report

**Files:**
- Modify: `tools/ace-step-generator/ace_step_generator/generate.py`
- Modify: `tools/ace-step-generator/tests/test_generate.py`

- [ ] **Step 1: Write failing tests for parameter building and dry-run report**

Append to `tools/ace-step-generator/tests/test_generate.py`:

```python
def test_build_generation_request_defaults_to_cover(tmp_path):
    workspace = make_workspace(tmp_path)
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")

    request = generate.build_generation_request(
        inputs,
        task_type="cover",
        batch_size=2,
        output_format="mp3",
        audio_cover_strength=0.7,
        model="acestep-v15-turbo",
        lm_model=None,
    )

    assert request["task_type"] == "cover"
    assert request["src_audio"] == str(workspace / "bella-bella-lofi-acapella.mp3")
    assert request["caption"] == "lo-fi hip hop, nostalgic, Telugu, soft male vocal, 75 bpm"
    assert request["lyrics"] == "పల్లవి\nచరణం"
    assert request["vocal_language"] == "te"
    assert request["batch_size"] == 2
    assert request["audio_format"] == "mp3"
    assert request["audio_cover_strength"] == 0.7


def test_write_generation_report_uses_workspace_relative_paths(tmp_path):
    workspace = make_workspace(tmp_path)
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")
    outputs = [workspace / "bella-bella-lofi-remix-v1.mp3", workspace / "bella-bella-lofi-remix-v2.mp3"]
    for output in outputs:
        output.write_bytes(b"audio")

    report_path = generate.write_generation_report(
        inputs,
        request={"task_type": "cover", "batch_size": 2, "audio_cover_strength": 0.7},
        outputs=outputs,
        model="acestep-v15-turbo",
        lm_model=None,
        seeds=[123, 456],
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["backend"] == "ace-step"
    assert report["outputs"] == [
        "bella-bella-lofi/bella-bella-lofi-remix-v1.mp3",
        "bella-bella-lofi/bella-bella-lofi-remix-v2.mp3",
    ]
    assert report["source_audio"] == "bella-bella-lofi/bella-bella-lofi-acapella.mp3"
    assert report["seeds"] == [123, 456]


def test_dry_run_writes_report_without_audio_outputs(tmp_path):
    workspace = make_workspace(tmp_path)

    exit_code = generate.main([
        "--workspace-dir",
        str(workspace),
        "--slug",
        "bella-bella-lofi",
        "--dry-run",
    ])

    report = json.loads((workspace / "bella-bella-lofi-ace-step-generation.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["dry_run"] is True
    assert report["outputs"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: FAIL because `build_generation_request` and `write_generation_report` are not implemented.

- [ ] **Step 3: Implement request building and report writing**

Update `tools/ace-step-generator/ace_step_generator/generate.py` by adding these imports and functions after `load_workspace_inputs`:

```python
from datetime import UTC, datetime


LANGUAGE_TO_ACE = {
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "English": "en",
}


def workspace_relative(path: Path, workspace_dir: Path) -> str:
    relative = path.resolve().relative_to(workspace_dir.resolve())
    return f"{workspace_dir.name}/{relative.as_posix()}"


def build_generation_request(
    inputs: WorkspaceInputs,
    *,
    task_type: str,
    batch_size: int,
    output_format: str,
    audio_cover_strength: float,
    model: str,
    lm_model: str | None,
) -> dict:
    if batch_size < 1:
        raise GenerationError("--batch-size must be at least 1")

    request = {
        "task_type": task_type,
        "caption": inputs.caption,
        "lyrics": inputs.lyrics,
        "vocal_language": LANGUAGE_TO_ACE.get(inputs.language, "unknown"),
        "batch_size": batch_size,
        "audio_format": output_format,
        "model": model,
        "lm_model": lm_model,
    }

    if task_type == "cover":
        request.update(
            {
                "src_audio": str(inputs.source_audio),
                "audio_cover_strength": audio_cover_strength,
                "thinking": False,
            }
        )
    else:
        request["thinking"] = True

    return request


def write_generation_report(
    inputs: WorkspaceInputs,
    *,
    request: dict,
    outputs: list[Path],
    model: str,
    lm_model: str | None,
    seeds: list[int] | None = None,
    dry_run: bool = False,
) -> Path:
    report = {
        "backend": "ace-step",
        "task_type": request["task_type"],
        "model": model,
        "lm_model": lm_model,
        "source_audio": workspace_relative(inputs.source_audio, inputs.workspace_dir),
        "caption": inputs.caption,
        "lyrics_file": workspace_relative(inputs.lyrics_file, inputs.workspace_dir),
        "batch_size": request["batch_size"],
        "audio_cover_strength": request.get("audio_cover_strength"),
        "outputs": [workspace_relative(output, inputs.workspace_dir) for output in outputs],
        "seeds": seeds or [],
        "dry_run": dry_run,
        "created_at": datetime.now(UTC).isoformat(),
    }
    report_path = inputs.workspace_dir / f"{inputs.slug}-ace-step-generation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path
```

Update `build_parser()` to include:

```python
    parser.add_argument("--model", default="acestep-v15-turbo")
    parser.add_argument("--lm-model", default=None)
    parser.add_argument("--audio-cover-strength", type=float, default=0.7)
```

Update `main()` to build the request and write a dry-run report:

```python
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    inputs = load_workspace_inputs(
        args.workspace_dir,
        args.slug,
        allow_original_fallback=args.allow_original_fallback,
    )
    request = build_generation_request(
        inputs,
        task_type=args.task_type,
        batch_size=args.batch_size,
        output_format=args.output_format,
        audio_cover_strength=args.audio_cover_strength,
        model=args.model,
        lm_model=args.lm_model,
    )
    if args.dry_run:
        write_generation_report(
            inputs,
            request=request,
            outputs=[],
            model=args.model,
            lm_model=args.lm_model,
            dry_run=True,
        )
        return 0
    raise GenerationError("ACE-Step inference is not implemented yet")
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: PASS.

- [ ] **Step 5: Commit**

Only commit if explicitly requested. If committing, run:

```bash
git add tools/ace-step-generator/ace_step_generator/generate.py tools/ace-step-generator/tests/test_generate.py
git commit -m "feat: add ace-step generation request reports"
```

---

### Task 3: Add Output Normalization And ACE-Step Inference Adapter

**Files:**
- Modify: `tools/ace-step-generator/ace_step_generator/generate.py`
- Modify: `tools/ace-step-generator/tests/test_generate.py`

- [ ] **Step 1: Write failing tests for output normalization and fake inference**

Append to `tools/ace-step-generator/tests/test_generate.py`:

```python
def test_normalize_outputs_renames_generated_files(tmp_path):
    workspace = make_workspace(tmp_path)
    raw_1 = tmp_path / "raw-a.flac"
    raw_2 = tmp_path / "raw-b.mp3"
    raw_1.write_bytes(b"flac audio")
    raw_2.write_bytes(b"mp3 audio")

    outputs = generate.normalize_outputs(
        [raw_1, raw_2],
        workspace_dir=workspace,
        slug="bella-bella-lofi",
        output_format="mp3",
        transcode=False,
    )

    assert outputs == [
        workspace / "bella-bella-lofi-remix-v1.mp3",
        workspace / "bella-bella-lofi-remix-v2.mp3",
    ]
    assert outputs[0].read_bytes() == b"flac audio"
    assert outputs[1].read_bytes() == b"mp3 audio"


def test_run_generation_uses_injected_backend(tmp_path):
    workspace = make_workspace(tmp_path)
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")
    request = generate.build_generation_request(
        inputs,
        task_type="cover",
        batch_size=2,
        output_format="mp3",
        audio_cover_strength=0.7,
        model="acestep-v15-turbo",
        lm_model=None,
    )

    def fake_backend(*, inputs, request, ace_step_root, output_dir):
        first = output_dir / "candidate-a.mp3"
        second = output_dir / "candidate-b.mp3"
        first.write_bytes(b"one")
        second.write_bytes(b"two")
        return generate.GenerationResult(paths=[first, second], seeds=[11, 22])

    result = generate.run_generation(
        inputs,
        request=request,
        ace_step_root=tmp_path / "ACE-Step-1.5",
        backend=fake_backend,
    )

    assert [path.name for path in result.paths] == ["candidate-a.mp3", "candidate-b.mp3"]
    assert result.seeds == [11, 22]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: FAIL because `normalize_outputs`, `run_generation`, and `GenerationResult` are not implemented.

- [ ] **Step 3: Implement output normalization, backend adapter, and real ACE-Step call boundary**

Update imports in `generate.py`:

```python
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
```

Add after `WorkspaceInputs`:

```python
@dataclass(frozen=True)
class GenerationResult:
    paths: list[Path]
    seeds: list[int]
```

Add these functions after `write_generation_report`:

```python
def transcode_to_mp3(source: Path, destination: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(destination),
        ],
        check=True,
    )


def normalize_outputs(
    raw_outputs: list[Path],
    *,
    workspace_dir: Path,
    slug: str,
    output_format: str,
    transcode: bool = True,
) -> list[Path]:
    if not raw_outputs:
        raise GenerationError("ACE-Step did not produce any audio files")

    normalized = []
    for index, raw_output in enumerate(raw_outputs[:2], start=1):
        destination = workspace_dir / f"{slug}-remix-v{index}.{output_format}"
        if output_format == "mp3" and raw_output.suffix.lower() != ".mp3" and transcode:
            transcode_to_mp3(raw_output, destination)
        else:
            shutil.copyfile(raw_output, destination)
        normalized.append(destination)

    return normalized


def default_ace_step_backend(
    *,
    inputs: WorkspaceInputs,
    request: dict,
    ace_step_root: Path,
    output_dir: Path,
) -> GenerationResult:
    if not ace_step_root.exists():
        raise GenerationError(f"ACE-Step root does not exist: {ace_step_root}")

    sys.path.insert(0, str(ace_step_root.resolve()))
    try:
        from acestep.handler import AceStepHandler
        from acestep.inference import GenerationConfig, GenerationParams, generate_music
        from acestep.llm_inference import LLMHandler
    except ImportError as error:
        raise GenerationError(
            "Could not import ACE-Step. From tools/ace-step-generator, run "
            "`uv pip install -e /path/to/ACE-Step-1.5` so ACE-Step and its "
            "dependencies are installed in this tool environment, then pass "
            "--ace-step-root /path/to/ACE-Step-1.5."
        ) from error

    dit_handler = AceStepHandler()
    dit_handler.initialize_service(
        project_root=str(ace_step_root.resolve()),
        config_path=request["model"],
        device="auto",
    )

    llm_handler = None
    if request["task_type"] == "text2music" and request.get("lm_model"):
        llm_handler = LLMHandler()
        llm_handler.initialize(
            checkpoint_dir=str(ace_step_root.resolve()),
            lm_model_path=request["lm_model"],
            backend="pt",
            device="auto",
        )

    params = GenerationParams(
        task_type=request["task_type"],
        caption=request["caption"],
        lyrics=request["lyrics"],
        vocal_language=request["vocal_language"],
        src_audio=request.get("src_audio"),
        audio_cover_strength=request.get("audio_cover_strength", 1.0),
        thinking=bool(request.get("thinking", False)),
    )
    config = GenerationConfig(
        batch_size=request["batch_size"],
        audio_format=request["audio_format"],
    )
    result = generate_music(dit_handler, llm_handler, params, config, save_dir=str(output_dir))
    if not result.success:
        raise GenerationError(result.error or result.status_message or "ACE-Step generation failed")

    paths = [Path(audio["path"]) for audio in result.audios]
    seeds = [int(audio.get("params", {}).get("seed", -1)) for audio in result.audios]
    return GenerationResult(paths=paths, seeds=seeds)


def run_generation(
    inputs: WorkspaceInputs,
    *,
    request: dict,
    ace_step_root: Path,
    backend: Callable[..., GenerationResult] = default_ace_step_backend,
) -> GenerationResult:
    with tempfile.TemporaryDirectory(prefix="ace-step-output-") as temp_dir:
        output_dir = Path(temp_dir)
        result = backend(
            inputs=inputs,
            request=request,
            ace_step_root=ace_step_root,
            output_dir=output_dir,
        )
        copied_paths = []
        permanent_dir = inputs.workspace_dir / ".ace-step-raw"
        permanent_dir.mkdir(exist_ok=True)
        for path in result.paths:
            destination = permanent_dir / path.name
            shutil.copyfile(path, destination)
            copied_paths.append(destination)
        return GenerationResult(paths=copied_paths, seeds=result.seeds)
```

Update `main()` non-dry-run branch:

```python
    if args.ace_step_root is None:
        raise GenerationError("Pass --ace-step-root /path/to/ACE-Step-1.5 for local generation")

    result = run_generation(inputs, request=request, ace_step_root=args.ace_step_root)
    outputs = normalize_outputs(
        result.paths,
        workspace_dir=inputs.workspace_dir,
        slug=inputs.slug,
        output_format=args.output_format,
    )
    write_generation_report(
        inputs,
        request=request,
        outputs=outputs,
        model=args.model,
        lm_model=args.lm_model,
        seeds=result.seeds,
    )
    return 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: PASS.

- [ ] **Step 5: Commit**

Only commit if explicitly requested. If committing, run:

```bash
git add tools/ace-step-generator/ace_step_generator/generate.py tools/ace-step-generator/tests/test_generate.py
git commit -m "feat: add ace-step local inference adapter"
```

---

### Task 4: Add ACE-Step Step 5 Prompt

**Files:**
- Create: `prompts/step-5-generate-with-ace-step.md`

- [ ] **Step 1: Write the new prompt file**

Create `prompts/step-5-generate-with-ace-step.md`:

```markdown
# Step 5: Generate Remix Locally with ACE-Step

## Objective

Generate two remix candidates locally with ACE-Step 1.5 instead of uploading the acapella to Suno.ai. Save the candidates using the same filenames expected by Step 5.5 and downstream steps.

## Prerequisites

- `${WORKSPACE_DIR}/${SLUG}-acapella.mp3` exists from Step 2.
- `${WORKSPACE_DIR}/${SLUG}-lyrics.txt` exists from Step 3.
- `${WORKSPACE_DIR}/${SLUG}-suno-style.txt` exists from Step 4.
- `${WORKSPACE_DIR}/meta.json` exists with `slug`, `genre`, `language`, `tempo`, and `song_length`.
- ACE-Step 1.5 is cloned locally and installed into `tools/ace-step-generator`'s `uv` environment with `uv pip install -e "$ACE_STEP_ROOT"`.
- The ACE-Step checkout path is available as `ACE_STEP_ROOT` or is provided explicitly by the user.

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep stored `meta.json.files.*` values root-relative, for example `<slug>/<slug>-remix-v1.mp3`.

## Instructions

### 5.1 - Verify Local ACE-Step Setup

Confirm `ACE_STEP_ROOT` points to the ACE-Step checkout:

```bash
test -d "$ACE_STEP_ROOT" && test -f "$ACE_STEP_ROOT/pyproject.toml"
```

If `ACE_STEP_ROOT` is missing or invalid, ask the user for the absolute path to their `ACE-Step-1.5` checkout. If ACE-Step or its dependencies are missing, ask the user to run this from the repo root:

```bash
cd tools/ace-step-generator && uv pip install -e "$ACE_STEP_ROOT"
```

### 5.2 - Verify Workspace Inputs

Check that these files exist:

- `${WORKSPACE_DIR}/meta.json`
- `${WORKSPACE_DIR}/${SLUG}-lyrics.txt`
- `${WORKSPACE_DIR}/${SLUG}-suno-style.txt`
- `${WORKSPACE_DIR}/${SLUG}-acapella.mp3`

If the acapella is missing but `${WORKSPACE_DIR}/${SLUG}-original.mp3` exists, ask before using `--allow-original-fallback` because the full mix may preserve less vocal control than the acapella.

### 5.3 - Dry Run The ACE-Step Tool

Run a dry run first to validate inputs and write an inspection report:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --ace-step-root "${ACE_STEP_ROOT}" \
  --task-type cover \
  --batch-size 2 \
  --output-format mp3 \
  --dry-run
```

Working directory:

```bash
tools/ace-step-generator
```

Verify `${WORKSPACE_DIR}/${SLUG}-ace-step-generation.json` exists and has `"dry_run": true`.

### 5.4 - Generate Two Local Candidates

Run ACE-Step generation:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --ace-step-root "${ACE_STEP_ROOT}" \
  --task-type cover \
  --batch-size 2 \
  --output-format mp3
```

Expected outputs:

- `${WORKSPACE_DIR}/${SLUG}-remix-v1.mp3`
- `${WORKSPACE_DIR}/${SLUG}-remix-v2.mp3`
- `${WORKSPACE_DIR}/${SLUG}-ace-step-generation.json`

### 5.5 - Recovery Paths

If ACE-Step runs out of memory with `--batch-size 2`, stop and ask the user before changing generation mode, model, device, or system resources. Do not treat `--batch-size 1` as a complete Step 5 output unless the tool later supports accumulating two normalized candidates, because downstream steps require both `${SLUG}-remix-v1.mp3` and `${SLUG}-remix-v2.mp3`.

If cover mode fails or quality is unusable, ask the user whether to try text-to-music mode:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --ace-step-root "${ACE_STEP_ROOT}" \
  --task-type text2music \
  --batch-size 2 \
  --output-format mp3
```

### 5.6 - Update meta.json

Update `${WORKSPACE_DIR}/meta.json`:

```json
{
  "generation_backend": "ace-step",
  "files": {
    "remix_v1": "<slug>/<slug>-remix-v1.mp3",
    "remix_v2": "<slug>/<slug>-remix-v2.mp3",
    "ace_step_generation": "<slug>/<slug>-ace-step-generation.json"
  },
  "status": {
    "remix_uploaded": false,
    "remix_v1_downloaded": true,
    "remix_v2_downloaded": true,
    "ace_step_generated": true
  }
}
```

Preserve all existing unrelated `meta.json` fields.

### 5.7 - Ask User To Select A Candidate

Print:

```text
ACE-Step remix candidates generated:
1. <workspaceRoot>/<slug>/<slug>-remix-v1.mp3
2. <workspaceRoot>/<slug>/<slug>-remix-v2.mp3

Generation report: <workspaceRoot>/<slug>/<slug>-ace-step-generation.json

Listen to both files and reply `v1` or `v2` for the video.
```

### 5.8 - Persist the Selected Remix

After the user replies with `v1` or `v2`, update `${WORKSPACE_DIR}/meta.json` before proceeding:

```json
{
  "status": {
    "selected_remix": "v1 or v2"
  }
}
```

If the response is anything else, stop and ask the user to choose `v1` or `v2` explicitly. After `meta.json.status.selected_remix` is set, proceed to Step 6.
```

- [ ] **Step 2: Review prompt for consistency**

Read `prompts/step-5-generate-with-ace-step.md` and confirm it references only files and commands created by Tasks 1-3.

- [ ] **Step 3: Commit**

Only commit if explicitly requested. If committing, run:

```bash
git add prompts/step-5-generate-with-ace-step.md
git commit -m "docs: add ace-step generation step"
```

---

### Task 5: Update Pipeline Documentation And Workspace Conventions

**Files:**
- Modify: `prompts/README.md`
- Modify: `README.md`
- Modify: `prompts/references/workspace-conventions.md`

- [ ] **Step 1: Update `prompts/README.md` Step 5 rows**

Modify the Step 5 row to describe backend selection:

```markdown
| 5 | `step-5-upload-to-suno.md` or `step-5-generate-with-ace-step.md` | Generate 2 remix variations via Suno upload or local ACE-Step | `<slug>-remix-v1.mp3`, `<slug>-remix-v2.mp3`, optional `<slug>-ace-step-generation.json` | Steps 2, 4 |
```

Modify the key conventions list to include:

```markdown
- **Generation backend**: Step 5 can use Suno (`step-5-upload-to-suno.md`) or local ACE-Step (`step-5-generate-with-ace-step.md`); both produce the same remix candidate filenames.
```

- [ ] **Step 2: Update `README.md` tech stack and Step 5 description**

Modify the Music Generation tech stack row:

```markdown
| **Music Generation** | Suno.ai via Chrome DevTools MCP, or local ACE-Step 1.5 direct Python generation |
```

Modify the Step 5 line in the pipeline diagram:

```markdown
[Step 5] Generate Remix             → Suno upload or local ACE-Step creates 2 variations
```

Modify the Step 5 section:

```markdown
### Step 5: Generate Remix

Step 5 supports two generation backends:

- **Suno**: Automates Suno.ai through Chrome DevTools MCP, uploads acapella, pastes formatted lyrics and style block, triggers generation, and downloads 2 remix variations.
- **ACE-Step**: Runs ACE-Step 1.5 locally through `tools/ace-step-generator`, using the Step 4 style prompt, native-script lyrics, and extracted acapella to generate 2 local remix variations.

Both backends write `<slug>-remix-v1.mp3` and `<slug>-remix-v2.mp3`, so Step 5.5 and downstream video steps remain unchanged.
```

- [ ] **Step 3: Update workspace conventions**

In `prompts/references/workspace-conventions.md`, add `generation_backend` after `song_length` in the schema example:

```json
  "generation_backend": "suno",
```

Add file keys in the schema example:

```json
    "remix_v1": null,
    "remix_v2": null,
    "ace_step_generation": null,
```

Add status key in the schema example:

```json
    "ace_step_generated": false,
```

Add directory entry:

```text
    ├── <slug>-ace-step-generation.json
```

Add purpose suffix:

```markdown
| `ace-step-generation` | Local ACE-Step generation report |
```

- [ ] **Step 4: Commit**

Only commit if explicitly requested. If committing, run:

```bash
git add prompts/README.md README.md prompts/references/workspace-conventions.md
git commit -m "docs: document ace-step backend selection"
```

---

### Task 6: Verify The Complete First Slice

**Files:**
- No code files expected unless verification finds a defect.

- [ ] **Step 1: Run the ACE-Step generator unit tests**

Run:

```bash
uv run pytest tests/test_generate.py -v
```

Working directory: `tools/ace-step-generator`

Expected: all tests PASS.

- [ ] **Step 2: Run a dry-run smoke test against a temporary workspace**

Create a temporary workspace manually or with shell commands, then run:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir /tmp/ace-step-smoke/bella-bella-lofi \
  --slug bella-bella-lofi \
  --dry-run
```

Working directory: `tools/ace-step-generator`

Expected: exit code 0 and `/tmp/ace-step-smoke/bella-bella-lofi/bella-bella-lofi-ace-step-generation.json` exists with `"dry_run": true`.

- [ ] **Step 3: Optional real ACE-Step short generation**

Only run this if ACE-Step is installed locally and the machine has enough resources for two candidates. Skip real generation if resources are insufficient:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --ace-step-root "${ACE_STEP_ROOT}" \
  --task-type cover \
  --batch-size 2 \
  --output-format mp3
```

Working directory: `tools/ace-step-generator`

Expected: `<slug>-remix-v1.mp3`, `<slug>-remix-v2.mp3`, and `<slug>-ace-step-generation.json` exist. If this is skipped, record that real model inference was not verified.

- [ ] **Step 4: Review docs links and paths**

Read these files and verify all referenced paths exist:

```text
README.md
prompts/README.md
prompts/step-5-generate-with-ace-step.md
prompts/references/workspace-conventions.md
```

Expected: no references to missing prompt/tool paths.

- [ ] **Step 5: Final commit**

Only commit if explicitly requested. If committing all remaining changes, run:

```bash
git status --short
git add tools/ace-step-generator prompts/step-5-generate-with-ace-step.md prompts/README.md README.md prompts/references/workspace-conventions.md docs/superpowers/specs/2026-05-03-ace-step-local-generation-design.md docs/superpowers/plans/2026-05-03-ace-step-local-generation.md
git commit -m "feat: add local ace-step remix backend"
```

---

## Self-Review

- Spec coverage: Tasks cover the direct Python tool, workspace validation, dry run, direct ACE-Step inference boundary, output normalization, generation report, Step 5 prompt, docs, workspace conventions, and verification.
- Placeholder scan: The plan avoids placeholders and gives exact files, commands, and code snippets. Optional real inference is explicitly conditional on local ACE-Step availability.
- Type consistency: The plan consistently uses `WorkspaceInputs`, `GenerationResult`, `build_generation_request`, `run_generation`, `normalize_outputs`, and `write_generation_report` across tests and implementation steps.

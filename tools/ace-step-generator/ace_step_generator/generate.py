from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


class GenerationError(RuntimeError):
    pass


LANGUAGE_TO_ACE = {
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "English": "en",
}

PARAM_REQUEST_KEYS = {"bpm", "duration", "guidance_scale", "inference_steps"}
CONFIG_REQUEST_KEYS = {
    "seeds",
    "use_random_seed",
}


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


@dataclass(frozen=True)
class GenerationResult:
    paths: list[Path]
    seeds: list[int]


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

    meta_slug = meta.get("slug")
    if meta_slug != slug:
        raise GenerationError(f"meta.json slug {meta_slug!r} does not match --slug {slug!r}")
    if workspace_dir.name != slug:
        raise GenerationError(
            f"Workspace directory name {workspace_dir.name!r} does not match --slug {slug!r}"
        )

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


def workspace_relative(path: Path, workspace_dir: Path) -> str:
    relative = path.resolve().relative_to(workspace_dir.resolve())
    return f"{workspace_dir.name}/{relative.as_posix()}"


def load_generation_config(config_path: Path | None) -> dict:
    if config_path is None:
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def clean_lyrics(lyrics: str, mode: str) -> str:
    if mode == "raw":
        return lyrics.strip()
    if mode not in {"clean-native", "suno-stripped"}:
        raise GenerationError(f"Unsupported lyrics_mode: {mode}")

    lines = []
    for line in lyrics.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if mode == "suno-stripped" and stripped.startswith("[") and stripped.endswith("]"):
            continue
        lines.append(stripped)
    return "\n".join(lines)


def parse_seeds(value: str | None) -> list[int] | None:
    if value is None:
        return None
    return [int(seed.strip()) for seed in value.split(",") if seed.strip()]


def compact_overrides(values: dict) -> dict:
    return {key: value for key, value in values.items() if value is not None}


def build_generation_request(
    inputs: WorkspaceInputs,
    *,
    task_type: str,
    batch_size: int,
    output_format: str,
    audio_cover_strength: float,
    model: str,
    lm_model: str | None,
    config_overrides: dict | None = None,
    cli_overrides: dict | None = None,
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

    overrides = {}
    overrides.update(config_overrides or {})
    overrides.update(cli_overrides or {})

    lyrics_file = overrides.pop("lyrics_file", None)
    lyrics_mode = overrides.pop("lyrics_mode", "clean-native")
    if lyrics_file is not None:
        request["lyrics"] = Path(lyrics_file).read_text(encoding="utf-8")
    request["lyrics"] = clean_lyrics(request["lyrics"], str(lyrics_mode))
    request["lyrics_mode"] = lyrics_mode

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

    for key, value in overrides.items():
        request[key] = value

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
        "effective_request": request,
        "dry_run": dry_run,
        "created_at": datetime.now(UTC).isoformat(),
    }
    report_path = inputs.workspace_dir / f"{inputs.slug}-ace-step-generation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def transcode_to_mp3(source: Path, destination: Path) -> None:
    try:
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
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise GenerationError(f"ffmpeg failed while transcoding {source} to MP3") from error


def normalize_outputs(
    raw_outputs: list[Path],
    *,
    workspace_dir: Path,
    slug: str,
    output_format: str,
    transcode: bool = True,
) -> list[Path]:
    if len(raw_outputs) < 2:
        raise GenerationError("ACE-Step must produce two audio files")

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
    ace_step_root: Path | None,
    output_dir: Path,
) -> GenerationResult:
    project_root = ace_step_root or (inputs.workspace_dir / ".ace-step")
    if ace_step_root is not None and not ace_step_root.exists():
        raise GenerationError(f"ACE-Step root does not exist: {ace_step_root}")

    original_sys_path = list(sys.path)
    try:
        if ace_step_root is not None:
            sys.path.insert(0, str(ace_step_root.resolve()))
        from acestep.handler import AceStepHandler
        from acestep.inference import GenerationConfig, GenerationParams, generate_music
        from acestep.llm_inference import LLMHandler

        output_dir.mkdir(parents=True, exist_ok=True)
        project_root.mkdir(parents=True, exist_ok=True)
        dit_handler = AceStepHandler()
        dit_handler.initialize_service(
            project_root=str(project_root.resolve()),
            config_path=request["model"],
            device="auto",
            offload_to_cpu=bool(request.get("offload_to_cpu", False)),
            offload_dit_to_cpu=bool(request.get("offload_dit_to_cpu", False)),
        )

        llm_handler = None
        if request["task_type"] == "text2music" and request.get("lm_model"):
            llm_handler = LLMHandler()
            llm_handler.initialize(
                checkpoint_dir=str(project_root.resolve()),
                lm_model_path=request["lm_model"],
                backend="pt",
                device="auto",
            )

        param_kwargs = {
            "task_type": request["task_type"],
            "caption": request["caption"],
            "lyrics": request["lyrics"],
            "vocal_language": request["vocal_language"],
            "src_audio": request.get("src_audio"),
            "audio_cover_strength": request.get("audio_cover_strength", 1.0),
            "thinking": bool(request.get("thinking", False)),
        }
        for key in PARAM_REQUEST_KEYS:
            if key in request:
                param_kwargs[key] = request[key]
        params = GenerationParams(**param_kwargs)

        config_kwargs = {
            "batch_size": request["batch_size"],
            "audio_format": "wav" if request["audio_format"] == "mp3" else request["audio_format"],
        }
        for key in CONFIG_REQUEST_KEYS:
            if key in request:
                config_kwargs[key] = request[key]
        config = GenerationConfig(**config_kwargs)
        result = generate_music(dit_handler, llm_handler, params, config, save_dir=str(output_dir))
        if not result.success:
            raise GenerationError(result.error or result.status_message or "ACE-Step generation failed")

        paths = [Path(audio["path"]) for audio in result.audios]
        seeds = [int(audio.get("params", {}).get("seed", -1)) for audio in result.audios]
        return GenerationResult(paths=paths, seeds=seeds)
    except ImportError as error:
        raise GenerationError(
            "Could not import ACE-Step. Run `uv sync` in tools/ace-step-generator "
            "so ACE-Step and its dependencies are installed."
        ) from error
    finally:
        sys.path[:] = original_sys_path
        if ace_step_root is not None:
            for module_name in list(sys.modules):
                if module_name == "acestep" or module_name.startswith("acestep."):
                    sys.modules.pop(module_name, None)


def run_generation(
    inputs: WorkspaceInputs,
    *,
    request: dict,
    ace_step_root: Path | None,
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
        seen_names = set()
        for path in result.paths:
            destination_name = path.name
            if destination_name in seen_names:
                destination_name = f"{path.stem}-{len(seen_names) + 1}{path.suffix}"
            seen_names.add(destination_name)
            destination = permanent_dir / destination_name
            shutil.copyfile(path, destination)
            copied_paths.append(destination)
        return GenerationResult(paths=copied_paths, seeds=result.seeds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate remix candidates with ACE-Step")
    parser.add_argument("--workspace-dir", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--ace-step-root", type=Path, default=None)
    parser.add_argument("--task-type", choices=["cover", "text2music"], default="cover")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--output-format", default="mp3")
    parser.add_argument("--model", default="acestep-v15-turbo")
    parser.add_argument("--lm-model", default=None)
    parser.add_argument("--audio-cover-strength", type=float, default=0.7)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--caption", default=None)
    parser.add_argument("--lyrics-file", type=Path, default=None)
    parser.add_argument("--lyrics-mode", choices=["clean-native", "raw", "suno-stripped"], default=None)
    parser.add_argument("--guidance-scale", type=float, default=None)
    parser.add_argument("--omega-scale", type=float, default=None)
    parser.add_argument("--seeds", default=None, help="Comma-separated manual seeds")
    parser.add_argument("--use-random-seed", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--bpm", type=int, default=None)
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--allow-original-fallback", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
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
            config_overrides=load_generation_config(args.config),
            cli_overrides=compact_overrides(
                {
                    "caption": args.caption,
                    "lyrics_file": str(args.lyrics_file) if args.lyrics_file else None,
                    "lyrics_mode": args.lyrics_mode,
                    "guidance_scale": args.guidance_scale,
                    "omega_scale": args.omega_scale,
                    "manual_seeds": parse_seeds(args.seeds),
                    "use_random_seed": args.use_random_seed,
                    "bpm": args.bpm,
                    "duration": args.duration,
                }
            ),
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
    except GenerationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

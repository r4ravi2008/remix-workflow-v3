import json
import sys
import tomllib
from pathlib import Path

import pytest

from ace_step_generator import generate


def test_pyproject_installs_ace_step_as_required_dependency():
    pyproject_path = Path(__file__).parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert pyproject["project"]["requires-python"] == ">=3.12,<3.13"
    assert any(
        dependency.startswith("ace-step @ git+https://github.com/ACE-Step/ACE-Step-1.5.git")
        for dependency in pyproject["project"]["dependencies"]
    )


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


def test_load_workspace_inputs_validates_meta_slug(tmp_path):
    workspace = make_workspace(tmp_path)
    meta_path = workspace / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["slug"] = "wrong-slug"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")

    with pytest.raises(generate.GenerationError, match="meta.json slug"):
        generate.load_workspace_inputs(workspace, "bella-bella-lofi")


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


def test_build_generation_request_applies_config_and_cli_overrides(tmp_path):
    workspace = make_workspace(tmp_path)
    lyrics_override = workspace / "clean-lyrics.txt"
    lyrics_override.write_text("# Header\n\nపల్లవి\n[Chorus]\nచరణం\n", encoding="utf-8")
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")

    request = generate.build_generation_request(
        inputs,
        task_type="cover",
        batch_size=2,
        output_format="mp3",
        audio_cover_strength=0.7,
        model="acestep-v15-turbo",
        lm_model=None,
        config_overrides={
            "caption": "config caption",
            "audio_cover_strength": 0.55,
            "bpm": 122,
            "duration": 183,
            "lyrics_file": str(lyrics_override),
            "lyrics_mode": "suno-stripped",
            "seeds": [111, 222],
            "use_random_seed": False,
        },
        cli_overrides={"caption": "cli caption", "guidance_scale": 8.5},
    )

    assert request["caption"] == "cli caption"
    assert request["audio_cover_strength"] == 0.55
    assert request["bpm"] == 122
    assert request["duration"] == 183
    assert request["guidance_scale"] == 8.5
    assert request["lyrics"] == "పల్లవి\nచరణం"
    assert request["seeds"] == [111, 222]
    assert request["use_random_seed"] is False


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
    assert report["effective_request"]["task_type"] == "cover"


def test_load_generation_config_reads_json(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"caption": "json style", "bpm": 124, "seeds": [1, 2]}),
        encoding="utf-8",
    )

    assert generate.load_generation_config(config_path) == {
        "caption": "json style",
        "bpm": 124,
        "seeds": [1, 2],
    }


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


def test_main_merges_config_and_cli_flags_into_dry_run_report(tmp_path):
    workspace = make_workspace(tmp_path)
    config_path = workspace / "ace-step-config.json"
    config_path.write_text(
        json.dumps({"caption": "config caption", "audio_cover_strength": 0.6, "bpm": 122}),
        encoding="utf-8",
    )

    exit_code = generate.main([
        "--workspace-dir",
        str(workspace),
        "--slug",
        "bella-bella-lofi",
        "--config",
        str(config_path),
        "--caption",
        "cli caption",
        "--guidance-scale",
        "8.5",
        "--dry-run",
    ])

    report = json.loads((workspace / "bella-bella-lofi-ace-step-generation.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["effective_request"]["caption"] == "cli caption"
    assert report["effective_request"]["audio_cover_strength"] == 0.6
    assert report["effective_request"]["bpm"] == 122
    assert report["effective_request"]["guidance_scale"] == 8.5


def test_main_reports_generation_errors_without_traceback(tmp_path, capsys):
    workspace = make_workspace(tmp_path)

    exit_code = generate.main([
        "--workspace-dir",
        str(workspace),
        "--slug",
        "bella-bella-lofi",
        "--batch-size",
        "0",
        "--dry-run",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err == "error: --batch-size must be at least 1\n"
    assert "Traceback" not in captured.err


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


def test_normalize_outputs_requires_two_generated_files(tmp_path):
    workspace = make_workspace(tmp_path)
    raw = tmp_path / "raw-a.mp3"
    raw.write_bytes(b"mp3 audio")

    with pytest.raises(generate.GenerationError, match="two audio files"):
        generate.normalize_outputs(
            [raw],
            workspace_dir=workspace,
            slug="bella-bella-lofi",
            output_format="mp3",
        )


def test_transcode_to_mp3_converts_ffmpeg_failures_to_generation_error(tmp_path, monkeypatch):
    source = tmp_path / "raw.flac"
    destination = tmp_path / "normalized.mp3"
    source.write_bytes(b"flac audio")

    def fail_ffmpeg(*args, **kwargs):
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(generate.subprocess, "run", fail_ffmpeg)

    with pytest.raises(generate.GenerationError, match="ffmpeg failed"):
        generate.transcode_to_mp3(source, destination)


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


def test_run_generation_keeps_duplicate_basenames_distinct(tmp_path):
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
        first = output_dir / "a" / "candidate.mp3"
        second = output_dir / "b" / "candidate.mp3"
        first.parent.mkdir()
        second.parent.mkdir()
        first.write_bytes(b"one")
        second.write_bytes(b"two")
        return generate.GenerationResult(paths=[first, second], seeds=[11, 22])

    result = generate.run_generation(
        inputs,
        request=request,
        ace_step_root=tmp_path / "ACE-Step-1.5",
        backend=fake_backend,
    )

    assert result.paths[0] != result.paths[1]
    assert result.paths[0].read_bytes() == b"one"
    assert result.paths[1].read_bytes() == b"two"


def test_default_ace_step_backend_rejects_missing_source_root_without_sys_path_change(tmp_path):
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
    ace_step_root = tmp_path / "ACE-Step-1.5"
    original_sys_path = list(sys.path)

    with pytest.raises(generate.GenerationError, match="ACE-Step root does not exist"):
        generate.default_ace_step_backend(
            inputs=inputs,
            request=request,
            ace_step_root=ace_step_root,
            output_dir=tmp_path / "outputs",
        )

    assert sys.path == original_sys_path


def test_default_ace_step_backend_uses_ace_step_15_inference_api(tmp_path):
    workspace = make_workspace(tmp_path)
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")
    request = generate.build_generation_request(
        inputs,
        task_type="cover",
        batch_size=2,
        output_format="mp3",
        audio_cover_strength=0.7,
        model="/models/ace-step",
        lm_model=None,
    )
    ace_step_root = tmp_path / "ACE-Step-1.5"
    package = ace_step_root / "acestep"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "handler.py").write_text(
        """
class AceStepHandler:
    def initialize_service(self, **kwargs):
        assert kwargs['project_root'].endswith('ACE-Step-1.5')
        assert kwargs['config_path'] == '/models/ace-step'
""".strip(),
        encoding="utf-8",
    )
    (package / "llm_inference.py").write_text(
        """
class LLMHandler:
    def initialize(self, **kwargs):
        raise AssertionError('cover mode should not initialize LM handler')
""".strip(),
        encoding="utf-8",
    )
    (package / "inference.py").write_text(
        """
from pathlib import Path


class GenerationParams:
    def __init__(self, **kwargs):
        assert kwargs['task_type'] == 'cover'
        assert kwargs['caption'] == 'lo-fi hip hop, nostalgic, Telugu, soft male vocal, 75 bpm'
        assert kwargs['lyrics'] == 'పల్లవి\\nచరణం'
        assert kwargs['vocal_language'] == 'te'
        assert kwargs['src_audio'].endswith('bella-bella-lofi-acapella.mp3')
        assert kwargs['audio_cover_strength'] == 0.7
        assert kwargs['thinking'] is False


class GenerationConfig:
    def __init__(self, **kwargs):
        assert kwargs['batch_size'] == 2
        assert kwargs['audio_format'] == 'wav'


def generate_music(dit_handler, llm_handler, params, config, save_dir):
    assert llm_handler is None
    output_dir = Path(save_dir)
    first = output_dir / 'candidate-a.mp3'
    second = output_dir / 'candidate-b.mp3'
    first.write_bytes(b'one')
    second.write_bytes(b'two')
    return type('Result', (), {
        'success': True,
        'audios': [
            {'path': str(first), 'params': {'seed': 101}},
            {'path': str(second), 'params': {'seed': 202}},
        ],
        'error': None,
        'status_message': '',
    })()
""".strip(),
        encoding="utf-8",
    )

    result = generate.default_ace_step_backend(
        inputs=inputs,
        request=request,
        ace_step_root=ace_step_root,
        output_dir=tmp_path / "outputs",
    )

    assert [path.name for path in result.paths] == ["candidate-a.mp3", "candidate-b.mp3"]
    assert result.seeds == [101, 202]


def test_default_ace_step_backend_maps_advanced_generation_config(tmp_path):
    workspace = make_workspace(tmp_path)
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")
    request = generate.build_generation_request(
        inputs,
        task_type="cover",
        batch_size=2,
        output_format="flac",
        audio_cover_strength=0.7,
        model="/models/ace-step",
        lm_model=None,
        config_overrides={
            "guidance_scale": 8.5,
            "inference_steps": 12,
            "seeds": [111, 222],
            "use_random_seed": False,
            "bpm": 122,
            "duration": 183,
        },
    )
    ace_step_root = tmp_path / "ACE-Step-1.5"
    package = ace_step_root / "acestep"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "handler.py").write_text(
        """
class AceStepHandler:
    def initialize_service(self, **kwargs):
        pass
""".strip(),
        encoding="utf-8",
    )
    (package / "llm_inference.py").write_text(
        """
class LLMHandler:
    def initialize(self, **kwargs):
        pass
""".strip(),
        encoding="utf-8",
    )
    (package / "inference.py").write_text(
        """
from pathlib import Path


class GenerationParams:
    def __init__(self, **kwargs):
        assert kwargs['bpm'] == 122
        assert kwargs['duration'] == 183
        assert kwargs['guidance_scale'] == 8.5
        assert kwargs['inference_steps'] == 12


class GenerationConfig:
    def __init__(self, **kwargs):
        assert kwargs['batch_size'] == 2
        assert kwargs['audio_format'] == 'flac'
        assert kwargs['seeds'] == [111, 222]
        assert kwargs['use_random_seed'] is False


def generate_music(dit_handler, llm_handler, params, config, save_dir):
    output_dir = Path(save_dir)
    first = output_dir / 'candidate-a.flac'
    second = output_dir / 'candidate-b.flac'
    first.write_bytes(b'one')
    second.write_bytes(b'two')
    return type('Result', (), {
        'success': True,
        'audios': [
            {'path': str(first), 'params': {'seed': 111}},
            {'path': str(second), 'params': {'seed': 222}},
        ],
        'error': None,
        'status_message': '',
    })()
""".strip(),
        encoding="utf-8",
    )

    result = generate.default_ace_step_backend(
        inputs=inputs,
        request=request,
        ace_step_root=ace_step_root,
        output_dir=tmp_path / "outputs",
    )

    assert result.seeds == [111, 222]


def test_default_ace_step_backend_passes_cpu_offload_options(tmp_path):
    workspace = make_workspace(tmp_path)
    inputs = generate.load_workspace_inputs(workspace, "bella-bella-lofi")
    request = generate.build_generation_request(
        inputs,
        task_type="cover",
        batch_size=2,
        output_format="mp3",
        audio_cover_strength=0.7,
        model="/models/ace-step",
        lm_model=None,
        config_overrides={"offload_to_cpu": True, "offload_dit_to_cpu": True},
    )
    ace_step_root = tmp_path / "ACE-Step-1.5"
    package = ace_step_root / "acestep"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "handler.py").write_text(
        """
class AceStepHandler:
    def initialize_service(self, **kwargs):
        assert kwargs['offload_to_cpu'] is True
        assert kwargs['offload_dit_to_cpu'] is True
""".strip(),
        encoding="utf-8",
    )
    (package / "llm_inference.py").write_text(
        """
class LLMHandler:
    def initialize(self, **kwargs):
        pass
""".strip(),
        encoding="utf-8",
    )
    (package / "inference.py").write_text(
        """
from pathlib import Path


class GenerationParams:
    def __init__(self, **kwargs):
        pass


class GenerationConfig:
    def __init__(self, **kwargs):
        pass


def generate_music(dit_handler, llm_handler, params, config, save_dir):
    output_dir = Path(save_dir)
    first = output_dir / 'candidate-a.wav'
    second = output_dir / 'candidate-b.wav'
    first.write_bytes(b'one')
    second.write_bytes(b'two')
    return type('Result', (), {
        'success': True,
        'audios': [
            {'path': str(first), 'params': {'seed': 101}},
            {'path': str(second), 'params': {'seed': 202}},
        ],
        'error': None,
        'status_message': '',
    })()
""".strip(),
        encoding="utf-8",
    )

    result = generate.default_ace_step_backend(
        inputs=inputs,
        request=request,
        ace_step_root=ace_step_root,
        output_dir=tmp_path / "outputs",
    )

    assert result.seeds == [101, 202]

from pathlib import Path

from acapella_extractor import extract as extract_module


def test_extract_vocals_renames_output_from_output_dir(monkeypatch, tmp_path):
    input_file = tmp_path / "input.m4a"
    input_file.write_bytes(b"source")

    class FakeSeparator:
        def __init__(self, **kwargs):
            self.output_dir = Path(kwargs["output_dir"])

        def load_model(self, model_name):
            self.model_name = model_name

        def separate(self, input_path):
            output_file = self.output_dir / "input_(vocals)_model.wav"
            output_file.write_bytes(b"vocals")
            return [output_file.name]

    monkeypatch.setattr(extract_module, "Separator", FakeSeparator)

    result = extract_module.extract_vocals(str(input_file), str(tmp_path))

    assert result == tmp_path / "acapella.mp3"
    assert result.read_bytes() == b"vocals"
    assert not (tmp_path / "input_(vocals)_model.wav").exists()


def test_extract_vocals_requests_mp3_output(monkeypatch, tmp_path):
    input_file = tmp_path / "input.m4a"
    input_file.write_bytes(b"source")
    separator_kwargs = {}

    class FakeSeparator:
        def __init__(self, **kwargs):
            separator_kwargs.update(kwargs)
            self.output_dir = Path(kwargs["output_dir"])

        def load_model(self, model_name):
            self.model_name = model_name

        def separate(self, input_path):
            output_file = self.output_dir / "input_(vocals)_model.mp3"
            output_file.write_bytes(b"vocals")
            return [str(output_file)]

    monkeypatch.setattr(extract_module, "Separator", FakeSeparator)

    extract_module.extract_vocals(str(input_file), str(tmp_path))

    assert separator_kwargs["output_format"] == "MP3"
    assert separator_kwargs["output_bitrate"] == "192k"

"""Shared test fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for test files."""
    output = tmp_path / "output"
    output.mkdir()
    return output

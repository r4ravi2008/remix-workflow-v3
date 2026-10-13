#!/usr/bin/env python3
"""Compatibility entrypoint for the shared video-director finish_review checker."""
import importlib.util
from pathlib import Path
import sys

_core_path = Path(__file__).resolve().parents[2] / 'video-director' / 'scripts' / 'finish_review.py'
_spec = importlib.util.spec_from_file_location('_video_director_finish_review', _core_path)
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)
globals().update({key: value for key, value in vars(_core).items() if not key.startswith('_')})

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Run the canonical Warpmoon checks, including hidden-event tooltip isolation.

Keep the performance-review entry point without maintaining a second, stale
copy of the project validator. These checks do not execute the EU4 engine.
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / 'Warpmoon Project' /
                  'validate_warpmoon.py'), run_name='__main__')

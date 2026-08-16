"""Shared pytest fixtures for the calculator skill test suite."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("calculator_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules["calculator_skill"] = _module
_spec.loader.exec_module(_module)

Calculator = _module.Calculator


@pytest.fixture
def skill(monkeypatch):
    s = Calculator.__new__(Calculator)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-calculator.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    monkeypatch.setattr(Calculator, "lang", "en-us", raising=False)
    s.res_dir = str(Path(__file__).resolve().parents[1])
    s._lang_resources = {}
    return s

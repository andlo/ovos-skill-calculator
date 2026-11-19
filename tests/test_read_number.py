"""Tests for _read_number(), the one place the skill reads a number."""
from fractions import Fraction
from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize("raw, lang, expected", [
    ("15", "en-us", 15),
    ("fifteen", "en-us", 15),
    ("3.5", "en-us", Fraction(7, 2)),
    ("two and a half", "en-us", Fraction(5, 2)),
    ("a third", "en-us", Fraction(1, 3)),
    ("femogtyve", "da-dk", 25),
    ("3,5", "da-dk", Fraction(7, 2)),
    ("halvanden", "da-dk", Fraction(3, 2)),
    ("en", "da-dk", 1),
])
def test_reads_digits_and_words(raw, lang, expected):
    from calculator_skill import _read_number
    assert _read_number(raw, lang) == expected


@pytest.mark.parametrize("raw", [None, "", "banana"])
def test_no_number(raw):
    from calculator_skill import _read_number
    assert _read_number(raw, "en-us") is None


def test_unsupported_language_reads_no_number():
    from calculator_skill import _read_number
    assert _read_number("5", "xx-xx") is None


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_decimal_arithmetic_is_exact(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_add(_msg(a="0.1", b="0.2"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 0.3})


def test_danish_decimal_comma(skill, monkeypatch):
    from calculator_skill import Calculator
    monkeypatch.setattr(Calculator, "lang", "da-dk", raising=False)
    skill.speak_dialog = MagicMock()
    skill.handle_add(_msg(a="3,5", b="2"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 5.5})


def test_common_query_danish_decimal_comma(skill):
    assert skill.handle_common_query("hvad er 3,5 gange 2", "da-dk") == ("7", 0.8)


def test_format_number_fraction():
    from calculator_skill import _format_number
    assert _format_number(Fraction(10, 2)) == 5
    assert isinstance(_format_number(Fraction(10, 2)), int)
    assert _format_number(Fraction(1, 3)) == 0.3333

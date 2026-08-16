"""Tests for _format_number - the fix for the ".0" rough edge flagged
in ovos-skill-convert/tuning-fork/rhythm-box."""
import pytest


def test_whole_number_float_becomes_plain_int():
    from calculator_skill import _format_number
    assert _format_number(10.0) == 10
    assert isinstance(_format_number(10.0), int)


def test_fraction_rounds_to_decimal_places():
    from calculator_skill import _format_number
    assert _format_number(3.333333333) == 3.3333


def test_int_passes_through_unchanged():
    from calculator_skill import _format_number
    assert _format_number(5) == 5

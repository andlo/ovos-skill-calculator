"""Tests for the seven arithmetic intent handlers."""
from unittest.mock import MagicMock

import pytest


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_add(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_add(_msg(a="5", b="3"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 8})


def test_subtract(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_subtract(_msg(a="10", b="4"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 6})


def test_multiply(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_multiply(_msg(a="6", b="7"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 42})


def test_divide(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_divide(_msg(a="10", b="4"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 2.5})


def test_divide_whole_result_has_no_trailing_dot_zero(skill):
    """The specific rough edge this skill fixes."""
    skill.speak_dialog = MagicMock()
    skill.handle_divide(_msg(a="10", b="2"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 5})


def test_divide_by_zero(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_divide(_msg(a="10", b="0"))
    skill.speak_dialog.assert_called_once_with("division_by_zero")


def test_percentage(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_percentage(_msg(a="20", b="150"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 30})


def test_square(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_square(_msg(a="9"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 81})


def test_square_root(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_square_root(_msg(a="144"))
    skill.speak_dialog.assert_called_once_with("result", {"result": 12})


def test_square_root_of_negative_number(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_square_root(_msg(a="-4"))
    skill.speak_dialog.assert_called_once_with("negative_square_root")


def test_unparseable_numbers(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_add(_msg(a="banana", b="3"))
    skill.speak_dialog.assert_called_once_with("numbers_not_understood")


def test_missing_slot(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_add(_msg(a="5"))  # no 'b' at all
    skill.speak_dialog.assert_called_once_with("numbers_not_understood")

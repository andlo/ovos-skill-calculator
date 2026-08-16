"""
skill OVOS Calculator
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

A basic calculator - "what is 15 times 23", "what is the square root
of 144", "what is 20 percent of 150". Fully offline, pure arithmetic,
no external dependencies beyond number parsing.

ONE INTENT FILE PER OPERATION, NOT A SHARED {operator} WILDCARD
-------------------------------------------------------------------
A tempting shortcut would be a single intent like
"what is {a} {operator} {b}" with the operator word (plus/minus/
times/...) captured as a wildcard. This does NOT work reliably in
padatious: with three consecutive wildcards and no literal anchor word
between {a}, {operator}, and {b}, the matcher has no way to know where
one wildcard ends and the next begins. Each operation therefore gets
its own intent file with the operator as LITERAL text ("what is {a}
plus {b}", "what is {a} minus {b}", etc) - the same anchor-word
pattern every other intent in this project family uses (e.g.
ovos-skill-convert's "convert {value} {from_unit} to {to_unit}").

RESULT FORMATTING - FIXES A ROUGH EDGE FLAGGED ELSEWHERE
------------------------------------------------------------
ovos-skill-convert, ovos-skill-tuning-fork, and ovos-skill-rhythm-box
all documented (but didn't fix) whole-number results being spoken
with a trailing ".0" (e.g. "10.0" instead of "10"), because Python's
default float formatting was used as-is. This skill fixes it via
_format_number(): a whole-number float is spoken as a plain integer,
a genuine fraction is rounded to a reasonable number of decimal
places. Worth back-porting the same helper to the other skills later,
not done retroactively here to keep this change scoped.
"""

import math

from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
from ovos_number_parser import extract_number

DECIMAL_PLACES = 4


def _format_number(value):
    """Whole numbers speak as plain integers ('10', not '10.0');
    genuine fractions are rounded to DECIMAL_PLACES."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, float):
        return round(value, DECIMAL_PLACES)
    return value


class Calculator(OVOSSkill):

    def _parse_two_numbers(self, message):
        """Shared by add/subtract/multiply/divide/percentage - all
        take an {a} and a {b} slot. Returns (a, b) or (None, None) if
        either failed to parse."""
        a_raw = message.data.get("a")
        b_raw = message.data.get("b")
        a = extract_number(a_raw, lang=self.lang) if a_raw else None
        b = extract_number(b_raw, lang=self.lang) if b_raw else None
        if a is False or a is None or b is False or b is None:
            return None, None
        return a, b

    def _speak_result(self, result):
        self.speak_dialog("result", {"result": _format_number(result)})

    @intent_handler("add.intent")
    def handle_add(self, message):
        a, b = self._parse_two_numbers(message)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        self._speak_result(a + b)

    @intent_handler("subtract.intent")
    def handle_subtract(self, message):
        a, b = self._parse_two_numbers(message)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        self._speak_result(a - b)

    @intent_handler("multiply.intent")
    def handle_multiply(self, message):
        a, b = self._parse_two_numbers(message)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        self._speak_result(a * b)

    @intent_handler("divide.intent")
    def handle_divide(self, message):
        a, b = self._parse_two_numbers(message)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        if b == 0:
            self.speak_dialog("division_by_zero")
            return
        self._speak_result(a / b)

    @intent_handler("percentage.intent")
    def handle_percentage(self, message):
        a, b = self._parse_two_numbers(message)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        self._speak_result(a / 100 * b)

    @intent_handler("square.intent")
    def handle_square(self, message):
        a_raw = message.data.get("a")
        a = extract_number(a_raw, lang=self.lang) if a_raw else None
        if a is False or a is None:
            self.speak_dialog("numbers_not_understood")
            return
        self._speak_result(a ** 2)

    @intent_handler("square_root.intent")
    def handle_square_root(self, message):
        a_raw = message.data.get("a")
        a = extract_number(a_raw, lang=self.lang) if a_raw else None
        if a is False or a is None:
            self.speak_dialog("numbers_not_understood")
            return
        if a < 0:
            self.speak_dialog("negative_square_root")
            return
        self._speak_result(math.sqrt(a))

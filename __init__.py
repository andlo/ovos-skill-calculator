"""
skill OVOS Calculator

A basic calculator - "what is 15 times 23", "what is the square root
of 144", "what is 20 percent of 150". Fully offline, pure arithmetic,
no external dependencies beyond number reading (numtag).

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
import re
from fractions import Fraction

from numtag import Reason, UnsupportedLanguageError, tag_numbers
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler, common_query

DECIMAL_PLACES = 4


def _format_number(value):
    """Whole numbers speak as plain integers ('10', not '10.0');
    genuine fractions are rounded to DECIMAL_PLACES."""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return int(value)
        value = float(value)
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, float):
        return round(value, DECIMAL_PLACES)
    return value


# ---------------------------------------------------------------
# Common Query safety net - see ovos-skill-geometry/ovos-skill-geography's
# DEVELOPMENT.md "Common Query as a safety net, not a replacement":
# live testing found a platform-level semantic router
# (ovos-m2v-pipeline-high) can intercept a "what is X" utterance
# before this skill's own Padatious intent gets a chance, on
# installations where pipeline confidence tuning differs from ours -
# a skill can't ship or control that per-instance config, so Common
# Query participation is the portable fallback. "What is {a} times
# {b}" is a strong candidate for this specific misrouting (same
# "what is X" shape as the confirmed cases), unlike this project
# family's imperative "quiz me on X" skills, which aren't phrased as
# questions at all.
#
# Regex, not fuzzy NLU - the anchor words (plus/minus/times/...) are
# LITERAL in every locale's own intent files (see the module
# docstring above for why: padatious itself can't disambiguate three
# consecutive wildcards without a literal anchor between them). The
# same anchor words are reused here as regex groups splitting on that
# literal text - a safety net for cases the platform's own routing
# failed to hand us properly, not a second implementation of intent
# parsing.
CALC_PATTERNS = {
    "en-us": [
        (re.compile(r"^what(?:'s| is) (.+) plus (.+)$", re.I), "add"),
        (re.compile(r"^what(?:'s| is) (.+) and (.+)$", re.I), "add"),
        (re.compile(r"^what(?:'s| is) (.+) minus (.+)$", re.I), "subtract"),
        (re.compile(r"^what(?:'s| is) (.+) multiplied by (.+)$", re.I), "multiply"),
        (re.compile(r"^what(?:'s| is) (.+) times (.+)$", re.I), "multiply"),
        (re.compile(r"^what(?:'s| is) (.+) divided by (.+)$", re.I), "divide"),
        (re.compile(r"^what(?:'s| is) (.+) percent of (.+)$", re.I), "percentage"),
        (re.compile(r"^what(?:'s| is) (.+) squared$", re.I), "square"),
        (re.compile(r"^what(?:'s| is) the square root of (.+)$", re.I), "square_root"),
    ],
    "da-dk": [
        (re.compile(r"^hvad er (.+) plus (.+)$", re.I), "add"),
        (re.compile(r"^hvad er (.+) minus (.+)$", re.I), "subtract"),
        (re.compile(r"^hvad er (.+) ganget med (.+)$", re.I), "multiply"),
        (re.compile(r"^hvad er (.+) gange (.+)$", re.I), "multiply"),
        (re.compile(r"^hvad er (.+) divideret med (.+)$", re.I), "divide"),
        (re.compile(r"^hvad er (.+) delt med (.+)$", re.I), "divide"),
        (re.compile(r"^hvad er (.+) procent af (.+)$", re.I), "percentage"),
        (re.compile(r"^hvad er (.+) i anden$", re.I), "square"),
        (re.compile(r"^hvad er kvadratroden af (.+)$", re.I), "square_root"),
    ],
}


def _compute(operation, a, b=None):
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        return None if b == 0 else a / b
    if operation == "percentage":
        return a / 100 * b
    if operation == "square":
        return a ** 2
    if operation == "square_root":
        return None if a < 0 else math.sqrt(a)
    return None


def _read_number(raw, lang):
    """The number in a slot as an exact Fraction, or None.

    numtag reads digits in the language's own notation ('3,5' in
    Danish, '3.5' in English) and spoken numbers ('fifteen',
    'femogtyve', 'two and a half'), so the arithmetic below stays
    exact ('0.1 plus 0.2' is 0.3). A lone article ('en', 'a') counts
    as 1 only when the slot holds no other number. A language numtag
    has no lexicon for reads no number, so it degrades to "no match"
    instead of crashing the handler or the Common Query flow."""
    if not raw:
        return None
    try:
        mentions = tag_numbers(str(raw), lang)
    except UnsupportedLanguageError:
        return None
    numbers = [m for m in mentions if Reason.ARTICLE not in m.reasons] or mentions
    return Fraction(numbers[0].value) if numbers else None


class Calculator(OVOSSkill):

    @common_query()
    def handle_common_query(self, phrase, lang):
        """Safety net - see CALC_PATTERNS above. Tries every known
        pattern for this language; the single-operand ones (square,
        square_root) only ever populate group 1, never group 2."""
        lang = lang.lower()
        if lang not in CALC_PATTERNS:
            lang = "en-us"  # both the regex patterns AND number
            # extraction fall back together - using en-us patterns
            # with a different lang's number words would just fail
        patterns = CALC_PATTERNS[lang]
        stripped = phrase.strip().rstrip("?").strip()
        for pattern, operation in patterns:
            m = pattern.match(stripped)
            if not m:
                continue
            groups = m.groups()
            a = _read_number(groups[0], lang)
            if a is None:
                return None
            b = None
            if len(groups) > 1:
                b = _read_number(groups[1], lang)
                if b is None:
                    return None
            result = _compute(operation, a, b)
            if result is None:
                return None
            return str(_format_number(result)), 0.8
        return None

    def _parse_two_numbers(self, message):
        """Shared by add/subtract/multiply/divide/percentage - all
        take an {a} and a {b} slot. Returns (a, b) or (None, None) if
        either failed to parse."""
        a = _read_number(message.data.get("a"), self.lang)
        b = _read_number(message.data.get("b"), self.lang)
        if a is None or b is None:
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
        a = _read_number(message.data.get("a"), self.lang)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        self._speak_result(a ** 2)

    @intent_handler("square_root.intent")
    def handle_square_root(self, message):
        a = _read_number(message.data.get("a"), self.lang)
        if a is None:
            self.speak_dialog("numbers_not_understood")
            return
        if a < 0:
            self.speak_dialog("negative_square_root")
            return
        self._speak_result(math.sqrt(a))

"""Tests for the Common Query safety net (handle_common_query) - see
ovos-skill-geometry/ovos-skill-geography's DEVELOPMENT.md for why
this exists (live-tested platform routing gap, not hypothetical)."""


def test_common_query_add(skill):
    assert skill.handle_common_query("what is 5 plus 6", "en-us") == ("11", 0.8)


def test_common_query_add_and_form(skill):
    assert skill.handle_common_query("what is 5 and 6", "en-us") == ("11", 0.8)


def test_common_query_subtract(skill):
    assert skill.handle_common_query("what is 10 minus 4", "en-us") == ("6", 0.8)


def test_common_query_multiply_times(skill):
    assert skill.handle_common_query("what is 5 times 6", "en-us") == ("30", 0.8)


def test_common_query_multiply_multiplied_by(skill):
    assert skill.handle_common_query("what is 5 multiplied by 6", "en-us") == ("30", 0.8)


def test_common_query_divide(skill):
    assert skill.handle_common_query("what is 20 divided by 4", "en-us") == ("5", 0.8)


def test_common_query_divide_by_zero_returns_none(skill):
    assert skill.handle_common_query("what is 10 divided by 0", "en-us") is None


def test_common_query_percentage(skill):
    assert skill.handle_common_query("what is 15 percent of 200", "en-us") == ("30", 0.8)


def test_common_query_square(skill):
    assert skill.handle_common_query("what is 5 squared", "en-us") == ("25", 0.8)


def test_common_query_square_root(skill):
    assert skill.handle_common_query("what is the square root of 144", "en-us") == ("12", 0.8)


def test_common_query_negative_square_root_returns_none(skill):
    assert skill.handle_common_query("what is the square root of -9", "en-us") is None


def test_common_query_unparseable_numbers_returns_none(skill):
    assert skill.handle_common_query("what is banana plus apple", "en-us") is None


def test_common_query_non_matching_phrase_returns_none(skill):
    assert skill.handle_common_query("play some music", "en-us") is None


def test_common_query_whats_contraction_form(skill):
    assert skill.handle_common_query("what's 5 times 6", "en-us") == ("30", 0.8)


def test_common_query_danish(skill):
    assert skill.handle_common_query("hvad er 5 gange 6", "da-dk") == ("30", 0.8)
    assert skill.handle_common_query("hvad er kvadratroden af 144", "da-dk") == ("12", 0.8)


def test_common_query_falls_back_to_english_for_unknown_lang(skill):
    # lang not in CALC_PATTERNS -> falls back to en-us patterns
    assert skill.handle_common_query("what is 5 plus 6", "xx-xx") == ("11", 0.8)

# Development

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-calculator.git
cd ovos-skill-calculator
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_formatting.py` covers the `_format_number()` fix
specifically. `tests/test_operations.py` covers all seven operations,
including division-by-zero, negative square roots, and unparseable
input.

## Adding a new operation

1. Pick literal anchor words for the intent, following the pattern
   every other operation here uses - see the module docstring for why
   a shared `{operator}` wildcard doesn't work in padatious.
2. Add `locale/en-us/<op>.intent` and the Danish equivalent - basic
   arithmetic vocabulary ("plus", "gange", "divideret med") is common
   elementary-school terminology, higher confidence than some of the
   more specialized translations elsewhere in this project family,
   but still worth a quick sanity check if the new operation uses
   less common terms.
3. Add the handler in `__init__.py`, reusing `_parse_two_numbers()`/
   `_speak_result()` where the operation takes two operands.
4. Add test cases in `test_operations.py` covering the normal case and
   any operation-specific edge case (like divide-by-zero or negative
   square roots).

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`.

## Releasing

Releases are tag-triggered (`v*`):
```bash
git add version.py
git commit -m "chore: bump version to 0.0.X"
git tag vX.Y.Z
git push && git push --tags
```
Triggers `.github/workflows/test.yml` then `.github/workflows/publish.yml`
(PyPI via trusted publishing - see `ovos-skill-convert`'s
DEVELOPMENT.md for the one-time PyPI setup needed before the first
tagged release).

## Style / conventions

- License: GPL-3.0-or-later (matches the other `andlo` skill repos).
- `locale/<lang-code>/` layout, `skill.json` inside each locale folder.
- Present design changes for review before implementing.

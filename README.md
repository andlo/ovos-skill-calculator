# <img src='icon.png' card_color='#4085DB' width='50' height='50' style='vertical-align:bottom'/> Calculator

A basic calculator for OVOS - "what is 15 times 23", "what is the
square root of 144", "what is 20 percent of 150". Fully offline, pure
arithmetic, no external dependencies beyond number parsing.

[![Tests](https://github.com/andlo/ovos-skill-calculator/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-calculator/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-calculator.svg)](https://pypi.org/project/ovos-skill-calculator/)

## Usage
```
"what is 5 plus 3"
"what is 15 times 23"
"what is 100 divided by 4"
"what is 20 percent of 150"
"what is 9 squared"
"what is the square root of 144"
"hvad er 5 plus 3"                (Danish)
"hvad er kvadratroden af 144"     (Danish)
```

## Why one intent file per operation

A single intent like `"what is {a} {operator} {b}"`, with the
operator word captured as a wildcard, does **not** work reliably in
padatious: with three consecutive wildcards and no literal anchor
word between `{a}`, `{operator}`, and `{b}`, the matcher can't tell
where one wildcard ends and the next begins. Each operation gets its
own intent file instead, with the operator as literal text - the same
anchor-word pattern every other intent in this project family uses
(e.g. `ovos-skill-convert`'s `"convert {value} {from_unit} to
{to_unit}"`).

## A rough edge fixed here (not yet back-ported elsewhere)

`ovos-skill-convert`, `ovos-skill-tuning-fork`, and
`ovos-skill-rhythm-box` all documented a cosmetic issue: whole-number
results spoken with a trailing ".0" (e.g. "10.0" instead of "10"),
because Python's default float formatting was used as-is. This skill
fixes it with a small `_format_number()` helper - a whole-number
float speaks as a plain integer, a genuine fraction rounds to 4
decimal places. Worth porting the same helper to the other skills
later; not done retroactively here to keep this change scoped to a
new skill rather than touching several existing ones at once.

## Install
```bash
pip install ovos-skill-calculator
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Category
**Utility**

## Tags
#calculator #math #arithmetic

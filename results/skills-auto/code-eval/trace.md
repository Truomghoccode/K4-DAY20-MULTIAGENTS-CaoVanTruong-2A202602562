### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: read_file
{"file_path": "skills/code-change-compliance/SKILL.md", "limit": 1000}

### Tool call: read_file
{"file_path": "skills/code-maintenance-conventions/SKILL.md", "limit": 1000}

### Tool result
@@ lines 1-10 of 10 @@
---
name: code-change-compliance
description: Use when fixing bugs or making changes in a Python package that has repository-level quality requirements.
---
1. Inspect the package, existing tests, and changelog before editing; identify all public functions affected by the change.
2. Add type annotations to every parameter and return value of every public function in the package.
3. Create `tests/test_regressions.py` with one test function per fixed bug, and include at least three regression tests.
4. Record every fix in `CHANGELOG.md` under `## Unreleased`, using bullets exactly in the form `- fix(<function name>): <short description>`; include at least three bullets.
5. Run the documented test command from the documented working directory. Do not treat a failed collection or “no tests ran” as a passing check.
6. Self-check: confirm the regression test file exists, all required changelog bullets are present, public functions are annotated, and the full test suite passes.

### Tool result
@@ lines 1-9 of 9 @@
---
name: code-maintenance-conventions
description: Use when fixing bugs or improving a code package that requires tests, annotations, and changelog updates.
---
1. Add type annotations to every parameter and return value of every public function (a name not starting with `_`).
2. Create `tests/test_regressions.py` with one passing test function per fixed bug, and at least 3 tests.
3. In `CHANGELOG.md`, add a `## Unreleased` heading and record each fix as a bullet in this exact format: `- fix(<function name>): <short description>`.
4. Run the documented test command from the package’s required working directory; do not treat a test run that fails during collection as validation.
5. Self-check: public annotations are complete, regression tests cover each fix, and the changelog has at least 3 correctly formatted fix bullets.

### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/bookings"}

### Tool call: ls
{"path": "workspace/tests"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/README.md", "limit": 1000}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py", "limit": 1000}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: execute
{"command": "python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "python -m pytest tests -q", "timeout": 3600}

### Tool result
Running teardown with pytest sessionfinish...

no tests ran in 0.01s

[stderr] ERROR: file or directory not found: tests

Exit code: 4
[Command failed with exit code 4]

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 3600}

### Tool result
FF.                                                                      [100%]Running teardown with pytest sessionfinish...

================================== FAILURES ===================================
______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

~\OneDrive\Documents\K4-DAY20-MULTIAGENTS-CaoVanTruong-2A202602562\tasks\code-eval\workspace\tests\test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
bookings\schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings\schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'


### Tool call: write_file
{"file_path": "workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    value = text.strip()\n    match = re.fullmatch(r\"(?:(\\d+)h)?(?:(\\d+)m)?\", value)\n    if match and any(part is not None for part in match.groups()):\n        hours, minutes = match.groups()\n        return int(hours or 0) * 60 + int(minutes or 0)\n\n    match = re.fullmatch(r\"(\\d+):(\\d{1,2})\", value)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n\n    if re.fullmatch(r\"\\d+\", value):\n        return int(value)\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool call: write_file
{"file_path": "workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes: int, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    if block <= 0:\n        raise ValueError(\"block must be > 0\")\n    return (minutes + block - 1) // block\n"}

### Tool result
Updated file /workspace/bookings/billing.py

### Tool call: write_file
{"file_path": "workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom collections.abc import Iterable\n\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations: Iterable[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(duration) for duration in durations)\n\n\ndef add_slot(slot: str, slots: Iterable[str] | None = None) -> list[str]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return [*(slots or []), slot]\n"}

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool call: write_file
{"file_path": "workspace/bookings/calendar_export.py", "content": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)\n"}

### Tool result
Updated file /workspace/bookings/calendar_export.py

### Tool call: write_file
{"file_path": "workspace/tests/test_regressions.py", "content": "import pytest\n\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot\nfrom bookings.timeutil import parse_duration\n\n\ndef test_parse_duration_accepts_all_documented_formats():\n    assert [parse_duration(value) for value in (\"1h30m\", \"2h\", \"45m\", \"1:30\", \"45\")] == [90, 120, 45, 90, 45]\n\n\ndef test_billable_blocks_rounds_up_and_rejects_negative_minutes():\n    assert billable_blocks(16) == 2\n    assert billable_blocks(0) == 0\n    with pytest.raises(ValueError):\n        billable_blocks(-1)\n\n\ndef test_add_slot_does_not_mutate_or_share_input_lists():\n    original = [\"existing\"]\n    result = add_slot(\"new\", original)\n    assert result == [\"existing\", \"new\"]\n    assert original == [\"existing\"]\n    assert add_slot(\"a\") == [\"a\"]\n    assert add_slot(\"b\") == [\"b\"]\n"}

### Tool result
Updated file /workspace/tests/test_regressions.py

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n", "new_string": "## Unreleased\n\n- fix(parse_duration): support every documented duration format\n- fix(billable_blocks): round partial blocks up and validate inputs\n- fix(add_slot): return a fresh list without mutating caller state\n"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 3600}

### Tool result
......                                                                   [100%]Running teardown with pytest sessionfinish...

6 passed in 0.03s

[Command succeeded with exit code 0]

### Assistant
Fixed duration parsing, billable-block rounding and validation, and `add_slot`’s list handling. Added regression tests and changelog entries; the full test suite passes.

Changed: `workspace/bookings/timeutil.py`, `workspace/bookings/billing.py`, `workspace/bookings/schedule.py`, `workspace/bookings/calendar_export.py`, `workspace/tests/test_regressions.py`, and `workspace/CHANGELOG.md`.
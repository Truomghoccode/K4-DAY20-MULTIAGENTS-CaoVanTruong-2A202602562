### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/bookings"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool call: ls
{"path": "/workspace/tests"}

### Tool call: read_file
{"file_path": "/workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/__init__.py"}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

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
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool call: read_file
{"file_path": "/workspace/tests/test_bookings.py"}

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
{"command": "python -m pytest -q workspace/tests", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "python -m pytest -q workspace/tests", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "python -m pytest -q workspace/tests"}

### Tool result
Running teardown with pytest sessionfinish...

=================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py ______________
ImportError while importing test module '~\AppData\Local\Temp\lab_sandbox_b3c3n6i5\workspace\tests\test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\..\..\miniconda3\envs\aivn\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\..\OneDrive\Documents\K4-DAY20-MULTIAGENTS-CaoVanTruong-2A202602562\tasks\code-eval\workspace\tests\test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ===========================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.62s

Exit code: 2
[Command failed with exit code 2]

### Tool call: edit_file
{"file_path": "/workspace/bookings/billing.py", "old_string": "    return round(minutes / block)", "new_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n    return (minutes + block - 1) // block"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/schedule.py", "old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return list(slots or []) + [slot]"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/timeutil.py", "old_string": "    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "new_string": "    if not isinstance(text, str):\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    value = text.strip()\n    match = re.fullmatch(r\"(\\d+)h(?:(\\d+)m)?\", value)\n    if match:\n        hours = int(match.group(1))\n        minutes = int(match.group(2) or 0)\n        return hours * 60 + minutes\n\n    match = re.fullmatch(r\"(\\d+)m\", value)\n    if match:\n        return int(match.group(1))\n\n    match = re.fullmatch(r\"(\\d+):(\\d{2})\", value)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n\n    match = re.fullmatch(r\"\\d+\", value)\n    if match:\n        return int(value)\n\n    raise ValueError(f\"bad duration: {text!r}\")"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/calendar_export.py", "old_string": "    return start_minute + parse_duration(duration_text)", "new_string": "    return (start_minute + parse_duration(duration_text)) % (24 * 60)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/calendar_export.py'

### Tool call: execute
{"command": "python -c \"import sys; sys.path.insert(0, 'workspace'); import pytest; raise SystemExit(pytest.main(['-q', 'workspace/tests']))\""}

### Tool result
...                                                                      [100%]Running teardown with pytest sessionfinish...

3 passed in 0.03s

[Command succeeded with exit code 0]

### Tool call: edit_file
{"file_path": "/workspace/bookings/calendar_export.py", "old_string": "    return (start_minute + parse_duration(duration_text)) % (24 * 60)", "new_string": "    return start_minute + parse_duration(duration_text)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/calendar_export.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/schedule.py", "old_string": "    return list(slots or []) + [slot]", "new_string": "    return list(slots if slots is not None else []) + [slot]"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: execute
{"command": "python -c \"import sys; sys.path.insert(0, 'workspace'); import pytest; raise SystemExit(pytest.main(['-q', 'workspace/tests']))\""}

### Tool result
...                                                                      [100%]Running teardown with pytest sessionfinish...

3 passed in 0.03s

[Command succeeded with exit code 0]

### Assistant
Updated `billing.py` to round billable blocks up and reject negative minutes, `schedule.py` to return a fresh list from `add_slot`, and `timeutil.py` to parse all documented duration formats. The test suite passes.
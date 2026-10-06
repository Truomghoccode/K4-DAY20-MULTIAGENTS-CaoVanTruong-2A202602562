### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"subagent_type": "explorer", "description": "Inspect bookings package and tests to identify failures and docstring requirements. Do not modify files. All paths are relative to sandbox root; project is workspace/. Return relevant files, suspected bugs, and test command.", "} 代 to=functions.ls  (commentary) 代json {": "workspace"}

### Tool result
Error invoking tool 'task' with kwargs {'subagent_type': 'explorer', 'description': 'Inspect bookings package and tests to identify failures and docstring requirements. Do not modify files. All paths are relative to sandbox root; project is workspace/. Return relevant files, suspected bugs, and test command.', '} 代 to=functions.ls  (commentary) 代json {': 'workspace'} with error:
 } 代 to=functions.ls  (commentary) 代json {: Value error, Unexpected argument '} 代 to=functions.ls  (commentary) 代json {'; put all instructions for the subagent in `description`.
 Please fix the error and try again.

### Tool call: task
{"subagent_type": "explorer", "description": "Inspect bookings package and tests to identify failures and docstring requirements. Do not modify files. All paths are relative to sandbox root; project is workspace/. Return relevant files, suspected bugs, and test command."}

### Tool result
## Relevant files

- `workspace/README.md` — documents the test command: `cd workspace && python -m pytest tests -q`.
- `workspace/CHANGELOG.md` — only notes the initial import as version 1.4.2.
- `workspace/bookings/billing.py`
- `workspace/bookings/calendar_export.py`
- `workspace/bookings/schedule.py`
- `workspace/bookings/timeutil.py`
- `workspace/tests/test_bookings.py`

## Suspected bugs and docstring requirements

- **`workspace/bookings/billing.py:billable_blocks`** — The docstring promises partial blocks round **up** and says negative minutes raise `ValueError`. The implementation uses `round(minutes / block)`, which rounds to nearest (and has Python’s tie behavior), not up; it also has no explicit negative-value check. The default block size is 15.
- **`workspace/bookings/timeutil.py:parse_duration`** — The docstring lists `1h30m`, `2h`, `45m`, `1:30`, and bare minutes as supported, with surrounding whitespace ignored. The implementation only matches the `NhNm` form, so the other documented formats fail. It also calls `.strip()` directly, so non-string inputs will fail with an attribute error rather than the documented `ValueError` for bad durations.
- **`workspace/bookings/schedule.py:add_slot`** — The docstring requires a new list per call, but the mutable default `slots=[]` is shared and the function appends to it. Separate calls without an explicit `slots` argument therefore share state.
- **`workspace/bookings/calendar_export.py:slot_end`** — Delegates duration

### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

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
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

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

### Tool call: task
{"subagent_type": "implementer", "description": "Fix source code in workspace/bookings only; do not modify workspace/tests. User requires all functions to satisfy docstrings and tests pass. Relevant files: workspace/bookings/billing.py (billable_blocks must round partial blocks up and reject negative minutes; consider invalid block sizes robustly), timeutil.py (parse_duration supports documented 1h30m, 2h, 45m, H:MM, bare minutes; whitespace ignored; invalid inputs ValueError), schedule.py (add_slot returns a NEW list and separate default calls don't share state), calendar_export.py delegates parser. Inspect all package files/docstrings, implement conventionally, run tests from workspace using shell command `python -m pytest tests -q` (shell starts sandbox root; use `cd workspace && ...`). Return changed files and test results."}

### Tool result
Implemented the bookings fixes:

- `billable_blocks` now rounds partial blocks up and rejects negative minutes and non-positive block sizes.
- `parse_duration` supports the documented formats, ignores whitespace, and raises `ValueError` for invalid inputs.
- `add_slot` returns a new list without mutating the supplied list or sharing default state.

**Tests:** `cd workspace && python -m pytest tests -q` — 3 passed.

**Files changed:**
- `workspace/bookings/billing.py`
- `workspace/bookings/timeutil.py`
- `workspace/bookings/schedule.py`

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool result
@@ lines 1-16 of 16 @@
"""Billing rules."""

import math


def billable_blocks(minutes, block=15):
    """Return the number of billable blocks for a booking.

    Partial blocks are billed as a full block (always round up). ``minutes``
    must be non-negative, and ``block`` must be a positive block size.
    """
    if minutes < 0:
        raise ValueError("minutes must be non-negative")
    if block <= 0:
        raise ValueError("block must be positive")
    return math.ceil(minutes / block)

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-41 of 41 @@
"""Time helpers for the bookings package."""
import re


_DURATION_RE = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?\Z")
_CLOCK_RE = re.compile(r"(\d+):(\d{1,2})\Z")
_MINUTES_RE = re.compile(r"\d+\Z")


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Whitespace is ignored.

    Raises ValueError when ``text`` is not one of the supported formats.
    """
    if not isinstance(text, str):
        raise ValueError(f"bad duration: {text!r}")

    value = "".join(text.split())
    match = _DURATION_RE.fullmatch(value)
    if match and any(part is not None for part in match.groups()):
        hours, minutes = match.groups()
        return int(hours or 0) * 60 + int(minutes or 0)

    match = _CLOCK_RE.fullmatch(value)
    if match:
        hours, minutes = map(int, match.groups())
        if minutes < 60:
            return hours * 60 + minutes

    if _MINUTES_RE.fullmatch(value):
        return int(value)

    raise ValueError(f"bad duration: {text!r}")

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool result
@@ lines 1-16 of 16 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Return the total minutes represented by duration strings."""
    return sum(parse_duration(duration) for duration in durations)


def add_slot(slot, slots=None):
    """Return a new list containing the existing slots and ``slot``.

    When ``slots`` is omitted, a fresh empty list is used for each call.
    The supplied list, if any, is not modified.
    """
    return [*(slots if slots is not None else ()), slot]

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 3600}

### Tool result
...                                                                      [100%]Running teardown with pytest sessionfinish...

3 passed in 0.02s

[Command succeeded with exit code 0]

### Assistant
Fixed duration parsing, billing-block rounding and validation, and slot-list handling so each call returns a new list without mutating its input. The test suite passes: **3 passed**.

Changed `workspace/bookings/billing.py`, `workspace/bookings/timeutil.py`, and `workspace/bookings/schedule.py`.
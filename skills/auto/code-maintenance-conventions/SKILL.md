---
name: code-maintenance-conventions
description: Use when fixing bugs or improving a code package that requires tests, annotations, and changelog updates.
---
1. Add type annotations to every parameter and return value of every public function (a name not starting with `_`).
2. Create `tests/test_regressions.py` with one passing test function per fixed bug, and at least 3 tests.
3. In `CHANGELOG.md`, add a `## Unreleased` heading and record each fix as a bullet in this exact format: `- fix(<function name>): <short description>`.
4. Run the documented test command from the package’s required working directory; do not treat a test run that fails during collection as validation.
5. Self-check: public annotations are complete, regression tests cover each fix, and the changelog has at least 3 correctly formatted fix bullets.

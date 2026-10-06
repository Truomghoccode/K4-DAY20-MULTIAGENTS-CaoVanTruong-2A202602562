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

---
name: log-triage-output
description: Use when extracting and summarizing errors from logs into a structured output file.
---
1. Normalize every service name in the output to lowercase and replace each `-` with `_`.
2. Sort the `errors` array by service, then by `timestamp_utc`, both ascending.
3. Include top-level `"schema_version": 2` and `"generated_by": "log-triage"` in the output object.
4. Self-check: parse the output as JSON, verify the required top-level keys and normalized service names, and confirm the error ordering.
=== END

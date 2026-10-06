---
name: log-triage-conventions
description: Use when parsing logs into structured error records and service-level counts.
---
1. Set the top-level JSON fields `schema_version` to `2` and `generated_by` to `log-triage`.
2. Normalize service names in output to lowercase and replace every `-` with `_`.
3. Sort `errors` by normalized service, then by `timestamp_utc`, both ascending.
4. Compute `counts_by_service` by summing each record’s `repeat_count` for that service.
5. Self-check: confirm the required top-level fields, normalized service names, sort order, and repeat-weighted counts agree with the emitted error records.
=== END===

# Task 1 — Transaction reconciliation CLI (txreconcile.py)

Implement `txreconcile.py` in the working directory root. Python standard library only.

CLI: `python txreconcile.py INPUT [--output OUT]`

## Input format
- `.csv`: header row `id,amount,currency,timestamp,status` (line 1); data rows start at line 2. Rows with a wrong number of columns are invalid records.
- `.jsonl`: one JSON object per line (line numbers start at 1). Lines that are not JSON objects are invalid records.
- Other extensions: exit code 1, stderr message.

## Record fields and validation
- `id`: non-empty string.
- `amount`: number strictly greater than 0.
- `currency`: exactly 3 ASCII letters; normalized to UPPERCASE internally.
- `timestamp`: ISO-8601 date (`YYYY-MM-DD`) or datetime (`YYYY-MM-DDTHH:MM[:SS]`); anything else invalid.
- `status`: case-insensitive one of `pending`, `settled`, `failed`, `refunded`; anything else invalid.
A record failing any check is an invalid record: skipped, counted, and reported with its line number.

## Semantics
- Duplicate `id`: for a non-empty string `id`, the first encountered record reserves that ID even if another field makes it invalid; subsequent records with the same ID are duplicates (neither valid nor invalid) and are reported in `duplicate_ids` (sorted list). The first invalid record still increments `invalid_records` and is reported in `errors`.
- Blank or whitespace-only lines (CSV and JSONL) are ignored: they are not records, not counted, and produce no errors.
- Totals per currency: `settled_sum` = sum of settled amounts, `refunded_sum` = sum of refunded amounts, `net = settled_sum - refunded_sum`. `pending` and `failed` count as valid but contribute to no sums. A currency appears in `totals` only if it has at least one valid `settled` or `refunded` record; currencies seen only via `pending`/`failed` records do not appear in `totals`.

## Output (stdout, UTF-8 JSON object)
Keys: `total_records` (all data records encountered, incl. invalid and duplicate), `valid_records` (unique valid first occurrences), `invalid_records`, `duplicate_ids`, `totals` (map currency -> {settled_sum, refunded_sum, net}), `errors` (list of `{"line": int, "reason": str}`).
All sums are rounded to 2 decimal places. Output must be deterministic: identical input produces byte-identical stdout (stable key order, sorted lists).
- `--output OUT`: additionally write the same JSON object to OUT. The file must parse to the same JSON object as stdout.

## Exit codes
- 0: processed successfully (even with invalid records).
- 1: unsupported input extension.
- 2: missing arguments, or input file missing/unreadable (stderr message required).

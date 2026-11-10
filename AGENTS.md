# Global instructions

## Gyro Gyro S via Strata

Apply these when the session model is `strata/gyro-gyro-s`. They are suggestions,
not hard rules: follow them unless they conflict with an explicit user request.

### Prompt cache reuse is the main performance priority
- Keep the conversation and the current task stable; do not jump to unrelated
  topics or new conversations mid-task.
- Complete related operations in one continuous work batch.
- Stay on the current task until it is finished or genuinely blocked.
- Reuse context you already have instead of re-reading the same files.

### Batch work by task
- Group file reading, analysis, editing and verification per task, in one batch.
- Prefer sequential execution over several independent Gyro-S requests.
- Do not launch Gyro-S subagents with independent contexts for work the current
  session can do; if a subagent is truly needed, pass it the full context.
- Optimize total task completion time, not only token generation time.

## Windows test commands and edits (Strata models)

Apply these when the session model is `strata/gyro-gyro-s` or
`strata/coder-iq1_m`. They are suggestions, not hard rules: follow them unless
they conflict with an explicit user request.

- The Windows shell is PowerShell: `ls` is a `Get-ChildItem` alias, so Unix
  flags such as `ls -la` fail. Use `Get-ChildItem -Force` to list hidden files.
- In PowerShell, Python's `unittest` writes normal progress and `OK` to stderr.
  Do not interpret stderr or `NativeCommandError` alone as a failed test. Avoid
  piping `2>&1` through PowerShell: it can turn successful tests into exit code 1.
  Run, for example, `cmd /c "python -m unittest test_module -v 2>&1"; exit $LASTEXITCODE`
  so the shell tool receives the real result. Preserve and inspect actual
  failures before changing tests.
- Before an edit, verify that the old and new text differ and that the target
  exists. For the `edit` tool, include all required fields: `path`, `oldString`,
  and `newString` in every call, even when editing the same file repeatedly.
  Do not issue no-op edit calls.

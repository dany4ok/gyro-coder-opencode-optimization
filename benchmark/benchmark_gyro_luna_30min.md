# TASK: AI Coding Benchmark — Maximum 30 Minutes

## Objective

Determine which configuration is most efficient for real-world coding tasks:

- **A:** Gyro-S alone (`strata/gyro-gyro-s`)
- **B:** Gyro-S as main agent + up to 2 parallel GPT-6 Luna subagents (`openai/gpt-6-luna`)
- **C:** GPT-6 Luna alone (`openai/gpt-6-luna`)

Measure total execution time, code correctness, tool overhead, error recovery, and overall efficiency.

**HARD DEADLINE: 30 minutes wall-clock, including setup, execution, evaluation, and final report.**

## 1. Benchmark design

Create two new, moderately complex Python programming tasks.

**Task 1 — Data processing CLI**

Build a production-style CLI that processes CSV/JSONL transaction files, validates records, performs reconciliation, handles malformed input and produces deterministic reports.

**Task 2 — Cache library**

Build a reusable Python caching library featuring LRU eviction, configurable TTL, thread safety, statistics, persistence, and deterministic expiration testing.

Both tasks must have precise specifications and independent acceptance tests covering normal usage, edge cases and failure conditions.

Target at least 15–20 meaningful acceptance assertions per task.

Prepare the specifications and tests BEFORE running any competing configuration.

Do not modify them between configurations.

## 2. Execution

Run each configuration on both tasks, using separate clean directories and fresh OpenCode sessions.

Total: **6 runs.**

Execution order:

1. Task 1 — Gyro-S alone
2. Task 1 — Gyro-S + Luna
3. Task 1 — Luna alone
4. Task 2 — Luna alone
5. Task 2 — Gyro-S + Luna
6. Task 2 — Gyro-S alone

Reverse the order on Task 2 to reduce ordering bias.

### Configuration A

Gyro-S performs all implementation, testing, debugging and verification itself. No subagents.

### Configuration B

Gyro-S orchestrates the task and may delegate up to two independent subtasks to GPT-6 Luna concurrently.

Gyro-S must minimize context switching and unnecessary KV-cache recomputation.

Delegation overhead must be included in total execution time.

### Configuration C

GPT-6 Luna performs the entire task independently, without subagents.

## 3. Fairness rules

- Identical specifications and external acceptance tests.
- Identical starting files, dependencies and tool access.
- Fresh sessions and isolated workspaces.
- Same initial task instructions, except for delegation policy.
- No sharing generated solutions between runs.
- No reuse of implementation artifacts from previous runs.
- Keep acceptance tests outside agents' editable workspaces.
- Use real executions and real wall-clock measurements.
- Do not estimate or invent metrics.
- Preserve completed outputs and logs.
- Confirm each run actually uses its assigned model.
- Avoid concurrent runs that compete for the same local hardware, unless explicitly measured as part of the configuration. Parallel Luna subagents **within** configuration B are permitted.

## 4. Strict time budget

Total experiment limit: **1800 seconds**.

Allocate:

- Preparation: maximum 120 seconds.
- Six execution slots: maximum 240 seconds each.
- Final evaluation and report: reserve at least 180 seconds.

Use enforceable process-level timeouts, not merely instructions asking an agent to stop.

If a run exceeds its deadline, terminate it, mark it TIMEOUT, preserve its output and evaluate whatever was completed.

Do not extend the experiment beyond 30 minutes.

If setup exceeds its allocation, reduce remaining execution time rather than extending the deadline.

Stop launching new runs when there is insufficient time for execution and reporting.

## 5. Metrics

For every run record:

- Total wall-clock time.
- Success, partial success, failure or timeout.
- Independent acceptance tests passed/failed/skipped.
- Correctness score as percentage of applicable acceptance tests.
- Tool calls and retries, separated by main agent and subagents where observable.
- Delegation overhead, if measurable.
- Number and type of errors.
- Time spent on implementation, testing and correction, where measurable.
- KV-cache reuse, cache misses and prefill time, only if Strata exposes reliable metrics.
- Unnecessary repeated operations and context switches, where observable.
- Number of lines/files changed.

Do not mistake fewer tool calls for higher efficiency.

Do not reward speed if correctness is substantially worse.

## 6. Evaluation

Calculate:

1. Average completion time per configuration.
2. Speedup relative to Gyro-S alone.
3. Correctness and reliability.
4. Time lost to errors and retries.
5. Whether delegation improved total completion time.
6. Whether keeping Gyro-S continuously active was beneficial.
7. Whether Luna alone eliminates enough orchestration overhead to outperform the other configurations.

Distinguish measured results from hypotheses.

If a configuration fails or times out, do not calculate its successful completion time as though it finished.

Identify the winner for each task separately and the overall winner, if supported by the results.

## 7. Output

Save specifications, logs, raw metrics and report inside a new benchmark directory.

Create `results.json` and `REPORT.md`.

The final report must be **in Romanian** and contain:

- Comparison table for all 6 runs.
- Average times and correctness scores.
- Speedup percentages.
- Errors and limitations.
- Explanation of which architecture performed best and why.
- Recommended default configuration for my OpenCode + Strata setup.
- Clear rules for when to use Gyro-S alone, Gyro-S + Luna or Luna alone.
- Whether additional testing is required for a reliable conclusion.

**Start immediately. Do not ask for confirmation.**

Do not modify my existing OpenCode or Strata configuration.

Prioritize experimental fairness, objective measurements and the strict 30-minute deadline.

# Gyro-S / Coder OpenCode + Strata settings

Local serving settings and agent instructions for two local Strata models used through OpenCode.

## What changed

| File | Change |
| --- | --- |
| `opencode.json` (not tracked; see `opencode.json.example`) | Added a `coder-iq1_m` model entry: `limit.context` 131072, `limit.output` 16384, `settings.cache.warming` false. |
| `AGENTS.md` | The Windows test/edit guidance now applies to both `strata/gyro-gyro-s` and `strata/coder-iq1_m`. The Gyro-S-specific prompt-cache and batching sections stay gated to Gyro-S. |

### Why these values

- `limit.context: 131072` matches the engine's real `--max-context`. Without it, OpenCode assumes the catalog fallback of 200000 tokens for a model that is not in the catalog, so compaction decisions target a window the engine cannot hold.
- `limit.output: 16384` caps generated tokens per model step instead of the 32000 fallback. A lower cap truncates large tool payloads mid-write, so this is the ceiling chosen for the local models.
- `settings.cache.warming: false` disables OpenCode's periodic keep-alive requests for these sessions. Warming is already off by default; the setting only makes it explicit. Historically it was `interval: 3 minutes, duration: 45 minutes`, which sent full-context requests every few minutes.

## Measured comparison (single A/B pair)

Same short task (currency must appear uppercase in a report) and the same external acceptance suite in both runs.

| Run | Wall time | Timeout | External acceptance | HTTP requests | `max_completion_tokens` | Tool calls |
| --- | --- | --- | --- | --- | --- | --- |
| Coder baseline | 123.0 s | no | 20 passed | 13 | 32000 | 14 |
| Coder with these settings | 103.1 s | no | 20 passed | 11 | 16384 | 12 |

Limitations: one run per configuration, no repeated trials. The experimental variant changed the output limit and the Windows guidance together, so the gain is not attributed to a single setting. `cache.warming` was not a factor, since both runs had warming off. Gyro-S memory thresholds (`STRATA_RESIDENT_HEADROOM_GIB`, `--vram-reserve-mib`) were not changed.

## Applying it locally

Set the gateway credential as a runtime variable rather than in the file:

```powershell
$env:STRATA_LOCAL_TOKEN = "<the token Strata wrote for the instance>"
```

The gateway port above is the local Strata desktop gateway. `strata/coder-iq1_m` only appears in `/models` after the Coder instance is loaded in Strata's model settings.

## Rollback

Local backups kept beside the config: `opencode.json.bak-coder-limits-*` and `AGENTS.md.bak-coder-guidance-*`. Restore by copying over the current file.

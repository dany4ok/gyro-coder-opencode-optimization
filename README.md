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

## Visual review gate (spritesheets and generated images)

| File | Change |
| --- | --- |
| `opencode.json.example` | Reviewer system prompt now requires opening images with `read`, returning `CANNOT VERIFY VISUALS` + Partially Verified when it cannot see them, treating a claimed fix as a hypothesis, and never calling a visual defect "intentional design" based on code text. |
| `AGENTS.md` | New "Review pentru sarcini vizuale" section: explicit per-frame criteria, judge pixels not code, inspect frame by frame at full size, run deterministic measurement before the verdict, and include criteria + measurement in the verdict. |
| `tools/check_atlas_frames.py` | New deterministic atlas/spritesheet checker (Pillow + OpenCV + NumPy). No AI involved. |

### Why

In an isolated `v2` worktree, a reviewer (vision-capable model) opened `atlas_player.png` and still returned `✓ Verified`, claiming "consistent heights" and calling the upright "death" frame intentional design because the code prompt said so. Another reviewer claimed visual verification without opening any image. The primary agent had reported the upright death frame as "cosmetic". Direct measurement showed frame 4 at 325 px versus frame 5 at 255 px — a 22 % height difference. A passing build and 27/27 JS tests say nothing about pixels.

### Script

```powershell
python tools/check_atlas_frames.py sprites/atlas_player.png --cols 4 --rows 2
```

For every cell it reports: empty or not, silhouette bounding box, pixel area, mean colour and colour distance from the median frame. It flags empty frames, height/area spread over the thresholds and palette drift. Exit codes: `0` PASS, `1` FAIL (confirmed visual defect), `2` bad input. Thresholds (`--max-height-spread` 0.12, `--max-area-spread` 0.45, `--palette-tol` 55) are configurable.

Measured on the two sheets from that session:

| Sheet | Result |
| --- | --- |
| `atlas_player.png` | FAIL — height spread 22 %, cell 5 = 255 px vs cell 4 = 325 px |
| `atlas_snake.png` | FAIL — height spread 61 %, cell 3 = 322 px vs cell 1 = 127 px |

The snake result is a striking pose, not necessarily a defect; the point is that the difference is now measured and must be accepted explicitly instead of being waved away as cosmetic.

### Applying it locally

Copy the `agents.reviewer` block from `opencode.json.example` into your real `opencode.json` (which is gitignored because it holds credentials), then follow the visual-review section in `AGENTS.md`.

## Rollback

Local backups kept beside the config: `opencode.json.bak-coder-limits-*` and `AGENTS.md.bak-coder-guidance-*`. Restore by copying over the current file.

## Investigation archive

This repository also carries the earlier Gyro-S investigation merged from `dany4ok/gyro-s-opencode-optimization`:
`benchmark/` (task specs plus the unchanged external acceptance suites), `reports/` (one file per experiment),
`tools/`, `fixes/`, `experiments/`, `notes/` and `docs/`. The archive README is kept at
`docs/gyro-s-investigation-2026-11-10.md`; its reports describe single-run A/B tests, so timings there are not
repeated measurements.

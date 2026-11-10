"""Analyze isolated Strata metrics snapshots without treating rolling windows as counters."""
import json
import re
import sys
from pathlib import Path

ENGINE = re.compile(r'prompt (\d+) tokens = (\d+) reused \+ (\d+) read in .*? generated in ')


def analyze(before, after, log_text):
    old, new = before.get('totals', {}), after.get('totals', {})
    keys = ('requests', 'reused', 'prompt_tokens')
    valid = (old.get('since') is not None and old.get('since') == new.get('since') and
             all(type(old.get(k)) is int and type(new.get(k)) is int and new[k] >= old[k] for k in keys))
    matches = [tuple(map(int, m.groups())) for m in ENGINE.finditer(log_text)]
    cache_old, cache_new = before.get('conversation_cache', {}), after.get('conversation_cache', {})
    return {
        'legacy_window_request_delta': cache_new.get('requests', 0) - cache_old.get('requests', 0),
        'legacy_window_reused_request_delta': cache_new.get('requests_reused', 0) - cache_old.get('requests_reused', 0),
        'cumulative_valid': valid,
        'cumulative_completed_request_delta': new['requests'] - old['requests'] if valid else None,
        'cumulative_reused_tokens_delta': new['reused'] - old['reused'] if valid else None,
        'cumulative_prompt_tokens_delta': new['prompt_tokens'] - old['prompt_tokens'] if valid else None,
        'engine_log_completed_lines': len(matches),
        'engine_log_lines_with_reuse': sum(reused > 0 for _, reused, _ in matches),
        'engine_log_reused_tokens': sum(reused for _, reused, _ in matches),
        'note': 'Window differences are not request counts; log coverage is not guaranteed; totals include all traffic in the snapshot interval.',
    }


if __name__ == '__main__':
    snapshot = json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    log = Path(sys.argv[2]).read_text(encoding='utf8', errors='replace')
    print(json.dumps(analyze(snapshot['before'], snapshot['after'], log), indent=2))

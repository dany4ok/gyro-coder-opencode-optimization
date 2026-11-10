import unittest
from metrics_delta import analyze


def snap(req, hits, total, reused, prompt, since=10):
    return {'conversation_cache': {'requests': req, 'requests_reused': hits},
            'totals': {'since': since, 'requests': total, 'reused': reused, 'prompt_tokens': prompt}}


class MetricsDeltaTest(unittest.TestCase):
    def test_rolling_window_can_stay_full_and_reused_go_down(self):
        before = snap(500, 396, 526, 1000, 2000)
        after = snap(500, 395, 533, 1200, 2400)
        r = analyze(before, after, 'strata serve: prompt 15 tokens = 12 reused + 3 read in 8 ms, 2 generated in 4 ms\n')
        self.assertEqual((r['legacy_window_request_delta'], r['legacy_window_reused_request_delta']), (0, -1))
        self.assertEqual((r['cumulative_completed_request_delta'], r['cumulative_reused_tokens_delta']), (7, 200))
        self.assertEqual((r['engine_log_completed_lines'], r['engine_log_lines_with_reuse']), (1, 1))

    def test_restart_or_counter_decrease_produces_unknown(self):
        for after in (snap(2, 1, 2, 1, 10, since=11), snap(2, 1, 2, 1, 10)):
            r = analyze(snap(500, 400, 526, 1000, 2000), after, '')
            self.assertFalse(r['cumulative_valid'])
            self.assertIsNone(r['cumulative_completed_request_delta'])

    def test_missing_since_is_not_comparable(self):
        before = snap(1, 1, 1, 1, 10)
        after = snap(2, 2, 2, 2, 20)
        del before['totals']['since']
        self.assertIsNone(analyze(before, after, '')['cumulative_prompt_tokens_delta'])


if __name__ == '__main__':
    unittest.main()

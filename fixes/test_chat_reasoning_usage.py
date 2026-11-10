"""Chat Completions must report counted reasoning tokens without guessing."""

import unittest

from serve.server import openai_chunks, openai_collect


class _Service:
    def model_for(self, req):
        return "test-model"


def _usage(reasoning_marker):
    done = {"finish": "stop", "prompt_tokens": 10, "completion_tokens": 12, "reused": 3}
    if reasoning_marker is not _MISSING:
        done["reasoning_tokens"] = reasoning_marker
    chunks = list(openai_chunks(_Service(), {}, [], False, None, 100, None, run=[("done", done)]))
    return chunks[-1]["usage"]


_MISSING = object()


class ChatReasoningUsageTests(unittest.TestCase):
    def test_report_nonzero_and_zero(self):
        for count in (7, 0):
            with self.subTest(count=count):
                usage = _usage(count)
                self.assertEqual(usage["completion_tokens_details"]["reasoning_tokens"], count)
                self.assertEqual(usage["completion_tokens"], 12)
                self.assertEqual(usage["prompt_tokens_details"]["cached_tokens"], 3)

    def test_do_not_invent_invalid_or_missing_counts(self):
        for count in (_MISSING, None, -1, 13, True, "7"):
            with self.subTest(count=count):
                self.assertNotIn("completion_tokens_details", _usage(count))

    def test_nonstream_collect_preserves_reasoning_count(self):
        done = {"finish": "stop", "prompt_tokens": 10, "completion_tokens": 12,
                "reused": 3, "reasoning_tokens": 7}
        chunks = openai_chunks(_Service(), {}, [], False, None, 100, None, run=[("done", done)])
        self.assertEqual(openai_collect(chunks)["usage"]["completion_tokens_details"]["reasoning_tokens"], 7)


if __name__ == "__main__":
    unittest.main()

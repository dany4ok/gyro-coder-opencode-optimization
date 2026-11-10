"""Offline fake-engine experiment; does not start or change the user's model."""
import unittest
import serve.test_server as mock_server


class AnswerRoom16384(unittest.TestCase):
    def test_enabled_then_disabled(self):
        fixture = mock_server.ThinkingBudget(methodName='test_the_answer_room_has_its_limits')
        fixture.setUp()
        try:
            fixture.engine.THOUGHT = 'thinking about the answer. ' * 1000
            fixture.engine.max_context = fixture.engine.known_ctx = 131072
            body = {'model': 'm', 'max_tokens': 16384, 'messages': [{'role':'user','content':'2+2?'}]}
            enabled_status, enabled = fixture.post('/v1/chat/completions', body)
            first_count = len(fixture.engine.prompts)
            fixture.svc.answer_room = False
            disabled_status, disabled = fixture.post('/v1/chat/completions', body)
            second_count = len(fixture.engine.prompts) - first_count
            yes = enabled['choices'][0]
            no = disabled['choices'][0]
            print('enabled:', enabled_status, 'finish=', yes['finish_reason'], 'answer_present=', bool(yes['message'].get('content')), 'engine_segments=', first_count)
            print('disabled:', disabled_status, 'finish=', no['finish_reason'], 'answer_present=', bool(no['message'].get('content')), 'engine_segments=', second_count)
            self.assertEqual((enabled_status, yes['finish_reason'], bool(yes['message'].get('content')), first_count), (200, 'stop', True, 2))
            self.assertEqual((disabled_status, no['finish_reason'], bool(no['message'].get('content')), second_count), (200, 'length', False, 1))
        finally:
            fixture.tearDown()


if __name__ == '__main__':
    unittest.main()

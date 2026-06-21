import asyncio
import json
import unittest
from types import SimpleNamespace

from app.services.deepseek_service import DeepseekService


class FakeCompletions:
    def __init__(self, chunks=None, error=None):
        self.chunks = chunks or []
        self.error = error

    async def create(self, **_kwargs):
        if self.error:
            raise self.error

        async def stream():
            for content in self.chunks:
                yield SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            delta=SimpleNamespace(content=content),
                        )
                    ]
                )

        return stream()


class DeepseekStreamingProtocolTests(unittest.TestCase):
    def create_service(self, completions):
        service = DeepseekService.__new__(DeepseekService)
        service.client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions)
        )
        service.model = "test-model"
        service.cache_enabled = False
        service.cache = None
        return service

    def test_stream_saves_raw_text_and_emits_done(self):
        service = self.create_service(FakeCompletions(["你", "好\n\"朋友\""]))
        saved = {}

        async def on_complete(user_id, conversation_id, messages, response):
            saved.update(
                user_id=user_id,
                conversation_id=conversation_id,
                messages=messages,
                response=response,
            )

        async def collect():
            return [
                event
                async for event in service.generate_stream(
                    messages=[{"role": "user", "content": "问候"}],
                    user_id=1,
                    conversation_id=2,
                    on_complete=on_complete,
                )
            ]

        events = asyncio.run(collect())

        self.assertEqual(json.loads(events[0][6:]), "你")
        self.assertEqual(json.loads(events[1][6:]), "好\n\"朋友\"")
        self.assertEqual(events[-1], "data: [DONE]\n\n")
        self.assertEqual(saved["response"], "你好\n\"朋友\"")

    def test_stream_emits_structured_error_and_done(self):
        service = self.create_service(
            FakeCompletions(error=RuntimeError("upstream unavailable"))
        )

        async def collect():
            return [
                event
                async for event in service.generate_stream(
                    messages=[{"role": "user", "content": "问候"}],
                )
            ]

        events = asyncio.run(collect())
        error = json.loads(events[0][6:])

        self.assertEqual(error["type"], "error")
        self.assertIn("upstream unavailable", error["message"])
        self.assertEqual(events[-1], "data: [DONE]\n\n")


if __name__ == "__main__":
    unittest.main()

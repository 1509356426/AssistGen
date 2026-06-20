import asyncio
import unittest
from unittest.mock import patch

from app.services.conversation_service import ConversationService


class ConversationContextTests(unittest.TestCase):
    def test_get_latest_user_content_returns_last_user_message(self):
        messages = [
            {"role": "user", "content": "第一轮问题"},
            {"role": "assistant", "content": "第一轮回答"},
            {"role": "user", "content": "当前问题"},
        ]

        self.assertEqual(
            ConversationService.get_latest_user_content(messages),
            "当前问题",
        )

    def test_get_context_messages_appends_current_message(self):
        async def fake_get_conversation_messages(conversation_id, user_id):
            self.assertEqual(conversation_id, 7)
            self.assertEqual(user_id, 3)
            return [
                {"sender": "user", "content": "我叫小明"},
                {"sender": "assistant", "content": "你好，小明"},
            ]

        current_messages = [{"role": "user", "content": "我叫什么？"}]
        with patch.object(
            ConversationService,
            "get_conversation_messages",
            new=fake_get_conversation_messages,
        ):
            result = asyncio.run(
                ConversationService.get_context_messages(
                    conversation_id=7,
                    user_id=3,
                    current_messages=current_messages,
                )
            )

        self.assertEqual(
            result,
            [
                {"role": "user", "content": "我叫小明"},
                {"role": "assistant", "content": "你好，小明"},
                {"role": "user", "content": "我叫什么？"},
            ],
        )


if __name__ == "__main__":
    unittest.main()

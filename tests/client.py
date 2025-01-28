import unittest
import os
from pylangdb import LangDb
from pylangdb.types import Message, ThreadCost
from dotenv import load_dotenv

load_dotenv()


class TestLangDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set environment variables for testing
        cls.api_key = os.getenv("LANGDB_API_KEY")
        cls.project_id = os.getenv("LANGDB_PROJECT_ID")
        cls.test_thread_id = os.getenv("LANGDB_TEST_THREAD_ID")

        # Skip tests if environment variables are not set
        if not all([cls.api_key, cls.project_id, cls.test_thread_id]):
            raise unittest.SkipTest(
                "LANGDB_API_KEY, LANGDB_PROJECT_ID, and LANGDB_TEST_THREAD_ID environment variables are required"
            )

    def setUp(self):
        # Initialize LangDb instance
        self.client = LangDb(api_key=self.api_key, project_id=self.project_id)

    def test_completion(self):
        # Test the completion method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"},
        ]
        response = self.client.completion(
            model="gemini-1.5-pro-latest",
            messages=messages,
            temperature=0.7,
            max_tokens=100,
        )
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_get_messages(self):
        # Test the get_messages method
        messages = self.client.get_messages(thread_id=self.test_thread_id)

        # Check return type
        self.assertIsInstance(messages, list)
        self.assertTrue(len(messages) > 0)
        self.assertIsInstance(messages[0], Message)

        # Check message attributes
        first_message = messages[0]
        self.assertIsInstance(first_message.id, str)
        self.assertIsInstance(first_message.thread_id, str)
        self.assertIsInstance(first_message.content, str)
        self.assertIsInstance(first_message.created_at, str)

        # Check that thread_id matches
        self.assertEqual(first_message.thread_id, self.test_thread_id)

    def test_get_cost(self):
        # Test the get_cost method
        cost = self.client.get_cost(thread_id=self.test_thread_id)

        # Check return type
        self.assertIsInstance(cost, ThreadCost)

        # Check cost attributes
        self.assertIsInstance(cost.total_cost, float)
        self.assertIsInstance(cost.total_input_tokens, int)
        self.assertIsInstance(cost.total_output_tokens, int)

        # Check that values are non-negative
        self.assertGreaterEqual(cost.total_cost, 0)
        self.assertGreaterEqual(cost.total_input_tokens, 0)
        self.assertGreaterEqual(cost.total_output_tokens, 0)


if __name__ == "__main__":
    unittest.main()

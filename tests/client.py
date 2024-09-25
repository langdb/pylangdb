import unittest
import os
import pandas as pd
from pylangdb import LangDb, MessageRequest

class TestLangDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set environment variables
        cls.client_id = os.getenv('LANGDB_CLIENT_ID')
        cls.client_secret = os.getenv('LANGDB_CLIENT_SECRET')
        cls.project_id = os.getenv('PROJECT_ID')

    def setUp(self):
        # Initialize LangDb instance
        self.langdb = LangDb(self.client_id, self.client_secret, self.project_id)

    def test_query_df(self):
        # Test the query_df method
        query = "select * from langdb.models"
        result = self.langdb.query_df(query)
        print(result)
        self.assertIsNotNone(result)  # Check that the result is not None
        self.assertIsInstance(result, pd.DataFrame)  # Assuming the result is a DataFrame
        self.assertGreater(len(result), 0) 

    def test_invoke_model(self):
        # Test the invoke_model method
        msg = MessageRequest(
            model_name='review',
            message='You are a terrible product',
            parameters={},
            include_history=False
        )
        response = self.langdb.invoke_model(msg)
        self.assertEqual(response, '1')

    # test get_entities
    def test_get_entities(self):
        # Test the get_entities method
        for ent in ['models', 'providers', 'views', 'prompts']:
            res = self.langdb.get_entities(ent)
            self.assertIsNotNone(res)  # Check that the result is not None
            self.assertIsInstance(res, list)  # Assuming the result is a list
            self.assertGreater(len(res), 0)
if __name__ == '__main__':
    unittest.main()
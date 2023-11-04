import sys
sys.path.append("data_loader_realtime_lambda/")

import unittest
from unittest.mock import patch
from lambda_handler import handler


class TestLambdaHandler(unittest.TestCase):

    @patch('lambda_handler.handler')
    def test_handler_with_valid_input(self, mock_handler):
        mock_handler.return_value = 'Success'
        response = handler({'key': 'value'}, {})
        print("fufufvjhbuihoij;pojpj", response)
        self.assertEqual(response, 'Success')

if __name__ == '__main__':
    unittest.main()
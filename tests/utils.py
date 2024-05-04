import unittest
from unittest.mock import patch, MagicMock

import os
import sys

sys.path.append(os.getcwd())

from jhdsfinder.utils import *


class TestAccessURL(unittest.TestCase):

    @patch("jhds.utils.requests.get")
    def test_access_url_success(self, mock_get):
        # モックの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # テスト対象の関数を呼び出す
        url = "dummy_url"
        response = access_url(url)

        # アサーション
        self.assertEqual(response, mock_response)
        mock_get.assert_called_once_with(url)


if __name__ == "__main__":
    unittest.main()

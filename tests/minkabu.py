import os
import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from jhdsfinder.minkabu import CompanyHTML
from jhdsfinder.names import *

DATA_DIR = os.path.join(os.path.dirname(__file__), DATA_DIRNAME)
TEST_CODE = "1301"
HTML_FILEPATH = os.path.join(DATA_DIR, f"{TEST_CODE}.html")
# HTML内に記載されている値
STOCK_PRICE_VALUE = 3600.0
DIVIDEND_YIELD_VALUE = 2.77
PER_VALUE = 6.67
PSR_VALUE = 0.15
PBR_VALUE = 0.91


class TestResponse:
    text = ""


class TestCompanyHTML(unittest.TestCase):
    with open(HTML_FILEPATH, "r", encoding="utf-8") as file:
        html_content = file.read()
    mock_soup = BeautifulSoup(html_content, "lxml")
    test_response = TestResponse()

    @patch("bs4.BeautifulSoup")
    @patch("jhds.utils.access_url")
    def test_extract_stock_price(self, mock_access_url, mock_beautifulsoup):
        # モック作成
        mock_access_url.return_value = self.test_response
        mock_beautifulsoup.return_value = self.mock_soup
        company_html = CompanyHTML(TEST_CODE)
        company_html.soup = self.mock_soup
        # テスト実行
        mock_access_url.assert_called_once()
        stock_price = company_html.extract_stock_price()
        self.assertEqual(stock_price, STOCK_PRICE_VALUE)

    @patch("bs4.BeautifulSoup")
    @patch("jhds.utils.access_url")
    def test_extract_data(self, mock_access_url, mock_beautifulsoup):
        # モック作成
        mock_access_url.return_value = self.test_response
        mock_beautifulsoup.return_value = self.mock_soup
        company_html = CompanyHTML(TEST_CODE)
        company_html.soup = self.mock_soup
        # テスト実行
        data = company_html.extract_data()
        self.assertEqual(data[STOCK_PRICE], STOCK_PRICE_VALUE)
        self.assertEqual(data[DIVIDEND_YIELD], DIVIDEND_YIELD_VALUE)
        self.assertEqual(data[PER], PER_VALUE)
        self.assertEqual(data[PSR], PSR_VALUE)
        self.assertEqual(data[PBR], PBR_VALUE)


if __name__ == "__main__":
    unittest.main()

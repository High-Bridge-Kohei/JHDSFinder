import unittest
from unittest.mock import patch, MagicMock

import os
from jhdsfinder.dataframe import *
from test_utils import *

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

TEST_CODE = "1301"
TEST_FY_CSV_FILENAME = f"{TEST_CODE}_{FY_CSV_FILENAME}"
DF_CSV_FILENAME = f"{TEST_CODE}_df.csv"
FY_CSV_FILEPATH = os.path.join(DATA_DIR, TEST_FY_CSV_FILENAME)
DF_CSV_FILEPATH = os.path.join(DATA_DIR, DF_CSV_FILENAME)

TEST_MARKET_EXCEL_FILEPATH = os.path.join(DATA_DIR, MARKET_EXCEL_FILENAME)
TEST_MARKET_CSV_FILEPATH = os.path.join(DATA_DIR, MARKET_CSV_FILENAME)


class TestTextToDfMethod(unittest.TestCase):
    shape = (16, 28)

    def test_text_to_df(self):
        with open(DF_CSV_FILEPATH, "r") as f:
            text = f.read()
        df = text_to_df(text)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(df.shape, self.shape)


class TestCompanyPerformanceDataFrameClass(unittest.TestCase):

    @patch("jhds.dataframe.CompanyPerformanceDataFrame.read_csv_as_text")
    def test_read_url(self, mock_read_csv_as_text):
        # モックを使ってread_csv_as_textメソッドをモック化する
        with open(FY_CSV_FILEPATH, "r") as f:
            text = f.read()
        mock_read_csv_as_text.return_value = text
        result = CompanyPerformanceDataFrame.read_fy_all_csv(FY_CSV_FILEPATH)
        # read_csv_as_textメソッドが呼び出されたことを確認する
        mock_read_csv_as_text.assert_called_once()
        # 正しくdataframeが呼び出されたことを確認する
        df = CompanyPerformanceDataFrame.from_csv(DF_CSV_FILEPATH)
        equal_flag = are_dataframes_equal(df, result)
        self.assertTrue(equal_flag)

    @patch("jhds.dataframe.get_irbank_url")
    @patch("jhds.dataframe.CompanyPerformanceDataFrame.read_csv_as_text")
    def test_download(self, mock_read_csv_as_text, mock_get_irbank_url):
        # テスト用のダミーデータを用意する
        dummy_df = CompanyPerformanceDataFrame.from_csv(DF_CSV_FILEPATH)
        # モックを使ってget_irbank_urlメソッドをモック化する
        mock_get_irbank_url.return_value = FY_CSV_FILEPATH
        # モックを使ってread_csv_as_textメソッドをモック化する
        with open(FY_CSV_FILEPATH, "r") as f:
            text = f.read()
        mock_read_csv_as_text.return_value = text
        # CompanyPerformanceDataFrameクラスのdownloadメソッドを呼び出す
        result = CompanyPerformanceDataFrame.download(
            TEST_CODE, access_restriction=False
        )
        # 正しいURLでget_irbank_urlメソッドが呼び出されたことを確認する
        mock_get_irbank_url.assert_called_once_with(TEST_CODE)
        # 返された結果がDataFrameであることを確認する
        self.assertIsInstance(result, CompanyPerformanceDataFrame)
        # 返されたDataFrameがダミーデータと同じかどうかを確認する
        equal_flag = are_dataframes_equal(dummy_df, result)
        self.assertTrue(equal_flag)

    @patch("jhds.utils.access_url")
    def test_read_csv_as_text(self, mock_access_url):
        # モックの設定
        csv_url = "dummy_url"
        dummy_csv_data = "dummy,csv,data\n1,2,3"
        mock_response = MagicMock()
        mock_response.content.decode.return_value = dummy_csv_data
        mock_access_url.return_value = mock_response

        # テスト対象のメソッドを呼び出す
        result = CompanyPerformanceDataFrame.read_csv_as_text(csv_url)

        # アサーション
        self.assertEqual(result, dummy_csv_data)
        mock_access_url.assert_called_once_with(csv_url)


class TestMarketDataFrame(unittest.TestCase):

    @patch("jhds.dataframe.get_jpx_market_excel_url")
    @patch("jhds.dataframe.MarketDataFrame.read_market_excel")
    def test_download(self, mock_read_market_excel, mock_get_jpx_market_excel_url):
        # モックの設定
        dummy_excel_url = "dummy_excel_url"
        mock_df = MarketDataFrame.from_csv(TEST_MARKET_CSV_FILEPATH)
        mock_read_market_excel.return_value = mock_df
        mock_get_jpx_market_excel_url.return_value = dummy_excel_url
        # テスト対象のメソッドを呼び出す
        result = MarketDataFrame.download()
        # アサーション
        self.assertIsInstance(result, MarketDataFrame)
        mock_get_jpx_market_excel_url.assert_called_once()
        mock_read_market_excel.assert_called_once_with(dummy_excel_url)

    def test_read_market_excel(self):
        df = MarketDataFrame.from_csv(TEST_MARKET_CSV_FILEPATH)
        result = MarketDataFrame.read_market_excel(TEST_MARKET_EXCEL_FILEPATH)
        equal_flag = are_dataframes_equal(df, result)
        self.assertTrue(equal_flag)


class TestMinkabuDataFrame(unittest.TestCase):

    @patch("jhds.minkabu.RankingHTML")
    def test__download(self, mock_ranking_html):
        # モックの設定
        ranking_type = minkabu.DIVIDEND_YIELD_TYPE
        columns = [COMPANY_CODE, COMPANY_NAME, STOCK_PRICE, DIVIDEND_YIELD]
        thres_column = DIVIDEND_YIELD
        thres = 1.0
        max_page = 2
        # lower = Trueのときのテスト
        lower = True
        mock_extracted_data = np.zeros((3, len(columns)))  # 仮の抽出データ
        mock_ranking_html.return_value.extract_data.return_value = mock_extracted_data
        # テスト対象のメソッドを呼び出す
        result = MinkabuDataFrame._download(
            ranking_type,
            columns,
            thres_column,
            thres,
            lower,
            max_page,
            access_restriction=False,
        )
        # アサーション
        expected_df = pd.DataFrame(mock_extracted_data, columns=columns)
        pd.testing.assert_frame_equal(result, expected_df)
        # mockの呼び出しを検証
        assert len(minkabu.RankingHTML.call_args_list) == 1

        # lower = Falseのときのテスト
        lower = False
        # テスト対象のメソッドを呼び出す
        result = MinkabuDataFrame._download(
            ranking_type,
            columns,
            thres_column,
            thres,
            lower,
            max_page,
            access_restriction=False,
        )
        # アサーション
        expected_data = np.concatenate([mock_extracted_data for i in range(max_page)])
        expected_df = pd.DataFrame(expected_data, columns=columns)
        pd.testing.assert_frame_equal(result, expected_df)
        # mockの呼び出しを検証
        assert len(minkabu.RankingHTML.call_args_list) == max_page + 1


if __name__ == "__main__":
    unittest.main()

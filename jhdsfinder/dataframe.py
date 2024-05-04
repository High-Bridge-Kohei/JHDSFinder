import os

import pandas as pd

pd.set_option("future.no_silent_downcasting", True)

from jhdsfinder.names import *


class DataFrame(pd.DataFrame):
    ENCODING = "utf-8"
    DTYPES = {}

    def __init__(self, data, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        # カラムの確認
        columns = self.columns.tolist()
        for column, dtype in self.DTYPES.items():
            assert column in columns, f"'{column}' is not in {columns}."
        self = self.astype(self.DTYPES)

    @classmethod
    def from_csv(cls, csv_path: str, index_col=0, header=0, encoding=ENCODING):
        assert os.path.exists(csv_path), f"There is no csv file. ({csv_path})"
        df = pd.read_csv(
            csv_path,
            index_col=index_col,
            header=header,
            encoding=encoding,
            dtype=cls.DTYPES,
        )
        return DataFrame(df)

    def to_csv(self, csv_path: str, encoding=ENCODING, *args, **kwargs) -> None:
        super().to_csv(csv_path, encoding=encoding, *args, **kwargs)


class FinanceAllDataFrame(DataFrame):
    DTYPES = {
        COMPANY_CODE: str,
        FISCAL_YEAR: float,  # "年度"
        REVENUE: float,  # "売上高"
        OPERATING_PROFIT: float,  # "営業利益"
        ORDINARY_PROFIT: float,  # "経常利益"
        NET_PROFIT: float,  # "純利益"
        EPS: float,  # "EPS"
        ROE: float,  # "ROE"
        ROA: float,  # "ROA"
        TOTAL_ASSETS: float,  # "総資産"
        NET_ASSETS: float,  # "純資産"
        SHAREHOLDER_EQUITY: float,  # "株主資本"
        RETAINED_EARNINGS: float,  # "利益剰余金"
        SHORT_TERM_DEBT: float,  # "短期借入金"
        LONG_TERM_DEBT: float,  # "長期借入金"
        BPS: float,  # "BPS"
        EQUITY_RATIO: float,  # "自己資本比率"
        OPERATING_CASH_FLOW: float,  # "営業CF"
        INVESTING_CASH_FLOW: float,  # "投資CF"
        FINANCING_CASH_FLOW: float,  # "財務CF"
        CAPITAL_EXPENDITURE: float,  # "設備投資"
        CASH_EQUIVALENTS: float,  # "現金同等物"
        OPERATING_CASH_FLOW_MARGIN: float,  # "営業CFマージン"
        DIVIDEND_PER_SHARE: float,  # "一株配当"
        SURPLUS_FUNDS_DIVIDENDS: float,  # "剰余金の配当"
        SHARE_BUYBACKS: float,  # "自社株買い"
        DIVIDEND_PAYOUT_RATIO: float,  # "配当性向"
        TOTAL_PAYOUT_RATIO: float,  # "総還元性向"
        NET_ASSETS_PAYOUT_RATIO: float,  # "純資産配当率"
    }

    def __init__(self, data: DataFrame) -> None:
        super().__init__(data)


class StockPriceDataFrame(DataFrame):
    """
    https://mujinzou.com/d_data/2024d/24_04d/T240425.zip
    """

    DTYPES = {
        DATE: str,
        COMPANY_CODE: str,
        MARKET_CODE: str,
        OPEN_PRICE: float,
        HIGH_PRICE: float,
        LOW_PRICE: float,
        CLOSE_PRICE: float,
        VOLUME: float,
        MARKET_CATEGORY: str,
    }

    def __init__(self, data, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        self[COMPANY_CODE] = self[COMPANY_CODE].astype(str)
        self.sort_values(by=COMPANY_CODE, inplace=False)


class CompanyPerformanceDataFrame(DataFrame):
    DTYPES = {
        COMPANY_CODE: str,
        DIVIDEND_YIELD: float,
        REVENUE_GRAD: float,
        EPS_GRAD: float,
        BPS_GRAD: float,
        DIVIDEND_PER_SHARE_GRAD: float,
        OPERATING_CASH_FLOW_GRAD: float,
        CASH_EQUIVALENTS_GRAD: float,
        OPERATING_CASH_FLOW_SURPLUS_EVERY_YEAR: float,
        OPERATING_PROFIT_MARGIN_AVG: float,
        EQUITY_RATIO_AVG: float,
        DIVIDEND_PAYOUT_RATIO_AVG: float,
        ROE_AVG: float,
        ROA_AVG: float,
        PER: float,
        PBR: float,
        # CURRENT_RATIO_AVG: float,
        # TOTAL_ASSETS_CASH_RATIO_AVG: float,
        # TOTAL_ASSETS_CASH_RATIO_GRAD: float,
        # CONTINUOUS_DIVIDEND_YEARS_AVG: float,
    }

    def __init__(self, data, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        self[COMPANY_CODE] = self[COMPANY_CODE].astype(str)
        self.sort_values(by=COMPANY_CODE, inplace=False)


class MarketDataFrame(DataFrame):
    DTYPES = {
        DATE: str,  # "日付"
        COMPANY_CODE: str,  # "コード"
        COMPANY_NAME: str,  # "銘柄名"
        MARKET_CATEGORY: str,  # "市場・商品区分"
        INDUSTRY_CODE_33: str,  # "33業種コード"
        INDUSTRY_CATEGORY_33: str,  # "33業種区分"
        INDUSTRY_CODE_17: str,  # "17業種コード"
        INDUSTRY_CATEGORY_17: str,  # "17業種区分"
        SCALE_CODE: str,  # "規模コード"
        SCALE_CATEGORY: str,  # "規模区分"
    }

    def __init__(self, data, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        self[COMPANY_CODE] = self[COMPANY_CODE].astype(str)
        self.sort_values(by=COMPANY_CODE, inplace=False)


class ScreenedCompanyDataFrame(DataFrame):
    DTYPES = {
        COMPANY_CODE: str,  # "コード"
        COMPANY_NAME: str,  # "銘柄名"
        DIVIDEND_YIELD: float,
        PER: float,
        PBR: float,
    }

    def __init__(self, data, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)


if __name__ == "__main__":
    pass
    # テスト
    # code = "1301"
    # csv_path = f"{code}.csv"
    # # df = CompanyPerformanceDataFrame.download(code, access_restriction=True)
    # # df.to_csv(csv_path)
    # df = CompanyPerformanceDataFrame.from_csv(csv_path)
    # print(df)

    # csv_path = "market.csv"
    # df = MarketDataFrame.download()
    # df.to_csv(csv_path)
    # df = MarketDataFrame.from_csv(csv_path)
    # print(df)

    # dy_csv_path = "dividend_yield.csv"
    # df = DividendYeildDataFrame.download(dy_thres=5.0)
    # df.to_csv(dy_csv_path)

    # pbr_csv_path = "pbr.csv"
    # df = PBRDataFrame.download(pbr_thres=0.01)
    # df.to_csv(pbr_csv_path)

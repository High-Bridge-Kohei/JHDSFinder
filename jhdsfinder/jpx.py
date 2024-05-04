import os

import pandas as pd

from jhdsfinder import utils
from jhdsfinder.names import *
from jhdsfinder.dataframe import MarketDataFrame

# 市場データのexcelファイルのURL
JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att"
MARKET_EXCEL_FILENAME = "data_j.xls"


def get_download_link() -> str:
    url = f"{JPX_URL}/{MARKET_EXCEL_FILENAME}"
    return url


def get_market_csv_filepath(data_dir=DATA_DIRNAME):
    csv_filepath = os.path.join(data_dir, MARKET_CSV_FILENAME)
    return csv_filepath


def download() -> MarketDataFrame:
    # 市場データのExcelにアクセス
    excel_url = get_download_link()
    try:
        df = pd.read_excel(excel_url, sheet_name="Sheet1")
    except Exception as e:
        print(f"Error occurred in progress of reading Market Execl ({excel_url}).")
        raise ValueError(e)
    return MarketDataFrame(df)


def load_market_dataframe(data_dir=DATA_DIRNAME, update_frequency_days=365):
    csv_filepath = get_market_csv_filepath(data_dir)
    update_flag = utils.get_update_flag(csv_filepath, update_frequency_days)
    if update_flag:
        df = download()
        df.to_csv(csv_filepath)
    else:
        df = MarketDataFrame.from_csv(csv_filepath)
    return df


if __name__ == "__main__":
    update_frequency_days = 1
    df = load_market_dataframe(update_frequency_days=update_frequency_days)
    print(df)

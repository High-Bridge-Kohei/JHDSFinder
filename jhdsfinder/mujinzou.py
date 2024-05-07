import os
import io
import datetime
import jpholiday
import zipfile

import pandas as pd

from jhdsfinder.names import *
from jhdsfinder import utils
from jhdsfinder.dataframe import *

MUJINZOU_URL = "https://www.mujinzou.com"


def is_holiday(date):
    if date.weekday() == 5 or date.weekday() == 6:  # 土曜日or日曜日の場合
        return True
    else:
        return jpholiday.is_holiday(date)


def get_recent_weekday(date):
    if not is_holiday(date):
        return date
    else:
        date = date - datetime.timedelta(days=1)
        return get_recent_weekday(date)


def get_stock_price_date():
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    recent_weekday = get_recent_weekday(yesterday)
    return recent_weekday


def get_download_link() -> str:
    """
    ダウンロード先リンクの例:
    - https://www.mujinzou.com/d_data/2024d/24_01d/T240125.zip
    - https://www.mujinzou.com/d_data/2024d/24_02d/T240221.zip
    - https://www.mujinzou.com/d_data/2024d/24_04d/T240425.zip
    """
    date = get_stock_price_date()
    y = str(date.year)
    m = str(date.month).zfill(2)
    d = str(date.day).zfill(2)
    url = f"{MUJINZOU_URL}/d_data/{y}d/{y[-2:]}_{m}d/T{y[-2:]}{m}{d}.zip"
    return url


def download() -> StockPriceDataFrame:
    url = get_download_link()
    filename = os.path.basename(url).split(".")[0] + ".csv"
    response = utils.access_url(url)
    # zipファイル内のcsvファイルを直接読み込む
    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_ref:
        with zip_ref.open(filename) as f:
            df = pd.read_csv(f, encoding="shift_jis")
    df = StockPriceDataFrame(df.values, columns=STOCK_PRICE_COLUMNS)
    df[COMPANY_CODE] = df[COMPANY_CODE].astype(str)
    return df


def get_stock_price_csv_filepath(data_dir=DATA_DIRNAME):
    csv_filepath = os.path.join(data_dir, STOCK_PRICE_CSV_FILENAME)
    return csv_filepath


def load_stock_price_dataframe(update_frequency_days=1):
    csv_filepath = get_stock_price_csv_filepath()
    update_flag = utils.get_update_flag(csv_filepath, update_frequency_days)
    if update_flag:
        df = download()
        df.to_csv(csv_filepath)
    else:
        df = StockPriceDataFrame.from_csv(csv_filepath)
    return df


if __name__ == "__main__":
    df = load_stock_price_dataframe()
    print(df)

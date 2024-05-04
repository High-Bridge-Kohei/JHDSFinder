import os
import time
import datetime
from glob import glob
import pandas as pd
import numpy as np

from jhdsfinder import utils
from jhdsfinder.dataframe import *
from jhdsfinder.names import *

IRBANK_URL = "https://f.irbank.net/files"
MIN_FISCAL_YEAR = 2010


def get_download_link(fiscal_year: int, csv_filename: str) -> str:
    assert csv_filename in FY_CSV_FILENAMES
    assert fiscal_year >= MIN_FISCAL_YEAR
    url = f"{IRBANK_URL}/00{str(fiscal_year)[-2:]}/{csv_filename}"
    return url


def get_fy_csv_filepath(fiscal_year: int, csv_filename: str):
    assert csv_filename in FY_CSV_FILENAMES
    assert fiscal_year >= MIN_FISCAL_YEAR
    dirname = csv_filename.split(".")[0]
    save_dir = os.path.join(DATA_DIRNAME, dirname)
    csv_filepath = os.path.join(save_dir, f"{str(fiscal_year)}.csv")
    return csv_filepath


def get_fy_all_csv_filepath(data_dir=DATA_DIRNAME):
    csv_filepath = os.path.join(data_dir, FY_ALL_CSV_FILENAME)
    return csv_filepath


def download_fy_csv_file(
    fiscal_year: int, csv_filename: str, access_restricstion: bool = True
):
    # 保存先の設定
    csv_filepath = get_fy_csv_filepath(fiscal_year, csv_filename)
    if os.path.exists(csv_filepath):
        print(f"Skip downloading since the file already exists. ({csv_filepath})")
    else:
        # csvファイルのダウンロード
        url = get_download_link(fiscal_year, csv_filename)
        response = utils.access_url(url)
        print(f"Downloading {fiscal_year} year {csv_filename} ...")
        with open(csv_filepath, "wb") as f:
            f.write(response.content)
        if access_restricstion:
            time.sleep(3600 / 50)


def download(fiscal_year: int):
    for csv_filename in FY_CSV_FILENAMES:
        download_fy_csv_file(fiscal_year, csv_filename)


def merge_csv_by_year(fiscal_year: int, data_dir=DATA_DIRNAME) -> DataFrame:
    df_list = []
    for csv_filename in FY_CSV_FILENAMES:
        dirname = csv_filename.split(".")[0]
        csv_filepath = os.path.join(data_dir, dirname, f"{fiscal_year}.csv")
        df = DataFrame.from_csv(csv_filepath, index_col=None, header=1).astype(str)
        # 銘柄コードをインデックスにする
        df = df.set_index(COMPANY_CODE)
        # 年度を更新する
        df[FISCAL_YEAR] = fiscal_year
        df = df.sort_values(by=[COMPANY_CODE])
        df_list.append(df)
    df = pd.concat(df_list, axis=1)
    # 重複するカラム (年度) を削除する
    df = df.loc[:, ~df.columns.duplicated()]
    df.reset_index(inplace=True)
    return df


def merge_csv() -> FinanceAllDataFrame:
    df_list = []
    fiscal_years = get_csv_fiscal_years()
    for fiscal_year in fiscal_years:
        df = merge_csv_by_year(fiscal_year)
        df_list.append(df)
    assert len(df_list) == len(fiscal_years), len(df_list)
    df = pd.concat(df_list, axis=0)
    df = df.sort_values(by=[COMPANY_CODE, FISCAL_YEAR])
    df.reset_index(inplace=True, drop=True)
    # '-'と''をNaNに置き換える
    df = df.astype(object).replace("-", np.nan).replace("", np.nan)
    # 1株配当を修正
    df[DIVIDEND_PER_SHARE] = df[DIVIDEND_PER_SHARE].astype(float).fillna(0)
    # 営業利益率を追加
    revenue = df[REVENUE].astype(float).values
    operating_profit = df[OPERATING_PROFIT].astype(float).values
    df[OPERATING_PROFIT_MARGIN] = operating_profit / (revenue + 1e-8) * 100
    # 銘柄コードで並び替え
    df.sort_values(by=COMPANY_CODE, inplace=False)
    return FinanceAllDataFrame(df)


def update(data_dir=DATA_DIRNAME):
    current_year = datetime.datetime.now().year
    years = np.arange(MIN_FISCAL_YEAR, current_year)
    for year in years:
        download(year)
    df = merge_csv()
    # 保存
    csv_filepath = get_fy_all_csv_filepath(data_dir)
    df.to_csv(csv_filepath)


def get_csv_fiscal_years(data_dir=DATA_DIRNAME) -> list:
    dirname = FY_BALANCE_SHEET_CSV_FILENAME.split(".")[0]
    csv_filenames = sorted(glob(os.path.join(data_dir, dirname, "20*.csv")))
    if len(csv_filenames) == 0:
        fiscal_years = [MIN_FISCAL_YEAR]
    else:
        fiscal_years = [int(os.path.basename(f).split(".")[0]) for f in csv_filenames]
    return fiscal_years


def load_fy_all_dataframe(
    force_update: bool = False, data_dir=DATA_DIRNAME
) -> CompanyPerformanceDataFrame:
    # dataframeのアップデートを行うかを判定する
    csv_filepath = get_fy_all_csv_filepath(data_dir)
    if not os.path.exists(csv_filepath):
        force_update = True
    csv_latest_year = get_csv_fiscal_years(data_dir)[-1]
    current_year = datetime.datetime.now().year
    if current_year - csv_latest_year > 1 or force_update:
        print("Update csv files ...")
        update(data_dir)
    else:
        print("IR Bank data is the latest status. (OK)")
    df = CompanyPerformanceDataFrame.from_csv(csv_filepath)
    return df


if __name__ == "__main__":
    force_update = 1
    df = load_fy_all_dataframe(force_update)
    code = "1301"
    _df = df[df[COMPANY_CODE] == code]
    print(_df)

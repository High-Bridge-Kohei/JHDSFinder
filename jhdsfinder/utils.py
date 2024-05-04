import os
import io
import time
from datetime import datetime, timedelta

from tqdm import tqdm
import numpy as np
import pandas as pd
import requests


def access_url(url: str) -> requests.Response:
    response = requests.get(url)
    if response.status_code == 200:
        pass
    elif response.status_code == 404:
        print(f"StatuCode={response.status_code}: Not Found. ({url})")
    else:
        # ステータスコードが200以外の場合はエラーを出す
        e = f"StatuCode={response.status_code}: {response.text}"
        raise RuntimeError(e)
    return response


def get_file_datetime(filepath) -> datetime:
    # ファイルの最終更新日時を取得
    file_modified_time = os.path.getmtime(filepath)
    file_modified_datetime = datetime.fromtimestamp(file_modified_time)
    return file_modified_datetime


def get_update_flag(filepath: str, update_frequency_days: int = 1) -> bool:
    update = False
    if not os.path.exists(filepath):
        update = True
    else:
        # ファイルの更新日時を取得
        file_modified_datetime = get_file_datetime(filepath)
        # 更新期間を計算
        thres = datetime.now() - timedelta(days=update_frequency_days)
        if file_modified_datetime < thres:
            # 更新期間を過ぎた古いファイルならアップデート
            update = True
    return update

import pandas as pd


def are_dataframes_equal(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    2つのデータフレームが同じかどうかを確認する関数。

    Parameters:
    - df1: DataFrame
    - df2: DataFrame

    Returns:
    - 同じ場合はTrue、異なる場合はFalse
    """
    df1 = pd.DataFrame(df1)
    df2 = pd.DataFrame(df2)
    # 型違いによる差分が生まれないようにする
    df1 = df1.astype(str)
    df2 = df2.astype(str)
    # 形状が異なる場合は異なると判定
    if df1.shape != df2.shape:
        print(f"df1.shape = {df1.shape}, but df2.shape = {df2.shape}")
        return False

    # 列名が異なる場合は異なると判定
    if list(df1.columns) != list(df2.columns):
        print(
            f"df1.columns = {list(df1.columns)}, but df2.columns = {list(df2.columns)}"
        )
        return False

    # 各要素が一致するか確認
    if df1.equals(df2):
        return True
    else:
        diff_df = df1.compare(df2)
        print("Belows are diffrent.")
        print(diff_df)
        return False

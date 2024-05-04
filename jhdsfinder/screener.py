from typing import List
import numpy as np

from jhdsfinder.names import *
from jhdsfinder.dataframe import CompanyPerformanceDataFrame

CATEGORICAL_COLUMNS = [INDUSTRY_CATEGORY_33, SCALE_CATEGORY]
NUMERICAL_COLUMNS = [
    DIVIDEND_YIELD,
    DIVIDEND_INCREASE_CONTINUOUS,
    REVENUE_GRAD,
    EPS_GRAD,
    BPS_GRAD,
    DIVIDEND_PER_SHARE_GRAD,
    OPERATING_CASH_FLOW_GRAD,
    CASH_EQUIVALENTS_GRAD,
    OPERATING_CASH_FLOW_SURPLUS_EVERY_YEAR,
    OPERATING_PROFIT_MARGIN_AVG,
    EQUITY_RATIO_AVG,
    CURRENT_RATIO_AVG,
    DIVIDEND_PAYOUT_RATIO_AVG,
    ROE_AVG,
    ROA_AVG,
    PER,
    PBR,
    # TOTAL_ASSETS_CASH_RATIO_GRAD,
    # CONTINUOUS_DIVIDEND_YEARS_AVG,
    # TOTAL_ASSETS_CASH_RATIO_AVG,
]


class Condition:
    def __init__(self, column: str):
        self.column = column
        self.screen_flag = False


class CategoricalCondition(Condition):
    def __init__(self, column: str, category_list: list = None) -> None:
        super().__init__(column)
        assert column in CATEGORICAL_COLUMNS, column
        if category_list is not None:
            assert isinstance(category_list, list)
        else:
            self.screen_flag = True
        self.category_list = category_list

    def __str__(self) -> str:
        text = f"column: {self.column}\ncategories: {self.category_list}\n"
        return text


class NumericalCondition(Condition):
    def __init__(self, column: str, vmin: float = None, vmax: float = None) -> None:
        super().__init__(column)
        assert column in NUMERICAL_COLUMNS, column
        if vmin is not None:
            assert isinstance(vmin, int) or isinstance(vmin, float)
        if vmax is not None:
            assert isinstance(vmax, int) or isinstance(vmax, float)
        self.screen_flag = (vmin is not None) and (vmax is not None)
        self.vmin = vmin
        self.vmax = vmax

    def __str__(self):
        text = f"column: {self.column}\nvmin: {self.vmin}\nvmax: {self.vmax}\n"
        return text


class Conditions:
    def __init__(self, data: List[Condition]) -> None:
        self.data = data
        self.index = 0

    @classmethod
    def from_dict(cls, dictionay: dict):
        data = []
        # for column, (vmin, vmax) in dictionay.items():
        for column, values in dictionay.items():
            print(column, values)
            if values is None or isinstance(values, list):
                category_list = values
                data.append(CategoricalCondition(column, category_list))
            else:
                vmin, vmax = values
                data.append(NumericalCondition(column, vmin, vmax))
        return Conditions(data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.data):
            value = self.data[self.index]
            self.index += 1
            return value
        else:
            raise StopIteration

    def add(self, condition: Condition):
        self.data += [condition]

    def cat(self, conditions):
        data = self.data + conditions.data
        return Conditions(data)


class CompanyScreener:
    def __init__(self, df: CompanyPerformanceDataFrame):
        self.df = df

    def run(self, conditions: Conditions) -> np.ndarray:
        new_df = self.df.copy()
        for condition in conditions:
            new_df = self._screen(new_df, condition)
        company_codes = new_df[COMPANY_CODE].values
        return company_codes

    def _screen(self, df: CompanyPerformanceDataFrame, condition: Condition):
        if condition.screen_flag:
            pass
        elif isinstance(condition, NumericalCondition):
            df = self._screen_numerical_category(df, condition)
        elif isinstance(condition, CategoricalCondition):
            df = self._screen_categorical_category(df, condition)
        else:
            raise ValueError(condition.column)
        return df

    def _screen_numerical_category(
        self, df: CompanyPerformanceDataFrame, condition: NumericalCondition
    ):
        column = condition.column
        vmin = condition.vmin
        vmax = condition.vmax
        if vmin is not None:
            df = df[df[column] >= vmin]
        if vmax is not None:
            df = df[df[column] <= vmax]
        return df

    def _screen_categorical_category(
        self, df: CompanyPerformanceDataFrame, condition: CategoricalCondition
    ):
        column = condition.column
        category_list = condition.category_list
        df = df[df[column].isin(category_list)]
        return df


def get_default_coditions() -> Conditions:
    # TODO
    dictionary = {
        DIVIDEND_YIELD: (3.75, None),  # 配当利回り
        REVENUE_GRAD: (0.0, None),  # 売上の勾配
        EPS_GRAD: (0.0, None),  # EPSの勾配
        BPS_GRAD: (0.0, None),  # BPSの勾配
        DIVIDEND_PER_SHARE_GRAD: (0.0, None),  # 1株配当の勾配
        OPERATING_CASH_FLOW_SURPLUS_EVERY_YEAR: (None, None),
        OPERATING_PROFIT_MARGIN_AVG: (10.0, None),  # 営業利益率の平均値
        EQUITY_RATIO_AVG: (50.0, None),  # 自己資本比率
        DIVIDEND_PAYOUT_RATIO_AVG: (None, None),  # 配当性向の平均値
        ROE_AVG: (None, None),
        ROA_AVG: (None, None),
        PER: (None, 15.0),
        PBR: (None, 2.0),
        # TOTAL_ASSETS_CASH_RATIO_GRAD: (0.0, None),  # 総資産現金率の勾配
        # CONTINUOUS_DIVIDEND_YEARS_AVG: (5.0, None),  # 配当継続年数の平均値
        # CURRENT_RATIO_AVG: (None, None),  # 総資産現金率の平均値
        # TOTAL_ASSETS_CASH_RATIO_AVG: (200.0, None),  # 流動比率の平均値
    }
    return Conditions.from_dict(dictionary)

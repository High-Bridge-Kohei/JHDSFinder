import os
from typing import List, Tuple

from tqdm import tqdm
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from jhdsfinder.names import *
from jhdsfinder import utils
from jhdsfinder.dataframe import *
from jhdsfinder.jpx import load_market_dataframe
from jhdsfinder.irbank import load_fy_all_dataframe, get_fy_all_csv_filepath
from jhdsfinder.mujinzou import load_stock_price_dataframe, get_stock_price_csv_filepath


def get_gradient(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) == 0 or len(y) == 0:
        return np.nan
    reg = LinearRegression().fit(x.reshape(-1, 1), y)
    gradient = reg.coef_.item()
    assert isinstance(gradient, float), gradient
    return gradient


def get_average(x: np.ndarray, calc_years: int) -> float:
    if len(x) == 0:
        return np.nan
    elif calc_years == -1 or len(x) < calc_years:
        return np.average(x)
    else:
        return np.average(x[-calc_years:])


def remove_outliers_mad(years: np.ndarray, x: np.ndarray, thresh=3.5):
    """
    https://www.ibm.com/docs/ja/cognos-analytics/11.1.0?topic=terms-modified-z-score
    """
    nan_bool = np.isnan(x)
    years = years[~nan_bool]
    x = x[~nan_bool]
    if len(x) < 3:
        return years, x
    median = np.median(x)
    absolute_deviation = np.abs(x - median)
    median_ad = np.median(absolute_deviation)
    if median_ad == 0.0:
        mean_ad = np.mean(absolute_deviation)
        modified_z_score = (x - median) / (1.253314 * mean_ad + 1e-8)
    else:
        modified_z_score = (x - median) / (1.486 * median_ad)

    bool_array = np.abs(modified_z_score) < thresh
    years = years[bool_array]
    x = x[bool_array]
    return years, x


class CompanyData:
    def __init__(
        self,
        company_code: str,
        company_name: str,
        market_category: str,
        industry_code_33: str,
        industry_category_33: str,
        industry_code_17: str,
        industry_category_17: str,
        scale_code: str,
        scale_category: str,
        stock_price: float,
        df: DataFrame,
    ) -> None:
        self.company_code = company_code
        self.company_name = company_name
        self.market_category = market_category
        self.industry_code_33 = industry_code_33
        self.industry_category_33 = industry_category_33
        self.industry_code_17 = industry_code_17
        self.industry_category_17 = industry_category_17
        self.scale_code = scale_code
        self.scale_category = scale_category
        self.company_code = company_code
        self.stock_price = stock_price
        self.df = df
        self.columns = self.df.columns.values.tolist()
        self.year = self.df[FISCAL_YEAR].values[-1]

    def __str__(self):
        dy = "{:.3g}".format(self.get_dividend_yield())
        text = f"[{self.company_code}] " + "-" * 30 + "\n"
        text += f" {COMPANY_NAME}: {self.company_name}\n"
        text += f" {STOCK_PRICE}: {self.stock_price} 円\n"
        text += f" {DIVIDEND_YIELD}: {dy} %\n"
        text += f" {MARKET_CATEGORY}: {self.market_category}\n"
        text += f" {INDUSTRY_CATEGORY_33}: {self.industry_category_33}\n"
        text += f" {SCALE_CATEGORY}: {self.scale_category}\n"
        text += "-" * 37
        return text

    def get_dividend_yield(self) -> float:
        years, dividends = self.get_dividend_per_share()
        if len(dividends) == 0 or self.stock_price == 0.0:
            return np.nan
        else:
            dividend_yield = dividends[-1] / self.stock_price * 100
            return dividend_yield

    def get_PBR(self):
        years, bps = self.get_BPS()
        if len(bps) == 0 or self.stock_price == 0.0:
            return np.nan
        else:
            pbr = self.stock_price / bps[-1]
            return pbr

    def get_PER(self):
        years, eps = self.get_EPS()
        if len(eps) == 0 or self.stock_price == 0.0:
            return np.nan
        else:
            per = self.stock_price / eps[-1]
            return per

    def get_values(self, column: list) -> Tuple[np.ndarray, np.ndarray]:
        assert column in self.columns, column
        _df = self.df.loc[:, [FISCAL_YEAR, column]].astype(float).dropna()
        years = _df[FISCAL_YEAR].values.astype(int)
        values = _df[column].values.astype(float)
        years, values = remove_outliers_mad(years, values)
        assert_text = f"len(years)={len(years)}, len(values)={len(values)}"
        assert len(years) == len(values), assert_text
        return years, values

    def get_revenues(self):
        return self.get_values(REVENUE)

    def get_operating_profit(self):
        return self.get_values(OPERATING_PROFIT)

    def get_operating_profit_margin(self) -> Tuple[np.ndarray, np.ndarray]:
        """営業利益率"""
        # columns = [FISCAL_YEAR, OPERATING_PROFIT, REVENUE]
        # _df = self.df.loc[:, columns].astype(float).dropna()
        # years = _df[FISCAL_YEAR].values.astype(int)
        # operating_profit = _df[OPERATING_PROFIT].values
        # revenue = _df[REVENUE].values
        # operating_profit_margin = operating_profit / (revenue + 1e-8) * 100
        # years, operating_profit_margin = remove_outliers_mad(
        #     years, operating_profit_margin
        # )
        # return years, operating_profit_margin
        return self.get_values(OPERATING_PROFIT_MARGIN)

    def get_ordinary_profit(self):
        return self.get_values(ORDINARY_PROFIT)

    def get_net_profit(self):
        return self.get_values(NET_PROFIT)

    def get_EPS(self):
        return self.get_values(EPS)

    def get_ROE(self):
        return self.get_values(ROE)

    def get_ROA(self):
        return self.get_values(ROA)

    def get_total_assets(self):
        return self.get_values(TOTAL_ASSETS)

    def get_net_assets(self):
        return self.get_values(NET_ASSETS)

    def get_shareholder_equity(self):
        return self.get_values(SHAREHOLDER_EQUITY)

    def get_retained_earnings(self):
        return self.get_values(RETAINED_EARNINGS)

    def get_short_term_debt(self):
        return self.get_values(SHORT_TERM_DEBT)

    def get_long_term_debt(self):
        return self.get_values(LONG_TERM_DEBT)

    def get_BPS(self):
        return self.get_values(BPS)

    def get_equity_ratio(self):
        return self.get_values(EQUITY_RATIO)

    def get_operating_cash_flow(self):
        return self.get_values(OPERATING_CASH_FLOW)

    def get_investing_cash_flow(self):
        return self.get_values(INVESTING_CASH_FLOW)

    def get_financing_cash_flow(self):
        return self.get_values(FINANCING_CASH_FLOW)

    def get_capital_expediture(self):
        return self.get_values(CAPITAL_EXPENDITURE)

    def get_cash_equivalents(self):
        return self.get_values(CASH_EQUIVALENTS)

    def get_operating_cash_flow_margin(self):
        return self.get_values(OPERATING_CASH_FLOW_MARGIN)

    def get_dividend_per_share(self):
        return self.get_values(DIVIDEND_PER_SHARE)

    def get_surplus_funds_dividends(self):
        return self.get_values(SURPLUS_FUNDS_DIVIDENDS)

    def get_share_buybacks(self):
        return self.get_values(SHARE_BUYBACKS)

    def get_dividend_payout_ratio(self):
        return self.get_values(DIVIDEND_PAYOUT_RATIO)

    def get_total_payout_ratio(self):
        return self.get_values(TOTAL_PAYOUT_RATIO)

    def get_net_assets_payout_ratio(self):
        return self.get_values(NET_ASSETS_PAYOUT_RATIO)

    def get_continuous_dividend_years(self):
        """配当継続年数"""
        columns = [
            FISCAL_YEAR,
            NET_ASSETS,  # 純資産
            RETAINED_EARNINGS,  # 利益剰余金
            NET_ASSETS_PAYOUT_RATIO,  # 純資産配当率
        ]
        _df = self.df.loc[:, columns].astype(float).dropna()
        years = _df[FISCAL_YEAR].values.astype(int)
        net_accets = _df[NET_ASSETS].values
        retained_earnings = _df[RETAINED_EARNINGS].values
        net_accets_payout_ratio = _df[NET_ASSETS_PAYOUT_RATIO].values
        total_dividends = net_accets * net_accets_payout_ratio / 100
        continuous_dividen_years = retained_earnings / (total_dividends + 1e-8)
        years, continuous_dividen_years = remove_outliers_mad(
            years, continuous_dividen_years
        )
        return years, continuous_dividen_years

    def get_current_ratio(self):
        """
        流動比率の概算 (現金等/短期借入金*100)
        """
        columns = [
            FISCAL_YEAR,
            SHORT_TERM_DEBT,  # 短期借入金
            CASH_EQUIVALENTS,  # 現金同等物
        ]
        _df = self.df.loc[:, columns].astype(float).dropna()
        years = _df[FISCAL_YEAR].values.astype(int)
        shor_term_debt = _df[SHORT_TERM_DEBT].values
        cash_equivalents = _df[CASH_EQUIVALENTS].values
        current_ratio = cash_equivalents / (shor_term_debt + 1e-8) * 100
        years, current_ratio = remove_outliers_mad(years, current_ratio)
        return years, current_ratio

    def get_total_assets_cash_ratio(self):
        """総資産現金率"""
        columns = [
            FISCAL_YEAR,
            TOTAL_ASSETS,  # 総資産
            CASH_EQUIVALENTS,  # 現金同等物
        ]
        _df = self.df.loc[:, columns].astype(float).dropna()
        years = _df[FISCAL_YEAR].values.astype(int)
        total_assets = _df[TOTAL_ASSETS].values
        cash_equivalents = _df[CASH_EQUIVALENTS].values
        cash_ratio = cash_equivalents / (total_assets + 1e-8) * 100
        years, cash_ratio = remove_outliers_mad(years, cash_ratio)
        return years, cash_ratio

    def is_dividend_increase_continuous(self) -> bool:
        years, divs = self.get_dividend_per_share()
        if len(divs > 0) == 0:
            return False
        else:
            return all(divs[i] <= divs[i + 1] for i in range(len(divs) - 1))

    def get_long_term_performance(self, calc_years: int = 3) -> pd.Series:
        # 配当利回り
        dividend_yield = self.get_dividend_yield()
        # 連続増配
        dividend_increase_continuous = self.is_dividend_increase_continuous()
        # 上昇傾向のトレンド
        ## 売上
        years, revenues = self.get_revenues()
        revenue_grad = get_gradient(years, revenues)
        ## EPS
        years, eps = self.get_EPS()
        eps_grad = get_gradient(years, eps)
        ## BPS
        years, bps = self.get_BPS()
        bps_grad = get_gradient(years, bps)
        ## 1株配当
        years, dividend_per_share = self.get_dividend_per_share()
        dividend_per_share_grad = get_gradient(years, dividend_per_share)
        ## 営業CF
        years, operating_cash_flows = self.get_operating_cash_flow()
        operating_cash_flows_grad = get_gradient(years, operating_cash_flows)
        ## 現金
        years, cash_equivalents = self.get_cash_equivalents()
        cash_equivalents_grad = get_gradient(years, cash_equivalents)

        # 中長期の平均業績
        ## 営業CF
        operating_cash_flows_surplus = all(operating_cash_flows >= 0.0)
        ## 営業利益率
        years, operating_profit_margin = self.get_operating_profit_margin()
        operating_profit_margin_avg = get_average(operating_profit_margin, calc_years)
        ## 自己資本率
        years, equity_ratio = self.get_equity_ratio()
        equity_ratio_avg = get_average(equity_ratio, calc_years)
        ## 流動比率
        years, current_ratio = self.get_current_ratio()
        current_ratio_avg = get_average(current_ratio, calc_years)
        ## 配当性向
        years, dividend_payout_ratio = self.get_dividend_payout_ratio()
        dividend_payout_ratio_avg = get_average(dividend_payout_ratio, calc_years)
        ## ROE
        years, roes = self.get_ROE()
        roe_avg = get_average(roes, calc_years)
        ## ROA
        years, roas = self.get_ROA()
        roa_avg = get_average(roas, calc_years)
        # PER
        per = self.get_PER()
        # PBR
        pbr = self.get_PBR()

        # ## 総資産現金率
        # years, total_assets_cash_ratio = self.get_total_assets_cash_ratio()
        # total_assets_cash_ratio_grad = get_gradient(years, total_assets_cash_ratio)
        # ## 配当継続年数
        # years, continuous_dividend_years = self.get_continuous_dividend_years()
        # continuous_dividend_years_avg = get_average(
        #     continuous_dividend_years, calc_years
        # )
        # ## 総資産現金率
        # total_assets_cash_ratio_avg = get_average(total_assets_cash_ratio, calc_years)

        # pd.Seriesにまとめる
        data = {
            COMPANY_CODE: self.company_code,
            DIVIDEND_YIELD: dividend_yield,
            DIVIDEND_INCREASE_CONTINUOUS: dividend_increase_continuous,
            REVENUE_GRAD: revenue_grad,
            EPS_GRAD: eps_grad,
            BPS_GRAD: bps_grad,
            DIVIDEND_PER_SHARE_GRAD: dividend_per_share_grad,
            OPERATING_CASH_FLOW_GRAD: operating_cash_flows_grad,
            CASH_EQUIVALENTS_GRAD: cash_equivalents_grad,
            OPERATING_CASH_FLOW_SURPLUS_EVERY_YEAR: operating_cash_flows_surplus,
            OPERATING_PROFIT_MARGIN_AVG: operating_profit_margin_avg,
            EQUITY_RATIO_AVG: equity_ratio_avg,
            CURRENT_RATIO_AVG: current_ratio_avg,
            DIVIDEND_PAYOUT_RATIO_AVG: dividend_payout_ratio_avg,
            ROE_AVG: roe_avg,
            ROA_AVG: roa_avg,
            PER: per,
            PBR: pbr,
            INDUSTRY_CATEGORY_33: self.industry_category_33,
            SCALE_CATEGORY: self.scale_category,
            # TOTAL_ASSETS_CASH_RATIO_GRAD: total_assets_cash_ratio_grad,
            # CONTINUOUS_DIVIDEND_YEARS_AVG: continuous_dividend_years_avg,
            # TOTAL_ASSETS_CASH_RATIO_AVG: total_assets_cash_ratio_avg,
        }
        return pd.Series(data)

    def get_latest_year(self) -> int:
        return self.year


class FinanceData:

    def __init__(self):
        # データフレームの読み込み
        market_df = load_market_dataframe()
        fy_all_df = load_fy_all_dataframe()
        stock_price_df = load_stock_price_dataframe()
        # 共通の銘柄コードのみを抽出
        self.company_codes = np.intersect1d(
            np.intersect1d(
                market_df[COMPANY_CODE].values.astype(str),
                fy_all_df[COMPANY_CODE].values.astype(str),
            ),
            stock_price_df[COMPANY_CODE].values.astype(str),
        ).tolist()
        self.market_df = market_df[market_df[COMPANY_CODE].isin(self.company_codes)]
        self.fy_all_df = fy_all_df[fy_all_df[COMPANY_CODE].isin(self.company_codes)]
        self.stock_price_df = stock_price_df[
            stock_price_df[COMPANY_CODE].isin(self.company_codes)
        ]
        self.performance_df = self.load_company_performance_dataframe()

    def get_company_data(self, company_code: str, debug=False) -> CompanyData:
        assert company_code in self.company_codes, company_code
        idx = self.market_df[self.market_df[COMPANY_CODE] == company_code].index.item()
        company_name = self.market_df.loc[idx, COMPANY_NAME]
        market_category = self.market_df.loc[idx, MARKET_CATEGORY]
        industry_code_33 = self.market_df.loc[idx, INDUSTRY_CODE_33]
        industry_category_33 = self.market_df.loc[idx, INDUSTRY_CATEGORY_33]
        industry_code_17 = self.market_df.loc[idx, INDUSTRY_CODE_17]
        industry_category_17 = self.market_df.loc[idx, INDUSTRY_CATEGORY_17]
        scale_code = self.market_df.loc[idx, SCALE_CODE]
        scale_category = self.market_df.loc[idx, SCALE_CATEGORY]
        stock_price = self.stock_price_df[
            self.stock_price_df[COMPANY_CODE] == company_code
        ][CLOSE_PRICE].item()
        df = self.fy_all_df[self.fy_all_df[COMPANY_CODE] == company_code]
        try:
            company_data = CompanyData(
                company_code,
                company_name,
                market_category,
                industry_code_33,
                industry_category_33,
                industry_code_17,
                industry_category_17,
                scale_code,
                scale_category,
                stock_price,
                df,
            )
            return company_data
        except Exception as e:
            if debug:
                print(e)
            return None

    def get_company_codes(self) -> list:
        return self.company_codes

    def get_company_names(self) -> list:
        return self.market_df[COMPANY_NAME].values.tolist()

    def make_company_pefomance_dataframe(
        self, calc_years: int = 3
    ) -> CompanyPerformanceDataFrame:
        data = []
        print("Making ComapanyPerformancesDataFrame ...")
        for company_code in tqdm(self.company_codes):
            company_data = self.get_company_data(company_code)
            company_performance = company_data.get_long_term_performance(calc_years)
            data.append(company_performance.values[None])
        data = np.concatenate(data, axis=0)
        columns = company_performance.index.tolist()
        df = pd.DataFrame(data, columns=columns)
        return CompanyPerformanceDataFrame(df)

    def load_company_performance_dataframe(self, calc_years=3, force_update=False):
        self.performance_csv_path = os.path.join(DATA_DIRNAME, PERFORMANCE_CSV_FILENAME)
        update_flag = utils.get_update_flag(
            self.performance_csv_path, update_frequency_days=1
        )
        if update_flag or force_update:
            performance_df = self.make_company_pefomance_dataframe(calc_years)
            performance_df.to_csv(self.performance_csv_path)
        else:
            performance_df = CompanyPerformanceDataFrame.from_csv(
                self.performance_csv_path
            )
        return performance_df

    def make_screened_company_dataframe(self):
        df = self.market_df.loc[:, [COMPANY_CODE, COMPANY_NAME]]
        # _dict = {
        #     TOPIX_CORE30: LEARGE_SCALE_CATEGORY,
        #     TOPIX_LARGE70: LEARGE_SCALE_CATEGORY,
        #     TOPIX_MID400: MIDDLE_SCALE_CATEGORY,
        #     TOPIX_SMALL1: SMALL_SCALE_CATEGORY,
        #     TOPIX_SMALL2: SMALL_SCALE_CATEGORY,
        #     OTHER: OTHER_SCALE_CATEGORY,
        # }
        # df[SCALE_CATEGORY] = df[SCALE_CATEGORY].replace(_dict)
        for col in [DIVIDEND_YIELD, PER, PBR]:
            df[col] = self.performance_df[col].values
            df[col] = df[col].astype(float).round(2)
        df = df.loc[
            :,
            [
                COMPANY_CODE,
                COMPANY_NAME,
                DIVIDEND_YIELD,
                PER,
                PBR,
            ],
        ]
        return df

    def get_market_dataframe(self):
        return self.market_df

    def get_finance_all_dataframe(self):
        return self.fy_all_df

    def get_stock_price_dataframe(self):
        return self.stock_price_df

    def get_company_performance_dataframe(self):
        return self.performance_df


if __name__ == "__main__":
    code = "2914"  # JT
    fy_data = FinanceData()
    company_data = fy_data.get_company_data(code, True)
    print(company_data)

    df = fy_data.make_company_pefomance_dataframe()
    print(df)

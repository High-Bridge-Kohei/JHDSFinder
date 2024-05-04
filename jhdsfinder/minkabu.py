import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from jhdsfinder.names import *
from jhdsfinder import utils

MINKABU_HOME_URL = "https://minkabu.jp"
MINKABU_STOCK_URL = f"{MINKABU_HOME_URL}/stock"
MINKABU_RANKING_URL = f"{MINKABU_HOME_URL}/financial_item_ranking"
ASC_ORDER = "asc"
DESC_ORDER = "desc"
DIVIDEND_YIELD_TYPE = "dividend_yield"
PBR_TYPE = "pbr"
RANKING_TYPES = [DIVIDEND_YIELD_TYPE, PBR_TYPE]


class MinkabuHTML:
    extract_method_dict = {}

    def __init__(self, url: str) -> None:
        self.response = utils.access_url(url)
        self.soup = BeautifulSoup(self.response.text, "lxml")


class RankingHTML(MinkabuHTML):
    def __init__(self, ranking_type: str, page: int, order: str = ASC_ORDER) -> None:
        assert order in [ASC_ORDER, DESC_ORDER]
        assert ranking_type in RANKING_TYPES
        assert page > 0 and isinstance(page, int)
        url = f"{MINKABU_RANKING_URL}/{ranking_type}?order={order}&page={str(page)}"
        super().__init__(url)

        self.extract_method_dict = {
            COMPANY_CODE: self.extract_company_codes,
            COMPANY_NAME: self.extract_company_names,
            STOCK_PRICE: self.extract_stock_prices,
            DIVIDEND_YIELD: self.extract_dividend_yields,
            PBR: self.extract_pbrs,
        }

    def extract_company_codes(self) -> list:
        company_codes = []
        for tag in self.soup.find_all("div", attrs={"class": "md_sub"}):
            company_code_text = str(tag.text)
            if "更新日時" in company_code_text or len(company_code_text) != 4:
                pass
            else:
                company_code = company_code_text
                company_codes.append(company_code)
        return company_codes

    def extract_company_names(self) -> list:
        company_names = []
        for tag in self.soup.find_all("div", attrs={"class": "fwb w90p"}):
            company_name = str(tag.text)
            company_names.append(company_name)
        return company_names

    def extract_stock_prices(self) -> list:
        stock_prices = []
        for tag in self.soup.find_all("td", class_="tar vamd"):
            # タグの中からdiv要素を検索
            div_tag = tag.find("div", class_="wsnw")
            # テキストを取得し、浮動小数点数に変換してリストに追加する
            stock_price_text = div_tag.get_text(strip=True)  # 例：'1,547.0(11:30)'
            stock_price_text = stock_price_text.split("(")[0].replace(",", "")
            stock_price = float(stock_price_text)  # コンマを削除して浮動小数点数に変換
            stock_prices.append(stock_price)
        return stock_prices

    def extract_dividend_yields(self) -> list:
        dividend_yields = []
        for tag in self.soup.find_all("td", class_="tar cur vamd"):
            # タグの中からdiv要素を検索
            div_tag = tag.find("div", class_="underline fwb")
            # div要素が見つかった場合、その中のテキストを取得し、浮動小数点数に変換してリストに追加する
            dividend_yield_text = div_tag.get_text(strip=True).replace("%", "")
            dividend_yield = float(dividend_yield_text)
            dividend_yields.append(dividend_yield)
        return dividend_yields

    def extract_pbrs(self) -> list:
        pbrs = []
        for tag in self.soup.find_all("td", class_="tar cur vamd"):
            # タグの中からdiv要素を検索
            div_tag = tag.find("div", class_="underline fwb")
            # テキストを取得し、浮動小数点数に変換してリストに追加する
            pbr_text = div_tag.get_text(strip=True).replace("倍", "")
            pbr = float(pbr_text)
            pbrs.append(pbr)
        return pbrs

    def extract_data(self, columns: list) -> np.array:
        data = [[] for i in range(len(columns))]
        # カラムで指定したデータの情報を取り出す
        for i, column in enumerate(columns):
            # カラム名からメソッドを得る
            extract = self.extract_method_dict[column]
            data[i] = extract()
            if i != 0:
                assert_text = (
                    f"{columns[i-1]}: {len(data[i-1])}, {columns[i]}: {len(data[i])}"
                )
                assert len(data[i - 1]) == len(data[i]), assert_text
        data = np.array(data).T  # (n, len(column))
        return data


class CompanyHTML(MinkabuHTML):
    def __init__(self, company_code: str) -> None:
        url = f"{MINKABU_STOCK_URL}/{company_code}"
        super().__init__(url)

    def extract_stock_price(self):
        """
        株価を取得するメソッド。HTMLで以下のように記載されている。
        <div class="stock_price">
            3,760.<span class="decimal">0</span>
            <span class="stock_price_unit">円</span>
        </div>
        """
        stock_price_text = self.soup.find("div", class_="stock_price").get_text(
            strip=True
        )
        stock_price = float(stock_price_text.replace(",", "").replace("円", ""))
        return stock_price

    def extract_data(self) -> pd.Series:
        """
        PER, PSR, PBRを取得するメソッド。HTMLで以下のように記載されている。

        <table class="md_table theme_light"><tbody>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">始値</th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">3,610.0円</td>
            </tr>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">高値</th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">3,620.0円</td>
            </tr>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">安値</th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">3,595.0円</td>
            </tr>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw"><a href="https://minkabu.jp/stock/1301/dividend" title="極洋の配当利回り">配当利回り</a></th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">2.77%</td>
        <table class="md_table theme_light"><tbody>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">単元株数</th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">100株</td>
            </tr>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">PER<span class="fss">(調整後)</span></th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">6.67倍</td>
            </tr>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">PSR</th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">0.15倍</td>
            </tr>
            <tr class="ly_vamd">
                <th class="ly_vamd_inner ly_colsize_3_fix tal wsnw">PBR</th>
                <td class="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw">0.91倍</td>
            </tr>
        </tbody></table>
        """
        data = {}
        columns = [STOCK_PRICE, DIVIDEND_YIELD, PER, PSR, PBR]
        # 株価
        stock_price = self.extract_stock_price()
        data[STOCK_PRICE] = stock_price
        # PBR等その他
        for tag in self.soup.find_all("table", class_="md_table theme_light"):
            for tr_tag in tag.find_all("tr", class_="ly_vamd"):
                key = self._extaract_key(tr_tag)
                if key in columns:
                    value_text = self._extaract_value(tr_tag)
                    if key == DIVIDEND_YIELD:
                        value = float(value_text.replace("%", ""))
                    elif key in [PER, PSR, PBR]:
                        value = float(value_text.replace("倍", ""))
                else:
                    continue
                data[key] = value
        data = pd.Series(data)
        return data

    def _extaract_key(self, tag) -> str:
        key = tag.find("th", class_="ly_vamd_inner ly_colsize_3_fix tal wsnw")
        if key:
            key = key.get_text(strip=True)
            if PER in key:
                # PERは'PER(調整後)'として記載されている
                key = key.split("(")[0]
        else:
            raise ValueError(f"Error occured in searching bellow tag.\n{tag}")
        return key

    def _extaract_value(self, tag) -> str:
        value = tag.find("td", class_="ly_vamd_inner ly_colsize_9_fix fwb tar wsnw")
        if value:
            value = value.get_text(strip=True)
        else:
            raise ValueError(f"Error occured in searching bellow tag.\n{tag}")
        return value

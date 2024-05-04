from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
import japanize_matplotlib

from jhdsfinder.dataframe import *
from jhdsfinder.data import FinanceData, CompanyData
from jhdsfinder.mujinzou import get_stock_price_date
from jhdsfinder.gui.abstract import *
from jhdsfinder.gui.abstract import Mediator
from jhdsfinder.screener import *
from jhdsfinder.gui.components import *
from jhdsfinder.gui.events import Event
from jhdsfinder.gui import utils


class CompanyPerformanceCanvas(ComponentFigureCanvas):
    title_font_size = 10
    axis_font_size = 8
    text_font_size = 8

    def __init__(self, fig, mediator: Mediator):
        super().__init__(fig, mediator)

    def plot_figures(self, company_data: CompanyData, figure_columns: list):
        self.figure.clear()
        nrows, ncols = self.get_nrows_ncols(figure_columns)
        for i, column in enumerate(figure_columns):
            x, y = company_data.get_values(column)
            ax = self.figure.add_subplot(nrows, ncols, i + 1)
            ax.set_title(column)
            x, y = company_data.get_values(column)
            ax.bar(x, y)

        self.figure.tight_layout()
        self.draw()

    def get_nrows_ncols(self, figure_columns: list):
        n = len(figure_columns)
        if n == 1:
            return 1, 1
        elif n <= 4:
            return 2, 2
        elif n <= 6:
            return 2, 3
        elif n <= 9:
            return 3, 3
        else:
            raise ValueError(f"Cannot get nrows and ncols. (num_columns={n})")


class YahooFianceLinkLabel(ComponentQLabel):
    code_keyword = "<COMPANY_CODE>"
    _text = f"<a href='https://finance.yahoo.co.jp/quote/{code_keyword}.T'>Yahoo!ファイナンスへのリンク</a>"

    def __init__(self, parent: QWidget, mediator: Mediator):
        super().__init__(parent, mediator)
        self.setText(self._text)
        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def receive_event(self, event):
        if event in Event.COMPANY_CODE_CHANGED:
            company_data = self.mediator.get_selected_company_data()
            selected_company_code = company_data.company_code
            new_text = self._text.replace(self.code_keyword, selected_company_code)
            self.setText(new_text)


class CustomLabel(ComponentQLabel):
    small_text_keyword = "<SMALL_TEXT>"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        text: str,
        font1: QFont,
        font2: QFont,
    ):
        super().__init__(parent, mediator)
        font_size = font1.pointSize()
        small_font_size = font2.pointSize()
        self._text = f"""
        <span style="font-size:{font_size}px">{text}</span>
        <span style="font-size:{small_font_size}px">{self.small_text_keyword}</span>
        """
        self.setText(self._text)
        self.setTextFormat(Qt.TextFormat.RichText)

    def update_small_text(self, small_text: str):
        text = self._text.replace(self.small_text_keyword, small_text)
        self.setText(text)


class InformationLabel(QLabel):
    def __init__(self, parent: QWidget, text: str, font: QFont):
        super().__init__(parent)
        self.setText(text)
        self.setFont(font)


class StockPriceLabel(CustomLabel):
    _text = "株価"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        font1: QFont,
        font2: QFont,
    ):
        super().__init__(parent, mediator, self._text, font1, font2)

    def receive_event(self, event):
        if event in Event.COMPANY_CODE_CHANGED:
            date = get_stock_price_date().strftime("%m/%d")
            small_text = f"({date})"
            self.update_small_text(small_text)


class ExpectedValueLabel(CustomLabel):
    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        text: str,
        font1: QFont,
        font2: QFont,
    ):
        super().__init__(parent, mediator, text, font1, font2)
        small_text = "(実績予想)"
        self.update_small_text(small_text)


class YearLabel(ComponentQLabel):
    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        font: QFont,
    ):
        super().__init__(parent, mediator)
        self.setFont(font)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

    def receive_event(self, event):
        if event in Event.COMPANY_CODE_CHANGED:
            company_data = self.mediator.get_selected_company_data()
            year = company_data.get_latest_year()
            text = f"※{year}年実績"
            self.setText(text)


class CompanyCodeLineEdit(ComponentQLineEdit):
    def __init__(self, parent, mediator):
        super().__init__(parent, mediator)
        self.returnPressed.connect(self.textEntered)
        self.company_codes = self.mediator.get_company_codes()

    def textEntered(self):
        entered_company_code = self.text()
        if entered_company_code in self.company_codes:
            self.mediator.set_selected_company_data(entered_company_code)
            self.send_event(Event.COMPANY_CODE_ENTERED)
        else:
            print(f"{entered_company_code} is not acceptable.")
            if len(entered_company_code) > 6:
                entered_company_code = entered_company_code[:4] + "..."
            msg = f"「{entered_company_code}」の銘柄コードは存在しません."
            self.setText("")
            utils.show_warning_popup(self.parent(), msg)


class CompanyInformation(Component):
    _title = "企業情報"
    upper_space = 30
    space = 5
    figure_columns = [
        REVENUE,
        EPS,
        OPERATING_PROFIT_MARGIN,
        EQUITY_RATIO,
        OPERATING_CASH_FLOW,
        CASH_EQUIVALENTS,
        DIVIDEND_PER_SHARE,
        DIVIDEND_PAYOUT_RATIO,
    ]

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        geometory: tuple,
        finance_data: FinanceData,
        h1Font: QFont,
        h2Font: QFont,
        h3Font: QFont,
    ):
        super().__init__(mediator)
        self.parent = parent
        self.geometory = geometory
        self.finance_data = finance_data
        self.fy_all_df = self.finance_data.get_finance_all_dataframe()
        self.h1Font = h1Font
        self.h2Font = h2Font
        self.h3Font = h3Font
        label_font = self.h2Font
        small_label_font = self.h3Font
        asr = ("\u2070" + "*")[-1]
        self.labels = [
            InformationLabel(parent, "銘柄名", label_font),
            InformationLabel(parent, "業種", label_font),
            InformationLabel(parent, "市場名", label_font),
            StockPriceLabel(parent, self.mediator, label_font, small_label_font),
            ExpectedValueLabel(
                parent, self.mediator, "配当利回り", label_font, small_label_font
            ),
            ExpectedValueLabel(
                parent, self.mediator, "PER", label_font, small_label_font
            ),
            ExpectedValueLabel(
                parent, self.mediator, "PBR", label_font, small_label_font
            ),
            InformationLabel(parent, "1株配当" + asr, label_font),
            InformationLabel(parent, "EPS" + asr, label_font),
            InformationLabel(parent, "BPS" + asr, label_font),
            InformationLabel(parent, "ROE" + asr, label_font),
            InformationLabel(parent, "ROA" + asr, label_font),
            InformationLabel(parent, "営業利益率" + asr, label_font),
            InformationLabel(parent, "自己資本比率" + asr, label_font),
            InformationLabel(parent, "配当性向" + asr, label_font),
        ]
        self.init_ui()

    def init_ui(self):
        self.set_geometory()
        # GruopBox
        self.groupBox = QGroupBox(self._title, self.parent)
        self.groupBox.setGeometry(*self.geometory)
        self.groupBox.setFont(self.h1Font)
        #
        self.set_figure_widget()
        self.set_info_widget()

    def set_info_widget(self):
        self.infoWidget = QWidget(self.parent)
        self.infoWidget.setGeometry(*self.info_geometory)
        self.infoVBoxLayout = QVBoxLayout()
        self.infoWidget.setLayout(self.infoVBoxLayout)
        self.formLayout = QFormLayout()
        self.infoVBoxLayout.addLayout(self.formLayout)
        #
        self.companyCodeLabel = QLabel(self.parent)
        self.companyCodeLabel.setText(COMPANY_CODE)
        self.companyCodeLabel.setFont(self.h2Font)
        self.companyCodeLineEdit = CompanyCodeLineEdit(self.parent, self.mediator)
        self.companyCodeLineEdit.setFont(self.h2Font)
        self.formLayout.addRow(self.companyCodeLabel, self.companyCodeLineEdit)
        underLineFont = QFont()
        underLineFont.setPointSize(self.h2Font.pointSize())
        underLineFont.setUnderline(True)
        self.rightLabels = []
        for leftLabel in self.labels:
            rightLabel = QLabel(self.parent)
            rightLabel.setFont(underLineFont)
            self.formLayout.addRow(leftLabel, rightLabel)
            self.rightLabels.append(rightLabel)
        self.yearLabel = YearLabel(self.parent, self.mediator, self.h2Font)
        self.infoVBoxLayout.addWidget(self.yearLabel)
        self.yahooLinkLabel = YahooFianceLinkLabel(self.parent, self.mediator)
        self.yahooLinkLabel.setFont(self.h2Font)
        self.infoVBoxLayout.addWidget(self.yahooLinkLabel)
        self.spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.infoVBoxLayout.addItem(self.spacer)

    def set_figure_widget(self):
        self.figureWidget = QWidget(self.parent)
        self.figureWidget.setGeometry(*self.figure_geometory)
        self.fig = plt.figure(figsize=self.figsize)
        self.canvas = CompanyPerformanceCanvas(self.fig, self.mediator)
        self.figureVBoxLayout = QVBoxLayout()
        self.figureVBoxLayout.addWidget(self.canvas)
        self.figureWidget.setLayout(self.figureVBoxLayout)

    def set_geometory(self):
        x, y, w, h = self.geometory
        xi = x + self.space
        yi = y + self.upper_space
        wi = int(w * 0.25)
        hi = h - self.space - self.upper_space
        self.info_geometory = (xi, yi, wi, hi)
        xf = xi + wi + self.space
        yf = yi
        wf = w - wi - self.space * 2
        hf = hi
        self.figure_geometory = (xf, yf, wf, hf)
        self.figsize = (wf / 100, hf / 100)

    def get_figure_columns(self):
        return self.figure_columns

    def receive_event(self, event):
        if event in Event.COMPANY_CODE_CHANGED:
            company_data = self.mediator.get_selected_company_data()
            figure_columns = self.get_figure_columns()
            self.canvas.plot_figures(company_data, figure_columns)
            self.update_info(company_data)
            print(company_data)

    def update_info(self, company_data: CompanyData):
        company_code = company_data.company_code
        company_name = company_data.company_name
        industry_category = company_data.industry_category_33
        scale_category = company_data.scale_category
        series = company_data.get_long_term_performance(calc_years=1)
        stock_price = str(company_data.stock_price) + " 円"
        years, dividend_per_shares = company_data.get_dividend_per_share()
        dividend_per_share = "{:.2f}".format(dividend_per_shares[-1]) + " 円"
        dividend_yield = "{:.2f}".format(series[DIVIDEND_YIELD].item()) + " %"
        per = "{:.2f}".format(series[PER].item()) + " 倍"
        pbr = "{:.2f}".format(series[PBR].item()) + " 倍"
        years, eps = company_data.get_EPS()
        eps = "{:.1f}".format(eps[-1])
        years, bps = company_data.get_BPS()
        bps = "{:.1f}".format(bps[-1])
        roe = "{:.2f}".format(series[ROE_AVG].item()) + " %"
        roa = "{:.2f}".format(series[ROA_AVG].item()) + " %"
        equity_ratio = "{:.2f}".format(series[EQUITY_RATIO_AVG].item()) + " %"
        operating_profit_margin = (
            "{:.2f}".format(series[OPERATING_PROFIT_MARGIN_AVG].item()) + " %"
        )
        dividend_payout_ratio = (
            "{:.2f}".format(series[DIVIDEND_PAYOUT_RATIO_AVG].item()) + " %"
        )
        info_texts = [
            company_name,
            industry_category,
            scale_category,
            stock_price,
            dividend_yield,
            per,
            pbr,
            dividend_per_share,
            eps,
            bps,
            roe,
            roa,
            operating_profit_margin,
            equity_ratio,
            dividend_payout_ratio,
        ]
        self.companyCodeLineEdit.setText(company_code)
        for i in range(len(info_texts)):
            text = info_texts[i]
            label: QLabel = self.rightLabels[i]
            label.setText(text)

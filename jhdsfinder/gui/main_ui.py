import sys
from typing import Tuple, List
import platform
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from jhdsfinder.gui import utils
from jhdsfinder.gui.abstract import *
from jhdsfinder.gui.search_condition import SearchConditionSetting
from jhdsfinder.gui.screened_result import ScreenedResult
from jhdsfinder.gui.company_info import CompanyInformation


class MainWindowUI(QMainWindow):
    TITLE = "優良高配当株ファインダー"
    TITLE_SEQRCH_CONDITION_VIEW = "検索条件設定"
    TITLE_SCREENED_RESULT_VIEW = "スクリーニング結果"
    TITLE_PERFORMANCE_VIEW = "企業業績"

    SPACE = 10

    def __init__(self, mediator: Mediator):
        super().__init__()
        self.mediator = mediator
        self.set_font()

        self.init_ui()

    def set_font(self):
        os_name = platform.system()
        if os_name == "Darwin":
            self.FONT_SIZE_H1 = 20
            self.FONT_SIZE_H2 = 16
            self.FONT_SIZE_H3 = 12
        elif os_name == "Windows":
            self.FONT_SIZE_H1 = 12
            self.FONT_SIZE_H2 = 10
            self.FONT_SIZE_H3 = 8

        self.h1Font = QFont()
        self.h1Font.setPointSize(self.FONT_SIZE_H1)
        self.h2Font = QFont()
        self.h2Font.setPointSize(self.FONT_SIZE_H2)
        self.h3Font = QFont()
        self.h3Font.setPointSize(self.FONT_SIZE_H3)

    def init_ui(self):
        self.setWindowTitle(self.TITLE)
        self.set_window_size()
        self.set_geometory()
        self.searchCondition = SearchConditionSetting(
            self,
            self.mediator,
            self.geometory1,
            self.h1Font,
            self.h2Font,
            self.h3Font,
        )
        self.screenedResult = ScreenedResult(
            self,
            self.mediator,
            self.geometory2,
            self.mediator.screened_df,
            self.h1Font,
            self.h2Font,
            self.h3Font,
        )

        self.companyInfo = CompanyInformation(
            self,
            self.mediator,
            self.geometory3,
            self.mediator.finance_data,
            self.h1Font,
            self.h2Font,
            self.h3Font,
        )

    def set_window_size(self):
        # 画面のプライマリディスプレイのジオメトリを取得
        screen_geometory = QGuiApplication.primaryScreen().availableGeometry()
        # 画面の幅と高さを取得
        self.width_size = screen_geometory.width()
        self.height_size = screen_geometory.height() - 30
        self.setGeometry(0, 0, self.width_size, self.height_size)

    def set_geometory(self):
        #
        x1 = self.SPACE
        y1 = self.SPACE
        w1 = int(self.width_size * 0.2)
        h1 = self.height_size - self.SPACE * 2
        self.geometory1 = (x1, y1, w1, h1)
        #
        x2 = w1 + x1 + self.SPACE
        y2 = self.SPACE
        w2 = self.width_size - x2 - self.SPACE
        h2 = int(self.height_size * 0.25)
        self.geometory2 = (x2, y2, w2, h2)
        #
        x3 = x2
        y3 = self.SPACE + y2 + h2
        w3 = w2
        h3 = self.height_size - y3 - self.SPACE
        self.geometory3 = (x3, y3, w3, h3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    width, height = utils.get_screen_size()
    window = MainWindowUI(width, height)
    window.showFullScreen()
    # window.show()
    app.exec()

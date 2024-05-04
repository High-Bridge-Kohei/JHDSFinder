from typing import Tuple, List
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from jhdsfinder.gui.abstract import Mediator, Component
from jhdsfinder.screener import *
from jhdsfinder.gui.easy_setting import EasySetting
from jhdsfinder.gui.detail_setting import DetailSetting
from jhdsfinder.gui.events import Event


class SearchConditionSetting(Component):
    _title = "検索条件設定"
    # TEXT_RUN_SEARCH_BUTTON = "検索実行"
    # TEXT_RUNNING_SEARCH_BUTTON = "検索実行中..."

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        geometory: tuple,
        h1Font: QFont,
        h2Font: QFont,
        h3Font: QFont,
    ):
        super().__init__(mediator)
        self.parent = parent
        self.geometory = geometory
        self.h1Font = h1Font
        self.h2Font = h2Font
        self.h3Font = h3Font
        self.init_ui()

    def init_ui(self):
        self.groupBox = QGroupBox(self._title, self.parent)
        self.groupBox.setGeometry(*self.geometory)
        self.groupBox.setFont(self.h1Font)
        self.vBoxLayout = QVBoxLayout(self.groupBox)
        self.vBoxLayout.setContentsMargins(2, 2, 2, 2)
        # 簡易設定
        self.easySetting = EasySetting(
            self.parent,
            self.mediator,
            self.vBoxLayout,
            self.h1Font,
            self.h2Font,
            self.h3Font,
        )
        # 詳細設定
        self.detailSetting = DetailSetting(
            self.parent,
            self.mediator,
            self.vBoxLayout,
            self.h1Font,
            self.h2Font,
            self.h3Font,
        )
        # ボタンをグループ化
        self.buttonGroup = QButtonGroup(self.groupBox)
        self.buttonGroup.addButton(self.easySetting.checkBox)
        self.buttonGroup.addButton(self.detailSetting.checkBox)

        # # レイアウト
        # self.runSearchVBoxLayout = QVBoxLayout()
        # self.vBoxLayout.addLayout(self.runSearchVBoxLayout)
        # ラベル
        # self.numberOfCompanyLabel = QLabel(self.groupBox)
        # self.numberOfCompanyLabel.setText(self.TEXT_NUMBER_OF_COMPANIES)
        # self.vBoxLayout.addWidget(self.numberOfCompanyLabel)
        # self.runSearchVBoxLayout.addWidget(self.numberOfCompanyLabel)
        # # ボタン
        # self.runSearchPushButton = QPushButton(self.groupBox)
        # self.runSearchPushButton.setText(self.TEXT_RUN_SEARCH_BUTTON)
        # self.runSearchVBoxLayout.addWidget(self.runSearchPushButton)
        # # プログレスバー
        # self.serachProgressBar = QProgressBar(self.groupBox)
        # self.runSearchVBoxLayout.addWidget(self.serachProgressBar)
        # 検索結果の企業数を初期化

    # def receive_event(self, event):
    #     conditions = self.get_conditionds(event)
    #     if conditions is not None:
    #         self.mediator.set_screened_company_codes(conditions)
    #         company_codes = self.mediator.get_screened_company_codes()
    #         self.update_number_of_companies(company_codes)

    # def get_conditionds(self, event):
    #     if event in Event.GETTING_EASY_CONDITION_EVENTS:
    #         conditions = self.easySetting.get_conditions()
    #     elif event in Event.GETTING_DETAIL_CONDITION_EVENTS:
    #         conditions = self.detailSetting.get_conditions()
    #     else:
    #         conditions = None
    #     return conditions

    # def update_number_of_companies(self, company_codes):
    #     text = self.TEXT_NUMBER_OF_COMPANIES.replace(
    #         self.keyword, str(len(company_codes))
    #     )
    #     self.numberOfCompanyLabel.setText(text)

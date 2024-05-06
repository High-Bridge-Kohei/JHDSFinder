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

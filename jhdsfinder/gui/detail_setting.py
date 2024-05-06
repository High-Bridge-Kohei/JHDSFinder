from typing import Tuple, List
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from jhdsfinder.gui.abstract import *
from jhdsfinder.screener import *
from jhdsfinder.gui.components import *
from jhdsfinder.gui.events import Event


class DetailSettingCheckBox(ComponentQCheckBox):
    _text = "詳細設定"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
    ):
        super().__init__(parent, mediator, checked=False)
        self.setText(self._text)

    def checkBoxStateChanged(self):
        checked = self.isChecked()
        if checked:
            self.send_event(Event.DETAIL_SETTING_CHECKED)
        else:
            self.send_event(Event.DETAIL_SETTING_UNCHECKED)


class DetailSettingPushButton(ComponentQPushButton):
    _text = "詳細条件設定"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
    ):
        super().__init__(parent, mediator)
        self.setText(self._text)

    def receive_event(self, event):
        if event == Event.DETAIL_SETTING_CHECKED:
            self.setEnabled(True)
        elif event == Event.DETAIL_SETTING_UNCHECKED:
            self.setEnabled(False)
        else:
            pass


class DetailSettingLineEdit(ComponentQLineEdit):
    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
    ):
        super().__init__(parent, mediator)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setEnabled(False)


class DetailSetting(Component):
    def __init__(
        self,
        parent,
        mediator: Mediator,
        settingVBoxLayout: QVBoxLayout,
        h1Font: QFont,
        h2Font: QFont,
        h3Font: QFont,
    ) -> None:
        super().__init__(mediator)
        self.parent = parent
        self.settingVBoxLayout = settingVBoxLayout
        self.h1Font = h1Font
        self.h2Font = h2Font
        self.h3Font = h3Font

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setContentsMargins(2, 2, 2, 2)
        self.settingVBoxLayout.addLayout(self.vBoxLayout)
        self.checkBox = DetailSettingCheckBox(self.parent, self.mediator)
        self.checkBox.setFont(self.h1Font)
        self.settingVBoxLayout.addWidget(self.checkBox)
        self.pushButton = DetailSettingPushButton(self.parent, self.mediator)
        self.settingVBoxLayout.addWidget(self.pushButton)
        self.pushButton.setFont(self.h2Font)
        self.lineEdit = DetailSettingLineEdit(self.parent, self.mediator)
        self.lineEdit.setFont(self.h3Font)
        self.settingVBoxLayout.addWidget(self.lineEdit)

        # 開発途中
        self.checkBox.setEnabled(False)
        self.pushButton.setEnabled(False)

    def get_conditions(self):
        return Conditions([])

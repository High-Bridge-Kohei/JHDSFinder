from typing import Tuple, List
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from jhdsfinder.gui.abstract import *
from jhdsfinder.screener import *
from jhdsfinder.gui.components import *
from jhdsfinder.gui.events import Event
from jhdsfinder.gui import utils


UPWARD_TREND = "右肩上がり"
UNDER_RANGE = "XX%以下"
UPPER_RANGE = "XX%以上"
SURPLUS_EVERY_YEAR = "毎年黒字"

TREND_TYPE = "trend_type"
RANGE_TYPE = "range_type"
TYPE = "type"
CONDITION = "condition"
TEXT = "text"


class RangeConditionItem(Component):
    keyword = "XX"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        condition: Condition,
        check_box_text: str,
        line_edit_text: str,
        font: QFont,
    ):
        super().__init__(mediator)
        assert self.keyword in check_box_text, check_box_text
        self.condition = condition
        self.origin_text = check_box_text
        if self.condition.vmin is not None:
            self.default_value = self.condition.vmin
        else:
            self.default_value = self.condition.vmax
        self.parent = parent
        # LineEdit
        self.lineEdit = QLineEdit(parent)
        self.lineEdit.setFont(font)
        self.lineEdit.setText(line_edit_text)
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lineEdit.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        # CheckBox
        check_box_text = self.get_check_box_text()
        self.checkBox = QCheckBox(parent)
        self.checkBox.setText(check_box_text)
        self.checkBox.setFont(font)
        self.checkBox.setChecked(True)
        self.checkBox.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        # signal
        self.checkBox.stateChanged.connect(self.checkBoxStateChanged)
        self.lineEdit.returnPressed.connect(
            self.lineEditTextChanged
        )  # TODO: 例外に対処する必要あり

    def get_check_box_text(self):
        thres = self.get_threshold()
        thres_text = "{:.3g}".format(thres)
        text = self.origin_text.replace(self.keyword, thres_text)
        return text

    def get_threshold(self):
        thres = float(self.lineEdit.text())
        return thres

    def lineEditTextChanged(self):
        text = self.lineEdit.text()
        if utils.is_float(text):
            text = self.get_check_box_text()
            self.checkBox.setText(text)
            # 条件変更
            thres = self.get_threshold()
            if self.condition.vmin is not None:
                self.condition.vmin = thres
            else:
                assert self.condition.vmax is not None
                self.condition.vmax = thres
            self.send_event(Event.EASY_SETTING_CONDITION_CHANGED)
        else:
            print(f"{text} is not acceptable.")
            msg = f"{text}は数字に変換できません."
            self.lineEdit.setText(str(self.default_value))
            utils.show_warning_popup(self.parent, msg)

    def checkBoxStateChanged(self, state):
        checked = self.checkBox.isChecked()
        # print("CheckBox state changed!", checked)
        self.lineEdit.setEnabled(checked)
        self.send_event(Event.EASY_SETTING_CONDITION_CHANGED)

    def receive_event(self, event):
        if event == Event.EASY_SETTING_UNCHECKED:
            self.checkBox.setEnabled(False)
            self.lineEdit.setEnabled(False)
        elif event == Event.EASY_SETTING_CHECKED:
            self.checkBox.setEnabled(True)
            if self.checkBox.isChecked():
                self.lineEdit.setEnabled(True)
        else:
            pass


class EasySettingCheckBox(ComponentQCheckBox):
    _text = "簡易設定"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
    ):
        super().__init__(parent, mediator)
        self.setText(self._text)

    def checkBoxStateChanged(self):
        checked = self.isChecked()
        if checked:
            self.send_event(Event.EASY_SETTING_CHECKED)
        else:
            self.send_event(Event.EASY_SETTING_UNCHECKED)


class EasySettingItemCheckBox(ComponentQCheckBox):
    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
    ):
        super().__init__(parent, mediator)

    def receive_event(self, event):
        if event == Event.EASY_SETTING_CHECKED:
            self.setEnabled(True)
        elif event == Event.EASY_SETTING_UNCHECKED:
            self.setEnabled(False)
        else:
            pass

    def send_event(self, event=None):
        event = Event.EASY_SETTING_CONDITION_CHANGED
        return super().send_event(event)


class EasySettingConditionItems(Component):

    item_dict = {
        REVENUE: [
            {
                TYPE: TREND_TYPE,
                TEXT: UPWARD_TREND,
                CONDITION: NumericalCondition(REVENUE_GRAD, 0.0, None),
            }
        ],
        EPS: [
            {
                TYPE: TREND_TYPE,
                TEXT: UPWARD_TREND,
                CONDITION: NumericalCondition(EPS_GRAD, 0.0, None),
            }
        ],
        OPERATING_PROFIT_MARGIN: [
            {
                TYPE: RANGE_TYPE,
                TEXT: UPPER_RANGE,
                CONDITION: NumericalCondition(OPERATING_PROFIT_MARGIN_AVG, 10.0, None),
            }
        ],
        EQUITY_RATIO: [
            {
                TYPE: RANGE_TYPE,
                TEXT: UPPER_RANGE,
                CONDITION: NumericalCondition(EQUITY_RATIO_AVG, 40.0, None),
            }
        ],
        OPERATING_CASH_FLOW: [
            {
                TYPE: TREND_TYPE,
                TEXT: UPWARD_TREND,
                CONDITION: NumericalCondition(OPERATING_CASH_FLOW_GRAD, 0.0, None),
            },
            {
                TYPE: TREND_TYPE,
                TEXT: SURPLUS_EVERY_YEAR,
                CONDITION: NumericalCondition(
                    OPERATING_CASH_FLOW_SURPLUS_EVERY_YEAR, 0.5, None
                ),
            },
        ],
        CASH_EQUIVALENTS: [
            {
                TYPE: TREND_TYPE,
                TEXT: UPWARD_TREND,
                CONDITION: NumericalCondition(CASH_EQUIVALENTS_GRAD, 0.0, None),
            }
        ],
        DIVIDEND_PER_SHARE: [
            {
                TYPE: TREND_TYPE,
                TEXT: UPWARD_TREND,
                CONDITION: NumericalCondition(DIVIDEND_PER_SHARE_GRAD, 0.0, None),
            },
            {
                TYPE: TREND_TYPE,
                TEXT: DIVIDEND_INCREASE_CONTINUOUS,
                CONDITION: NumericalCondition(DIVIDEND_INCREASE_CONTINUOUS, 0.5, None),
            },
        ],
        DIVIDEND_PAYOUT_RATIO: [
            {
                TYPE: RANGE_TYPE,
                TEXT: UNDER_RANGE,
                CONDITION: NumericalCondition(DIVIDEND_PAYOUT_RATIO_AVG, None, 50),
            }
        ],
        DIVIDEND_YIELD: [
            {
                TYPE: RANGE_TYPE,
                TEXT: UPPER_RANGE,
                CONDITION: NumericalCondition(DIVIDEND_YIELD, 3.0, None),
            }
        ],
    }

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        settingVBoxLayout: QVBoxLayout,
        h2Font: QFont,
        h3Font: QFont,
    ):
        super().__init__(mediator)
        self.parent = parent
        self.settingVBoxLayout = settingVBoxLayout
        self.h2Font = h2Font
        self.h3Font = h3Font
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(5, 0, 0, 0)
        self.condition_list: List[Condition] = []
        self.widget_list: List[QWidget] = []
        self.check_box_list: List[QCheckBox] = []
        self.range_condition_item_list = []
        n_row = 0
        for i, (item_name, item_list) in enumerate(self.item_dict.items()):
            n_row += 1
            self.label = QLabel(self.parent)
            item_text = f"{i+1}. {item_name}"
            self.label.setText(item_text)
            self.label.setFont(self.h2Font)
            self.gridLayout.addWidget(self.label, n_row, 0, 1, 2)
            n_row += 1
            for j, _dict in enumerate(item_list):
                _type = _dict[TYPE]
                check_box_text = _dict[TEXT]
                condition = _dict[CONDITION]
                self.condition_list.append(condition)
                if _type == RANGE_TYPE:
                    vmin = condition.vmin
                    vmax = condition.vmax
                    if vmin is not None:
                        line_edit_text = str(vmin)
                    else:
                        line_edit_text = str(vmax)
                    rangeConditionItem = RangeConditionItem(
                        self.parent,
                        self.mediator,
                        condition,
                        check_box_text,
                        line_edit_text,
                        self.h3Font,
                    )
                    checkBox = rangeConditionItem.checkBox
                    lineEdit = rangeConditionItem.lineEdit
                    self.gridLayout.addWidget(
                        checkBox, n_row, 0, Qt.AlignmentFlag.AlignCenter
                    )
                    self.gridLayout.addWidget(
                        lineEdit, n_row, 1, Qt.AlignmentFlag.AlignCenter
                    )
                    self.widget_list.extend([checkBox, lineEdit])
                    self.range_condition_item_list.append(rangeConditionItem)
                else:
                    checkBox = EasySettingItemCheckBox(self.parent, self.mediator)
                    checkBox.setText(check_box_text)
                    checkBox.setFont(self.h3Font)
                    self.gridLayout.addWidget(
                        checkBox, n_row, j, Qt.AlignmentFlag.AlignCenter
                    )
                    self.widget_list.append(checkBox)
                self.check_box_list.append(checkBox)
        self.settingVBoxLayout.addLayout(self.gridLayout)

    def get_conditions(self) -> Conditions:
        conditions = Conditions([])
        for i in range(len(self.condition_list)):
            checkBox: QCheckBox = self.check_box_list[i]
            checked = checkBox.isChecked()
            if checked:
                condition: Condition = self.condition_list[i]
                conditions.add(condition)
        return conditions


class EasySetting(Component):
    keyword = "????"
    text_number_of_companies = f"該当企業数: {keyword}"

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
        self.settingVBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.setContentsMargins(2, 2, 2, 2)
        self.checkBox = EasySettingCheckBox(self.parent, self.mediator)
        self.checkBox.setFont(self.h1Font)
        self.vBoxLayout.addWidget(self.checkBox)
        self.easySettingConditionItems = EasySettingConditionItems(
            self.parent, self.mediator, self.vBoxLayout, h2Font, h3Font
        )

        # self.numberOfCompanyLabel = QLabel(self.parent)
        # self.numberOfCompanyLabel.setText(self.text_number_of_companies)
        # self.numberOfCompanyLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.vBoxLayout.addWidget(self.numberOfCompanyLabel)

    def get_conditions(self):
        return self.easySettingConditionItems.get_conditions()

    def receive_event(self, event):
        if event in Event.GETTING_EASY_CONDITION_EVENTS:
            conditions = self.get_conditions()
            self.mediator.set_screened_company_codes(conditions)
            # company_codes = self.mediator.get_screened_company_codes()
            # self.update_number_of_companies(company_codes)

    # def update_number_of_companies(self, company_codes):
    #     text = self.text_number_of_companies.replace(
    #         self.keyword, str(len(company_codes))
    #     )
    #     self.numberOfCompanyLabel.setText(text)

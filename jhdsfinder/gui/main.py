import os
import sys
import numpy as np
from typing import Tuple, List
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from jhdsfinder.gui.abstract import *
from jhdsfinder.gui import utils
from jhdsfinder.gui.main_ui import MainWindowUI


from jhdsfinder.names import *
from jhdsfinder.dataframe import CompanyPerformanceDataFrame
from jhdsfinder.data import FinanceData
from jhdsfinder.screener import CompanyScreener, Conditions
from jhdsfinder.gui.events import Event


class MainController(Mediator):
    selected_company_code = "1301"
    calc_years = 3

    def __init__(self) -> None:
        super().__init__()
        self.finance_data = FinanceData()
        self.screened_df = self.finance_data.make_screened_company_dataframe()
        self.screener = CompanyScreener(self.finance_data.performance_df)
        self.screened_company_codes = []
        self.ui = MainWindowUI(self)
        self.send_event(Event.INIT_UI, None)

    def set_screened_company_codes(self, conditions: Conditions = []):
        self.screened_company_codes = self.screener.run(conditions)

    def get_screened_company_codes(self):
        return self.screened_company_codes

    def set_selected_company_data(self, company_code: str):
        self.selected_company_data = self.finance_data.get_company_data(company_code)

    def get_selected_company_data(self) -> str:
        return self.selected_company_data

    def get_company_codes(self):
        return self.finance_data.get_company_codes()

    def show(self):
        # self.ui.showFullScreen()
        self.ui.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainController()
    main.show()
    app.exec()

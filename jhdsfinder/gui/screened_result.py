from typing import Tuple, List
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from jhdsfinder.dataframe import ScreenedCompanyDataFrame
from jhdsfinder.gui.abstract import *
from jhdsfinder.screener import *
from jhdsfinder.gui.components import *
from jhdsfinder.gui.events import Event


class ScreenedResultTableView(ComponentQTableView):
    def __init__(
        self, parent: QWidget, mediator: Mediator, df: ScreenedCompanyDataFrame
    ):
        super().__init__(parent, mediator)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        model = ScreenedCompanyTableModel(df, self.mediator)
        self.setModel(model)
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.handle_selection_changed)

    def handle_selection_changed(self, selected, deselected):
        # 選択された行のインデックスを取得
        indexes = selected.indexes()
        if indexes:
            # 最初の選択された行のインデックスから行番号を取得
            row_idx = indexes[0].row()
            # 銘柄コードを取得
            selected_company_code = self.model()._dataframe.iloc[row_idx, 0]
            # mediatorにセット
            self.mediator.set_selected_company_data(selected_company_code)
            # イベント通知
            self.send_event(Event.COMPANY_SELECTED_ON_TABLE)

    def tableClicked(self, index):
        row_idx = index.row()
        selected_company_code = self.model()._dataframe.iloc[row_idx, 0]
        self.mediator.set_selected_company_data(selected_company_code)
        self.send_event(Event.COMPANY_SELECTED_ON_TABLE)

    def update_dataframe(self, df: ScreenedCompanyDataFrame):
        self.model().update_model(df)

    def receive_event(self, event):
        if event == Event.INIT_UI:
            model = self.selectionModel()
            # 選択する行のインデックスを作成
            row_index = QModelIndex(model.model().index(0, 0))
            # 選択範囲を作成し、選択モデルに追加
            selection = QItemSelection()
            selection.select(row_index, row_index)
            model.select(selection, QItemSelectionModel.SelectionFlag.Select)


class ScreenedCompanyTableModel(PandasModel):
    def __init__(self, dataframe: pd.DataFrame, mediator: Mediator):
        super().__init__(dataframe, mediator)


class ScreenedResult(Component):
    keyword = "????"
    _title = f"スクリーニング結果 (該当企業数: {keyword})"

    def __init__(
        self,
        parent: QWidget,
        mediator: Mediator,
        geometory: tuple,
        df: ScreenedCompanyDataFrame,
        h1Font: QFont,
        h2Font: QFont,
        h3Font: QFont,
    ):
        super().__init__(mediator)
        self.parent = parent
        self.geometory = geometory
        self.df = df
        self.h1Font = h1Font
        self.h2Font = h2Font
        self.h3Font = h3Font
        self.init_ui()

    def init_ui(self):
        # GruopBox
        self.groupBox = QGroupBox(self._title, self.parent)
        self.groupBox.setGeometry(*self.geometory)
        self.groupBox.setFont(self.h1Font)
        # TableView
        self.tableView = ScreenedResultTableView(self.parent, self.mediator, self.df)
        self.tableView.setFont(self.h3Font)
        self.tableView.setAlternatingRowColors(True)
        # Layout
        self.vBoxLayout = QVBoxLayout(self.groupBox)
        self.vBoxLayout.addWidget(self.tableView)

    def receive_event(self, event):
        if event in Event.CONDITION_CHANGED:
            company_codes = self.mediator.get_screened_company_codes()
            df = self.df[self.df[COMPANY_CODE].isin(company_codes)]
            df = df.sort_values(by=DIVIDEND_YIELD, ascending=False)
            self.tableView.update_dataframe(df)
            self.update_number_of_companies(company_codes)

    def update_number_of_companies(self, company_codes):
        title = self._title.replace(self.keyword, str(len(company_codes)))
        self.groupBox.setTitle(title)

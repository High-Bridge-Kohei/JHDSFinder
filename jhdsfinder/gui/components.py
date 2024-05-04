from typing import Any

import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from jhdsfinder.gui.abstract import *


class ComponentQLabel(Component, QLabel):
    def __init__(self, parent: QWidget, mediator: Mediator, event=None):
        super().__init__(mediator)
        QLabel.__init__(self, parent)
        self._event = event


class ComponentQCheckBox(Component, QCheckBox):
    def __init__(self, parent: QWidget, mediator: Mediator, event=None, checked=True):
        super().__init__(mediator)
        QCheckBox.__init__(self, parent)
        self._event = event
        self.setChecked(checked)
        self.stateChanged.connect(self.checkBoxStateChanged)

    def checkBoxStateChanged(self):
        self.send_event(self._event)


class ComponentQPushButton(Component, QPushButton):
    def __init__(self, parent: QWidget, mediator: Mediator, event=None):
        super().__init__(mediator)
        QPushButton.__init__(self, parent)
        self._event = event
        self.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        self.send_event(self._event)


class ComponentQLineEdit(Component, QLineEdit):
    def __init__(self, parent: QWidget, mediator: Mediator, event=None):
        super().__init__(mediator)
        QPushButton.__init__(self, parent)
        self._event = event


class ComponentQTableView(Component, QTableView):
    def __init__(self, parent: QWidget, mediator: Mediator, event=None):
        super().__init__(mediator)
        QTableView.__init__(self, parent)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._event = event


class PandasModel(Component, QAbstractTableModel):
    """
    A model to interface a Qt view with pandas dataframe
    https://bitwalk.blogspot.com/2022/05/pandas-pyside6.html
    """

    def __init__(self, dataframe: pd.DataFrame, mediator: Mediator, parent=None):
        super().__init__(mediator)
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel
        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel
        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel
        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        value = self._dataframe.iloc[row, col]

        if role == Qt.ItemDataRole.DisplayRole:
            return str(value)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if (type(value) is np.int64) | (type(value) is np.float64):
                flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            else:
                flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            return flag

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        """Override method from QAbstractTableModel
        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Orientation.Vertical:
                # return str(self._dataframe.index[section])
                return None

        return None

    def update_model(self, new_data: pd.DataFrame):
        # データフレームを新しいデータで更新
        self._dataframe = new_data

        # モデルデータの構造が変更された場合は、ここでモデルをリセット
        self.beginResetModel()
        self.endResetModel()

        # モデルにデータ更新を通知
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def sort(self, column: int, order=Qt.SortOrder.AscendingOrder):
        # データを指定された列でソート
        self._dataframe = self._dataframe.sort_values(
            by=self._dataframe.columns[column],
            ascending=(order == Qt.SortOrder.AscendingOrder),
        )
        self.dataChanged.emit(
            self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1)
        )


class ComponentFigureCanvas(Component, FigureCanvas):
    def __init__(self, fig, mediator: Mediator):
        super().__init__(mediator)
        FigureCanvas.__init__(self, fig)

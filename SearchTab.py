import sys
import re
import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QTabWidget, QDateEdit, QFormLayout,
                               QComboBox, QTableView, QAbstractItemView, QGridLayout,
                               QRadioButton, QButtonGroup, QStyle, QScrollArea, QMenu,
                               QDialog)
from PySide6.QtCharts import QChartView, QPieSeries, QChart
from PySide6.QtGui import QAction, QPainter, QIcon
import qtawesome as qta
from connection1 import ConnectAccount, ConnectWorkDiary
from test_pandas import PandasModel


class SearchTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.search_tab_container = QVBoxLayout()
        self.search_tab_container.addWidget(self.SearchLE())
        # self.search_tab_container.addStretch()
        self.search_tab_container.addLayout(self.DisplayArea())
        # self.search_tab_container.addLayout(self.TableArea())
        # self.search_tab_container.addLayout(self.FormArea())

        self.setLayout(self.search_tab_container)

    def SearchLE(self):
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText("搜尋...")

        self.action = self.search_le.addAction(
            QIcon("search.png"),
            QLineEdit.ActionPosition.TrailingPosition
        )

        self.action.triggered.connect(self._SearchClicked)

        return self.search_le

    @Slot()
    def _SearchClicked(self):
        print("Searching...")
        match = self.search_le.text()

        connection = ConnectAccount()
        search_result = connection.Searching(match=match)

        print(search_result)

        df = pd.DataFrame(search_result)
        model = PandasModel(df)
        model.horizontal_header = ["科目代碼", "會計科目", "明細摘要", "支出明細", "收入明細"]

        self.result_table.setModel(model_detail)

    def DisplayArea(self):
        self.result_tilte = QLabel("搜尋結果：")
        self.result_tilte.setStyleSheet('font-size: 15px; color: #333; font-weight: 300')

        self.result_table = QTableView()
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)  # set same width as tab container
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableView.SelectRows)

        self.display_area = QVBoxLayout()
        self.display_area.addWidget(self.result_tilte)
        self.display_area.addWidget(self.result_table)

        return self.display_area

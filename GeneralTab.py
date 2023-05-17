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

today = QtCore.QDate.currentDate()


class GeneralTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.title_label = QLabel("心富工程行")
        self.title_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.title_label.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.date = QLabel(today.toString("yyyy/MM/dd"))
        self.date.setAlignment(QtCore.Qt.AlignHCenter)
        self.date.setStyleSheet('font-size: 25px; color: #333; font-weight: 500')

        # Chart
        # self.revenues_chart_view = QChartView()
        # self.revenues_chart_view.setRenderHint(QPainter.Antialiasing)
        # self.expenditure_chart_view = QChartView()
        # self.expenditure_chart_view.setRenderHint(QPainter.Antialiasing)

        # self.chart_area = QHBoxLayout()
        # # self.chart_area.addWidget(self.revenues_chart_view)
        # self.chart_area.addWidget(self.expenditure_chart_view)
        # self.PlotData()
        #
        self.refresh_button = QPushButton("重新整理")
        self.refresh_button.clicked.connect(self.RefreshAccountSummaryTable)

        self.general_tab_container = QVBoxLayout()
        self.general_tab_container.addWidget(self.title_label)
        self.general_tab_container.addWidget(self.date)
        self.general_tab_container.addLayout(self.AccountSummaryTable())
        self.general_tab_container.addStretch()
        # self.general_tab_container.addLayout(self.chart_area)
        self.general_tab_container.addWidget(self.refresh_button)

        self.setLayout(self.general_tab_container)

    def AccountSummaryTable(self):
        self.summary_tilte = QLabel("帳戶清單")
        self.summary_tilte.setStyleSheet('font-size: 15px; color: #333; font-weight: 300')

        self.summary_table = QTableView()
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # set same width as tab container
        # self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionBehavior(QTableView.SelectRows)
        # self.summary_table.setHorizontalHeader(0, QTableWidgetItem("帳戶"))

        connection = ConnectAccount()
        results = connection.SummaryByAccount()
        df = pd.DataFrame(results)
        model = PandasModel(df)
        model.horizontal_header = ["帳戶名稱", "總收入", "總支出", "帳戶餘額"]
        self.summary_table.setModel(model)

        self.summary_table.hideColumn(1)
        self.summary_table.hideColumn(2)

        self.summary_area = QGridLayout()
        self.summary_area.addWidget(self.summary_tilte, 0, 0)
        self.summary_area.addWidget(self.summary_table, 1, 0)

        return self.summary_area

    @Slot()
    def RefreshAccountSummaryTable(self):
        connection = ConnectAccount()
        results = connection.SummaryByAccount()
        df = pd.DataFrame(results)
        model = PandasModel(df)
        self.summary_table.setModel(model)

    @Slot()
    def PlotData(self):
        connection = ConnectAccount()
        results = connection.Summary()

        revenues_series = QPieSeries()
        expenditure_series = QPieSeries()

        for data in results:
            text = data["_id"] + data["accounting_item"]
            number = float(data["total_expenditure"])
            if data["total_expenditure"] > 0:
                # print("total_expenditure")
                # print(text, number)
                expenditure_series.append(text, number)
            else:
                # print("total_revenues")
                # print(text, number)
                revenues_series.append(text, number)

        for i in range(5):
            chart_expenditure_slice = expenditure_series.slices()[i]
            chart_expenditure_slice.setLabelVisible()

        # chart_revenues = QChart()
        chart_expenditure = QChart()
        # chart_revenues.addSeries(revenues_series)
        chart_expenditure.addSeries(expenditure_series)
        # chart_revenues.legend().setAlignment(Qt.AlignLeft)
        chart_expenditure.legend().setAlignment(Qt.AlignLeft)

        # self.revenues_chart_view.setChart(chart_revenues)
        self.expenditure_chart_view.setChart(chart_expenditure)
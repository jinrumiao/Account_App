import sys
import re
import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QTabWidget, QDateEdit, QFormLayout,
                               QComboBox, QTableView, QAbstractItemView, QGridLayout, QRadioButton, QButtonGroup,
                               QStyle, QScrollArea, QMenu, QDialog)
from PySide6.QtCharts import QChartView, QPieSeries, QChart
from PySide6.QtGui import QAction, QPainter, QIcon
import qtawesome as qta
from connection1 import ConnectAccount, ConnectWorkDiary
from AccountDialogUI import AccountDialog
from GeneralTab import GeneralTab
from InsertTab import InsertTab
from WorkDiaryTab import WorkDiaryTab
from SearchTab import SearchTab

# today = QtCore.QDate.currentDate()


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.tab_general = GeneralTab(self)
        self.tab_insert = InsertTab(self)
        self.tab_work_diary = WorkDiaryTab(self)
        self.tab_search = SearchTab(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.tab_general, "首頁")
        self.tab_widget.addTab(self.tab_insert, "日記簿 / 輸入資料")
        self.tab_widget.addTab(self.tab_work_diary, "工作日誌 / 輸入資料")
        # self.tab_widget.addTab(self.tab_search, "搜尋")

        self.tab_insert.insert_button.clicked.connect(self.tab_general.RefreshAccountSummaryTable)

        self.body = QVBoxLayout()
        self.body.addWidget(self.tab_widget)

        self.setLayout(self.body)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Accounting System")
        self.resize(1200, 900)
        self.setUpdatesEnabled(True)

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Initial Qt application
    app = QApplication(sys.argv)

    # QWidget
    widget = Widget()  # QMainWindow using QWidget as central widget

    window = MainWindow(widget)
    window.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    # Execute application
    sys.exit(app.exec())

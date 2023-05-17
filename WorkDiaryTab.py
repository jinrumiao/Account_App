import sys
import re
import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QTabWidget, QDateEdit, QFormLayout,
                               QComboBox, QTableView, QAbstractItemView, QGridLayout,
                               QRadioButton, QButtonGroup, QStyle, QScrollArea, QMenu,
                               QDialog, QMessageBox)
from PySide6.QtCharts import QChartView, QPieSeries, QChart
from PySide6.QtGui import QAction, QPainter, QIcon
import qtawesome as qta
from connection1 import ConnectAccount, ConnectWorkDiary
from test_pandas import PandasModel
from WorkDiaryDialogUI import WorkDiaryDialog, DiaryExportDialog

today = QtCore.QDate.currentDate()


class WorkDiaryTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.work_diary_tab_container = QHBoxLayout()

        self.work_diary_tab_container.addLayout(self.TableArea())
        self.work_diary_tab_container.addLayout(self.FormArea())

        self.setLayout(self.work_diary_tab_container)

    def TableArea(self):
        self.data = self.GetData()

        self.selected_target = []
        self.dialog_info = []

        self.table_title = QLabel("工作紀錄")
        self.table_title.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.tableview_widget = QTableView()
        self.tableview_widget.horizontalHeader().setStretchLastSection(True)
        # self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # set same width as tab container
        self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableview_widget.setAlternatingRowColors(True)
        self.tableview_widget.setSelectionBehavior(QTableView.SelectRows)
        # self.tableview_widget.setSelectionMode(QTableView.ExtendedSelection)
        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        model.horizontal_header = ["id", "日期", "品名", "規格", "數量", "單價", "金額", "備註"]
        self.tableview_widget.setModel(model)

        self.tableview_widget.hideColumn(0)

        self.table = QVBoxLayout()
        self.table.addWidget(self.table_title)
        self.table.addWidget(self.tableview_widget)

        self.tableview_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableview_widget.customContextMenuRequested.connect(self.ContextMenu)

        self.tableview_widget.selectionModel().currentChanged.connect(self.__SelectedRow)

        return self.table

    def GetData(self):
        connection = ConnectWorkDiary()
        data = connection.QueryData()

        return data

    def ContextMenu(self, pos):
        context = QMenu()
        context.addAction(QIcon(qta.icon("ei.file-edit-alt")), "編輯", self.__ClickedEdit)
        context.addAction(QIcon(qta.icon("mdi.delete-circle")), "刪除", self.__ClickedDelete)
        context.addAction(QIcon(qta.icon("mdi.file-export")), "輸出", self.__ClickedExport)
        context.setStyleSheet("font-size: 20px; color: #333; icon-size: 30px;")
        # context.setIconSize(QSize(20, 20))
        context.exec(self.mapToGlobal(pos))

    @Slot()
    def __SelectedRow(self, selected, deselected):
        # selected_ix = selected.indexes()[0].row()
        # deselected_ix = deselected.indexes()[0].row()
        # self.selected_index.append(selected_ix)
        # deselected_ix = deselected.indexes()[0].row()
        # print(f"Selected: {selected_ix}, Deselected: {deselected_ix}")
        print(f"Selected: {selected.row()}, Deselected: {deselected.row()}")
        # print(self.selected_index)

    @Slot()
    def __ClickedEdit(self):
        # print("編輯")
        ix = self.tableview_widget.selectionModel().selectedRows()
        # print(ix[0].row())

        dialog = WorkDiaryDialog(self.data[ix[0].row()])
        dialog.exec()

        # print("quit messagebox")

        connection = ConnectWorkDiary()
        self.data = connection.QueryData()

        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        model.horizontal_header = ["id", "日期", "品名", "規格", "數量", "單價", "金額", "備註"]
        self.tableview_widget.setModel(model)

        connection.client.close()

    @Slot()
    def __ClickedDelete(self):
        # print("刪除")
        icon = QPixmap("delete.png").scaledToHeight(45, Qt.SmoothTransformation)
        msg_box = QMessageBox()
        msg_box.setIconPixmap(icon)
        msg_box.setText("確認：")
        msg_box.setInformativeText("確認刪除")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg_box.exec()

        if result == QMessageBox.Yes:
            ix = self.tableview_widget.selectionModel().selectedRows()

            target = self.data[ix[0].row()]

            connection = ConnectWorkDiary()
            connection.DeleteData(target)

            self.data = connection.QueryData()

            df = pd.DataFrame(self.data)
            model = PandasModel(df)
            model.horizontal_header = ["id", "日期", "品名", "規格", "數量", "單價", "金額", "備註"]
            self.tableview_widget.setModel(model)

            connection.client.close()
        else:
            pass

    @Slot()
    def __ClickedExport(self):
        print("輸出")
        ix = self.tableview_widget.selectionModel().selectedRows()
        target = self.data[ix[0].row()]

        self.selected_target.append(target)

        if len(self.dialog_info) == 0:
            dialog = DiaryExportDialog(self.selected_target, self)
            self.dialog_info.append(dialog)
            # print(dialog)
            dialog.SumUp()
            dialog.show()
        else:
            print(self.dialog_info[0].isVisible())
            self.dialog_info[0].SetData(self.selected_target)

        self.dialog_info[0].finished.connect(self.__ClearLists)

    @Slot()
    def __ClearLists(self):
        self.dialog_info = []
        self.selected_target = []

        connection = ConnectWorkDiary()
        self.data = connection.QueryData()

        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        model.horizontal_header = ["id", "日期", "品名", "規格", "數量", "單價", "金額", "備註"]
        self.tableview_widget.setModel(model)

        connection.client.close()

    def FormArea(self):
        self.insert_label = QLabel("新增紀錄")
        self.insert_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.insert_label.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.summary_label = QLabel("工作紀錄： ")
        self.summary_label.setStyleSheet('font-size: 23px; color: #333; font-weight: 700')

        self.clicked_times = 0

        # self.delete_button = QPushButton(text="刪除紀錄")
        # self.delete_button.clicked.connect(self._DeleteDetail)
        # self.delete_button.setEnabled(False)

        # self.add_detail_button = QPushButton("新增紀錄")
        # self.add_detail_button.clicked.connect(self.AddDetailClicked)

        self.insert_button = QPushButton("輸入")
        self.insert_button.clicked.connect(self._DiaryInsertClicked)

        # self.scroll = self.ScrollArea()

        # self.detail_form_area = QVBoxLayout()

        self.forms = QVBoxLayout()

        self.forms.addWidget(self.insert_label)
        # self.forms.addLayout(self.SelectionArea())
        self.forms.addWidget(self.summary_label)
        self.forms.addLayout(self.WorkDiaryForm())
        # self.forms.addLayout(self.DetailForm())
        # self.forms.addWidget(self.scroll)
        # self.forms.addLayout(self.detail_form_area)

        # if not self.detail_form_area.count():
        #     self.forms.addStretch()
        # else:
        #     pass

        self.forms.addWidget(self.insert_button)
        self.forms.addStretch()
        # self.forms.addWidget(self.delete_button)
        # self.forms.addWidget(self.add_detail_button)

        return self.forms

    def WorkDiaryForm(self):
        self.date_label = QLabel("日期： ")
        self.date_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.date_edit = QDateEdit(date=today)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("background-color: #eee;")

        self.description_label = QLabel("品名： ")
        self.description_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.description_le = QLineEdit()

        self.spec_label = QLabel("規格： ")
        self.spec_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.spec_le = QLineEdit()

        self.quantity_label = QLabel("數量： ")
        self.quantity_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.quantitye_le = QLineEdit()
        # self.quantitye_le.setReadOnly(True)

        self.price_label = QLabel("單價： ")
        self.price_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.price_le = QLineEdit()
        # self.price_le.setReadOnly(True)

        self.amount_label = QLabel("金額： ")
        self.amount_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.amount_le = QLineEdit()
        # self.amount_le.setReadOnly(True)

        self.remark_label = QLabel("備註： ")
        self.remark_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.remark_le = QLineEdit()
        # self.amount_le.setReadOnly(True)

        self.work_diary_form = QFormLayout()
        self.work_diary_form.addRow(self.date_label, self.date_edit)
        self.work_diary_form.addRow(self.description_label, self.description_le)
        self.work_diary_form.addRow(self.spec_label, self.spec_le)
        self.work_diary_form.addRow(self.quantity_label, self.quantitye_le)
        self.work_diary_form.addRow(self.price_label, self.price_le)
        self.work_diary_form.addRow(self.amount_label, self.amount_le)
        self.work_diary_form.addRow(self.remark_label, self.remark_le)

        self.quantitye_le.editingFinished.connect(self.__Caculate)
        self.price_le.editingFinished.connect(self.__Caculate)

        return self.work_diary_form

    def _DiaryInsertClicked(self):
        post = {
            "date": self.date_edit.date().toString("yyyy/MM/dd"),
            "description": self.description_le.text(),
            "spec": self.spec_le.text(),
            "quantity": self.quantitye_le.text(),
            "price": self.price_le.text(),
            "amount": self.amount_le.text(),
            "remark": self.remark_le.text()
        }

        connection = ConnectWorkDiary()
        connection.InsertData(post)

        connection = ConnectWorkDiary()
        self.data = connection.QueryData()

        self._ClearForm()

        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        self.tableview_widget.setModel(model)

    def _ClearForm(self):
        self.description_le.setText("")
        self.spec_le.setText("")
        self.quantitye_le.setText("")
        self.price_le.setText("")
        self.amount_le.setText("")
        self.remark_le.setText("")

    @Slot()
    def __Caculate(self):
        if self.quantitye_le.text() != "" and self.price_le.text() != "":
            pattern = re.compile(r"\d+")
            amount = int(pattern.findall(self.quantitye_le.text())[0]) * int(self.price_le.text())
            self.amount_le.setText(str(amount))


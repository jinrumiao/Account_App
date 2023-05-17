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
from dictionary import accout_list, accounting_items, expenditure_items, revenues_items
from AccountDialogUI import AccountDialog

today = QtCore.QDate.currentDate()


class InsertTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.insert_tab_container = QHBoxLayout()
        self.insert_tab_container.addLayout(self.TableArea())
        self.insert_tab_container.addLayout(self.FormArea())

        self.setLayout(self.insert_tab_container)


    def GetData(self):
        connection = ConnectAccount()
        data = connection.QueryData()

        return data

    def TableArea(self):
        self.dialog = QDialog()

        self.data = self.GetData()

        self.table_title = QLabel("日記簿")
        self.table_title.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.tableview_widget = QTableView()
        # self.tableview_widget.horizontalHeader().setStretchLastSection(True)
        self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # set same width as tab container
        # self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableview_widget.setAlternatingRowColors(True)
        self.tableview_widget.setSelectionBehavior(QTableView.SelectRows)
        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        model.horizontal_header = ["id", "傳單編號", "日期", "摘要", "帳戶", "支出", "收入", "明細"]
        self.tableview_widget.setModel(model)

        self.tableview_widget.hideColumn(0)

        self.detail_tiltle = QLabel("明細清單： ")
        self.detail_tiltle.setStyleSheet('font-size: 20px; color: #333; font-weight: 500')

        self.tableview_details_widget = QTableView()
        # self.tableview_details_widget.horizontalHeader().setStretchLastSection(True)
        self.tableview_details_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableview_details_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableview_details_widget.setAlternatingRowColors(True)
        self.tableview_details_widget.setSelectionBehavior(QTableView.SelectRows)

        self.table = QVBoxLayout()
        self.table.addWidget(self.table_title)
        self.table.addWidget(self.tableview_widget)
        self.table.addWidget(self.detail_tiltle)
        self.table.addWidget(self.tableview_details_widget)

        self.tableview_widget.selectionModel().selectionChanged.connect(self.fetch_details)

        self.tableview_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableview_widget.customContextMenuRequested.connect(self.ContextMenu)

        return self.table

    @Slot()
    def fetch_details(self, selected):
        try:
            # ix = selected.indexes()
            # detail = ix[-1].data()

            ix = selected.indexes()[0].row()
            detail = self.data[ix]["details"]

            self.detail_tiltle.setText(f"明細清單： {self.data[ix]['serial_number']}")

            # print(type(detail))
            df_detail = pd.DataFrame(detail)
            model_detail = PandasModel(df_detail)
            model_detail.horizontal_header = ["科目代碼", "會計科目", "明細摘要", "支出明細", "收入明細"]
            self.tableview_details_widget.setModel(model_detail)
            # self.setLayout(self.table)

        except IndexError:
            pass

    def FormArea(self):
        self.insert_label = QLabel("新增記帳")
        self.insert_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.insert_label.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.summary_label = QLabel("總額： ")
        self.summary_label.setStyleSheet('font-size: 23px; color: #333; font-weight: 700')

        self.clicked_times = 0

        self.delete_button = QPushButton(text="刪除明細")
        self.delete_button.clicked.connect(self._DeleteDetail)
        self.delete_button.setEnabled(False)

        self.add_detail_button = QPushButton("新增明細")
        self.add_detail_button.clicked.connect(self.AddDetailClicked)

        self.insert_button = QPushButton("輸入")
        self.insert_button.clicked.connect(self.InsertClicked)

        self.scroll = self.ScrollArea()

        # self.detail_form_area = QVBoxLayout()

        self.forms = QVBoxLayout()

        self.forms.addWidget(self.insert_label)
        self.forms.addLayout(self.SelectionArea())
        self.forms.addWidget(self.summary_label)
        self.forms.addLayout(self.SummaryForm())
        # self.forms.addLayout(self.DetailForm())
        self.forms.addWidget(self.scroll)
        # self.forms.addLayout(self.detail_form_area)

        # if not self.detail_form_area.count():
        #     self.forms.addStretch()
        # else:
        #     pass

        self.forms.addWidget(self.delete_button)
        self.forms.addWidget(self.add_detail_button)
        self.forms.addWidget(self.insert_button)

        return self.forms

    def ScrollArea(self):
        self.detail_list = []

        self.add_clicked_times = 0

        self.widget = QWidget(self)

        self.detail_form_area = QVBoxLayout(self)

        self.widget.setLayout(self.detail_form_area)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        return self.scroll_area

    def ContextMenu(self, pos):
        context = QMenu()
        context.addAction(QIcon(qta.icon("ei.file-edit-alt")), "編輯", self.__ClickedEdit)
        context.addAction(QIcon(qta.icon("mdi.delete-circle")), "刪除", self.__ClickedDelete)
        context.setStyleSheet("font-size: 20px; color: #333; icon-size: 30px;")
        # context.setIconSize(QSize(20, 20))
        context.exec(self.mapToGlobal(pos))

    @Slot()
    def __ClickedEdit(self):
        # print("編輯")
        ix = self.tableview_widget.selectionModel().selectedRows()
        # print(ix[0].row())

        self.dialog = AccountDialog(self.data[ix[0].row()])
        self.dialog.exec()

        # print("quit messagebox")

        connection = ConnectAccount()
        self.data = connection.QueryData()

        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        model.horizontal_header = ["id", "傳單編號", "日期", "摘要", "帳戶", "支出", "收入", "明細"]
        self.tableview_widget.setModel(model)

        self.tableview_widget.selectionModel().selectionChanged.connect(self.fetch_details)

        connection.client.close()

        # print(self.data[ix])

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

            connection = ConnectAccount()
            connection.DeleteData(target)

            self.data = connection.QueryData()

            df = pd.DataFrame(self.data)
            model = PandasModel(df)
            model.horizontal_header = ["id", "傳單編號", "日期", "摘要", "帳戶", "支出", "收入", "明細"]
            self.tableview_widget.setModel(model)

            self.tableview_widget.selectionModel().selectionChanged.connect(self.fetch_details)

            connection.client.close()
        else:
            pass


    def _SerialNumber(self):
        year = today.year()
        month = today.month()
        if len(self.data) != 0:
            last_one = self.data[-1]["serial_number"]
            number = last_one[6:]
            if int(month) == int(last_one[5:6]):
                self.serial_number = f"{year}{month:0>2d}{int(number) + 1:0>4d}"
            else:
                self.serial_number = f"{year}{month:0>2d}{1:0>4d}"
        else:
            self.serial_number = f"{year}{month:0>2d}{1:0>4d}"

        return self.serial_number

    def SelectionArea(self):
        self.expenditure = QRadioButton()
        self.expenditure.setText("支出")
        self.expenditure.setAutoExclusive(True)
        self.expenditure.toggled.connect(self._ExpenditureSelected)

        self.revenues = QRadioButton()
        self.revenues.setText("收入")
        self.revenues.setAutoExclusive(True)
        self.revenues.toggled.connect(self._RevenuesSelected)

        self.selection_area = QHBoxLayout()
        self.selection_area.addWidget(self.expenditure)
        self.selection_area.addWidget(self.revenues)

        return self.selection_area

    @Slot()
    def _ExpenditureSelected(self):
        self.expenditure_le.setEnabled(True)
        self.revenues_le.setEnabled(False)

        # self.accounting_item_cb.addItems(list(expenditure_items.keys()))

        if self.detail_form_area.count() != 0:
            for i in range(self.detail_form_area.count()):
                self.detail_list[i].itemAt(5).widget().clear()
                self.detail_list[i].itemAt(5).widget().addItems(list(expenditure_items.keys()))
                self.detail_list[i].itemAt(9).widget().setEnabled(True)
                self.detail_list[i].itemAt(11).widget().setEnabled(False)

    @Slot()
    def _RevenuesSelected(self):
        self.expenditure_le.setEnabled(False)
        self.revenues_le.setEnabled(True)

        # self.accounting_item_cb.addItems(list(revenues_items.keys()))

        if self.detail_form_area.count() != 0:
            for i in range(self.detail_form_area.count()):
                self.detail_list[i].itemAt(5).widget().clear()
                self.detail_list[i].itemAt(5).widget().addItems(list(revenues_items.keys()))
                self.detail_list[i].itemAt(9).widget().setEnabled(False)
                self.detail_list[i].itemAt(11).widget().setEnabled(True)

    def SummaryForm(self):
        serial_num = self._SerialNumber()
        self.serial_number_label = QLabel(f"傳票編號：   {serial_num}")
        self.serial_number_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')

        self.date_label = QLabel("日期： ")
        self.date_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.date_edit = QDateEdit(date=today)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("background-color: #eee;")

        self.description_label = QLabel("總摘要： ")
        self.description_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.description_le = QLineEdit()

        self.account_label = QLabel("收付帳戶： ")
        self.account_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.account_le = QComboBox()
        self.account_le.addItems(accout_list)

        self.expenditure_label = QLabel("支出總額： ")
        self.expenditure_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.expenditure_le = QLineEdit()
        # self.expenditure_le.setReadOnly(True)

        self.revenues_label = QLabel("收入總額： ")
        self.revenues_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.revenues_le = QLineEdit()
        # self.revenues_le.setReadOnly(True)

        self.summary_form = QFormLayout()
        self.summary_form.addRow(self.serial_number_label)
        self.summary_form.addRow(self.date_label, self.date_edit)
        self.summary_form.addRow(self.description_label, self.description_le)
        self.summary_form.addRow(self.account_label, self.account_le)
        self.summary_form.addRow(self.expenditure_label, self.expenditure_le)
        self.summary_form.addRow(self.revenues_label, self.revenues_le)

        return self.summary_form

    def DetailForm(self):
        # self.detail_label = QLabel(f"明細{self.clicked_times}")
        # self.detail_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
        #                                 QtWidgets.QSizePolicy.Policy.Fixed)
        # self.detail_label.setStyleSheet('font-size: 18px; color: #333; font-weight: 500')
        self.detail_label = QLabel(f"明細： ")
        self.detail_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                                        QtWidgets.QSizePolicy.Policy.Fixed)
        self.detail_label.setStyleSheet('font-size: 18px; color: #333; font-weight: 500')
        self.detail_le = QLineEdit(f"{self.clicked_times}")
        self.detail_le.setEnabled(False)

        # self.code_of_accounts_label = QLabel("科目代號： ")
        # self.code_of_accounts_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        # self.code_of_accounts_le = QLineEdit(str(accounting_items[self.accounting_item_cb.currentText()]))
        # self.code_of_accounts_le.setEnabled(False)

        self.accounting_item_label = QLabel("科目名稱： ")
        self.accounting_item_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.accounting_item_cb = QComboBox()
        # self.accounting_item_cb.addItems(list(accounting_items.keys()))

        self.code_of_accounts_label = QLabel("科目代號： ")
        self.code_of_accounts_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.code_of_accounts_le = QLineEdit()
        # str(accounting_items[self.accounting_item_cb.currentText()])
        self.code_of_accounts_le.setReadOnly(True)

        self.accounting_item_cb.currentTextChanged.connect(self._TextChanged)

        self.detail_description_label = QLabel("明細摘要： ")
        self.detail_description_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.detail_description_le = QLineEdit()

        self.expenditure_details_label = QLabel("支出明細： ")
        self.expenditure_details_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.expenditure_details_le = QLineEdit()
        self.expenditure_details_le.editingFinished.connect(self._Sum)

        self.revenues_details_label = QLabel("收入明細： ")
        self.revenues_details_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.revenues_details_le = QLineEdit()
        self.revenues_details_le.editingFinished.connect(self._Sum)

        # self.delete_button = QPushButton(text="刪除明細")
        # self.delete_button.clicked.connect(self._DeleteDetail)

        self.detail_form = QFormLayout()
        # self.detail_form.addWidget(self.detail_label)
        self.detail_form.addRow(self.detail_label, self.detail_le)
        self.detail_form.addRow(self.code_of_accounts_label, self.code_of_accounts_le)
        self.detail_form.addRow(self.accounting_item_label, self.accounting_item_cb)
        self.detail_form.addRow(self.detail_description_label, self.detail_description_le)
        self.detail_form.addRow(self.expenditure_details_label, self.expenditure_details_le)
        self.detail_form.addRow(self.revenues_details_label, self.revenues_details_le)
        # self.detail_form.addRow(self.delete_button)

        self.setLayout(self.detail_form)

        return self.detail_form

    @Slot()
    def _Sum(self):
        # le = self.sender()

        if self.expenditure.isChecked():
            total = 0
            for i in range(self.detail_form_area.count()):
                add = 0 if self.detail_list[i].itemAt(9).widget().text() == "" \
                        else int(self.detail_list[i].itemAt(9).widget().text())
                total += add

            self.expenditure_le.setText(str(total))

        if self.revenues.isChecked():
            # print(f"revenues.toggled {self.revenues.isChecked()}")
            total = 0
            for i in range(self.detail_form_area.count()):
                add = 0 if self.detail_list[i].itemAt(11).widget().text() == "" \
                        else int(self.detail_list[i].itemAt(11).widget().text())
                total += add

            self.revenues_le.setText(str(total))

    @Slot()
    def _TextChanged(self, s):
        codes_items_pairs = self._FindCodele()
        # print(s)
        combo = self.sender()
        # print(f"from combo: {combo} select: {s}")
        if combo in codes_items_pairs:
            # print("Ture")
            # print(codes_items_pairs.index(combo))
            codes_items_pairs[int(codes_items_pairs.index(combo))-1].setText(
                str(accounting_items[combo.currentText()])
            )
            # print(f"from combo: {combo}, select: {s}, code: {codes_items_pairs[int(codes_items_pairs.index(combo))-1].text()}")
            # print(f"from lineedit: {codes_items_pairs[int(codes_items_pairs.index(combo))-1]}, select: {s}, code: {codes_items_pairs[int(codes_items_pairs.index(combo))-1].text()}")
        # else:
        #     print("False")
        # self.code_of_accounts_le.setText(str(accounting_items[self.accounting_item_cb.currentText()]))

    @Slot()
    def _FindCodele(self):
        if self.detail_form_area.count() != 0:
            codes_and_items = []
            for i in range(self.detail_form_area.count()):
                codes = self.detail_list[i].itemAt(3).widget()
                items = self.detail_list[i].itemAt(5).widget()
                codes_and_items.append(codes)
                codes_and_items.append(items)

            # print(codes_and_items)

        return codes_and_items

    @Slot()
    def AddDetailClicked(self):
        # print(f"detail_{self.clicked_times}")
        self.delete_button.setEnabled(True)

        self.clicked_times += 1

        self.added = self.DetailForm()

        self.detail_list.append(self.added.layout())
        # print(self.detail_list)

        self.detail_form_area.addLayout(self.added)

        self.setLayout(self.insert_tab_container)

        # if self.detail_form_area.count() is not None:
        #     self.delete_button.setEnabled(True)
        # else:
        #     self.delete_button.setEnabled(False)

    @Slot()
    def _DeleteDetail(self):
        if self.detail_form_area.count() != 0:
            # self.delete_button.setEnabled(True)
            delete_target = self.detail_list[-1]
            # print(f"delete_target: {delete_target}")
            children = []
            for i in range(delete_target.count()):
                widget = delete_target.itemAt(i).widget()
                if widget:
                    children.append(widget)
                    # print(widget)

            for widget in children:
                widget.deleteLater()

            delete_target.layout().deleteLater()

            self.detail_list.remove(delete_target)

            if len(self.detail_list) < 1:
                self.delete_button.setEnabled(False)

            self.clicked_times -= 1

    def _ClearForm(self):
        self.clicked_times = 0

        serial_num = self._SerialNumber()

        self.serial_number_label.setText(serial_num)
        self.description_le.setText("")
        # self.account_le.setText("")
        self.expenditure_le.setText("")
        self.revenues_le.setText("")

        if self.detail_form_area.count() != 0:
            for i in range(self.detail_form_area.count()):
                delete_target = self.detail_list[i]
                children = []
                for j in range(delete_target.count()):
                    widget = delete_target.itemAt(j).widget()
                    if widget:
                        children.append(widget)
                        # print(widget)

                for widget in children:
                    widget.deleteLater()
                # self.detail_form_area.itemAt(i).layout().deleteLater()
                delete_target.layout().deleteLater()

            self.detail_list = []

            self.delete_button.setEnabled(False)

    @Slot()
    def InsertClicked(self):
        # print(self.detail_form_area.count())
        # print(self.detail_form_area.itemAt(0).layout())
        # print(self.detail_form_area.itemAt(0).layout().itemAt(1).widget())
        insert_data = {
            "serial_number": self.serial_number,
            "date": self.date_edit.date().toString("yyyy/MM/dd"),
            "description": self.description_le.text(),
            "account": self.account_le.currentText(),
            "expenditure": int(self.expenditure_le.text()) if self.expenditure_le.text() != "" else self.expenditure_le.text(),
            "revenues": int(self.revenues_le.text()) if self.revenues_le.text() != "" else self.revenues_le.text(),
        }

        if self.detail_form_area.count() != 0:
            insert_data["details"] = []

            for i in range(self.detail_form_area.count()):
                # print(f"{self.detail_label.text()}{self.detail_le.text()}")
                # print(self.detail_list[i].itemAt(1).widget().text())
                detail_content = {
                    "code_of_accounts": self.detail_list[i].itemAt(3).widget().text(),
                    "accounting_item": self.detail_list[i].itemAt(5).widget().currentText(),
                    "description": self.detail_list[i].itemAt(7).widget().text(),
                    "expenditure_details":
                        int(self.detail_list[i].itemAt(9).widget().text())
                        if self.detail_list[i].itemAt(9).widget().text() != ""
                        else self.detail_list[i].itemAt(9).widget().text(),
                    "revenues_details":
                        int(self.detail_list[i].itemAt(11).widget().text())
                        if self.detail_list[i].itemAt(11).widget().text() != ""
                        else self.detail_list[i].itemAt(11).widget().text(),
                }
                insert_data["details"].append(detail_content)
        else:
            insert_data["details"] = []

        # print(self.detail_form_area.count())

        # print(insert_data)
        connection = ConnectAccount()
        connection.InsertData(insert_data)

        self.data = connection.QueryData()

        connection.client.close()

        self._ClearForm()
        self.expenditure.setChecked(False)
        self.revenues.setChecked(False)

        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        self.tableview_widget.setModel(model)

        self.tableview_widget.selectionModel().selectionChanged.connect(self.fetch_details)

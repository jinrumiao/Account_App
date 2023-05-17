import sys
import re
import pandas as pd
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QFileInfo, Qt, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QCheckBox, QApplication, QDialog, QTabWidget, QLineEdit,
                               QDialogButtonBox, QFrame, QListWidget, QGroupBox, QScrollArea, QDateEdit, QComboBox,
                               QFormLayout, QPushButton, QMessageBox, QAbstractButton, QTableView, QHeaderView,
                               QFileDialog)
import qtawesome as qta
from dictionary import accout_list, accounting_items, expenditure_items, revenues_items
from connection1 import ConnectWorkDiary
from test_pandas import PandasModel
from PDFPrinter import PDFPrinter

today = QtCore.QDate.currentDate()


class WorkDiaryDialog(QDialog):
    def __init__(self, data: dict = None, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Accounting System")
        self.resize(600, 350)
        self.setUpdatesEnabled(True)

        self.body = QVBoxLayout()

        self.data = data

        self.dialog_title = QLabel("編輯")
        self.dialog_title.setAlignment(QtCore.Qt.AlignHCenter)
        self.dialog_title.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.confirm_edit = QPushButton("確認編輯")
        self.cancel = QPushButton("取消")

        self.body.addWidget(self.dialog_title)
        self.body.addLayout(self.FormArea())
        self.body.addStretch()
        self.body.addWidget(self.confirm_edit)
        self.body.addWidget(self.cancel)
        # self.body.addStretch()

        self.setLayout(self.body)

        self.confirm_edit.clicked.connect(self.__EditSlot)
        self.cancel.clicked.connect(self.close)

    @Slot()
    def __EditSlot(self):
        self.save_button = QMessageBox.Save
        self.dont_save_button = QMessageBox.Cancel
        icon = QPixmap("edit.png").scaledToHeight(45, Qt.SmoothTransformation)
        msg_box = QMessageBox()
        msg_box.setIconPixmap(icon)
        msg_box.setText("確認：")
        msg_box.setInformativeText("是否儲存編輯內容")
        # msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.addButton(self.save_button)
        msg_box.addButton(self.dont_save_button)
        msg_box.setDefaultButton(self.dont_save_button)
        result = msg_box.exec()

        if result == QMessageBox.Save:
            print("Yes button clicked")
            new_data = self.__CollectData()
            connection = ConnectWorkDiary()
            connection.UpdateData(new_data)
            # print(new_data)
            self.close()
        else:
            print("Cancel button clicked")

    def FormArea(self):
        self.summary_label = QLabel("紀錄： ")
        self.summary_label.setStyleSheet('font-size: 23px; color: #333; font-weight: 700')

        self.forms = QVBoxLayout()

        self.forms.addWidget(self.summary_label)
        self.forms.addLayout(self.WorkDiaryForm())

        return self.forms

    # @Slot()
    def __CollectData(self):
        new_data = {
            "_id": self.data['_id'],
            "date": self.date_edit.date().toString("yyyy/MM/dd"),
            "description": self.description_le.text(),
            "spec": self.spec_le.text(),
            "quantity": self.quantitye_le.text(),
            "price": self.price_le.text(),
            "amount": self.amount_le.text(),
            "remark": self.remark_le.text()
        }

        return new_data

    def WorkDiaryForm(self):
        self.date_label = QLabel("日期： ")
        self.date_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.date_edit = QDateEdit(date=QtCore.QDate.fromString(self.data['date'], "yyyy/MM/dd"))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("background-color: #eee;")

        self.description_label = QLabel("品名： ")
        self.description_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.description_le = QLineEdit()
        self.description_le.setText(self.data["description"])

        self.spec_label = QLabel("規格： ")
        self.spec_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.spec_le = QLineEdit()
        self.spec_le.setText(self.data["spec"])

        self.quantity_label = QLabel("數量： ")
        self.quantity_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.quantitye_le = QLineEdit()
        # self.quantitye_le.setReadOnly(True)
        self.quantitye_le.setText(self.data["quantity"])

        self.price_label = QLabel("單價： ")
        self.price_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.price_le = QLineEdit()
        # self.price_le.setReadOnly(True)
        self.price_le.setText(self.data["price"])

        self.amount_label = QLabel("金額： ")
        self.amount_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.amount_le = QLineEdit()
        # self.amount_le.setReadOnly(True)
        self.amount_le.setText(str(self.data["amount"]))

        self.remark_label = QLabel("備註： ")
        self.remark_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.remark_le = QLineEdit()
        # self.amount_le.setReadOnly(True)
        self.remark_le.setText(self.data["remark"])

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

    @Slot()
    def __Caculate(self):
        if self.quantitye_le.text() != "" and self.price_le.text() != "":
            pattern = re.compile(r"\d+")
            amount = int(pattern.findall(self.quantitye_le.text())[0]) * int(self.price_le.text())
            self.amount_le.setText(str(amount))


class DiaryExportDialog(QDialog):
    def __init__(self, data: list = None, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Accounting System")
        self.resize(595, 842)
        self.setUpdatesEnabled(True)

        self.sum = QLabel("總計： \n以上金額不含5%營業稅")
        self.sum.setAlignment(QtCore.Qt.AlignRight)
        self.sum.setStyleSheet('font-size: 16px; color: #333; font-weight: 500')

        self.data = data

        self.body = QVBoxLayout()

        self.dialog_title = QLabel("輸出")
        self.dialog_title.setAlignment(QtCore.Qt.AlignHCenter)
        self.dialog_title.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')

        self.confirm_export = QPushButton("輸出")
        self.cancel = QPushButton("取消")

        self.body.addWidget(self.dialog_title)
        self.body.addLayout(self.FormArea())
        self.body.addLayout(self.TableArea())
        self.body.addWidget(self.sum)
        self.body.addWidget(self.confirm_export)
        self.body.addWidget(self.cancel)
        # self.body.addStretch()

        self.setLayout(self.body)

        self.confirm_export.clicked.connect(self.__ExportSlot)
        self.cancel.clicked.connect(self.close)

    def FormArea(self):
        self.company_name = QLabel("心富工程行")
        self.company_name.setStyleSheet('font-size: 30px; color: #333; font-weight: 700')
        self.company_name.setAlignment(QtCore.Qt.AlignHCenter)

        self.contact = QLabel("連絡電話： 0983-266-259\n地址：台中市大甲區中山里甲后路五段335巷157號")
        self.contact.setStyleSheet('font-size: 14px; color: #333; font-weight: 500')
        self.contact.setAlignment(QtCore.Qt.AlignLeft)

        self.table_title = QLabel("估價單")
        self.table_title.setStyleSheet('font-size: 25px; color: #333; font-weight: 700')
        self.table_title.setAlignment(QtCore.Qt.AlignHCenter)

        self.header = QVBoxLayout()
        self.header.addWidget(self.company_name)
        self.header.addWidget(self.contact)
        self.header.addWidget(self.table_title)

        self.customer = QLabel("客戶名稱： ")
        self.customer.setStyleSheet('font-size: 18px; color: #333; font-weight: 700')
        self.customer_le = QLineEdit()

        self.date = QLabel(f"日期： {today.toString('yyyy/MM/dd')}")
        self.date.setStyleSheet('font-size: 18px; color: #333; font-weight: 700')

        self.form = QFormLayout()
        self.form.addRow(self.customer, self.customer_le)
        self.form.addRow(self.date)

        self.estimate_container = QVBoxLayout()
        self.estimate_container.addLayout(self.header)
        self.estimate_container.addLayout(self.form)

        return self.estimate_container

    def TableArea(self):
        self.tableview_widget = QTableView()
        self.tableview_widget.horizontalHeader().setStretchLastSection(True)
        # self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # set same width as tab container
        self.tableview_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableview_widget.setAlternatingRowColors(True)
        self.tableview_widget.setSelectionBehavior(QTableView.SelectRows)
        # print(self.data)
        # df = pd.DataFrame.from_dict(self.data, orient="index").T
        df = pd.DataFrame(self.data)
        # print(df)
        model = PandasModel(df)
        model.horizontal_header = ["id", "日期", "品名", "規格", "數量", "單價", "金額", "備註"]
        self.tableview_widget.setModel(model)

        self.tableview_widget.hideColumn(0)

        self.table = QVBoxLayout()
        # self.table.addStretch()
        self.table.addWidget(self.tableview_widget)

        # self.tableview_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.tableview_widget.customContextMenuRequested.connect(self.ContextMenu)

        return self.table

    def SetData(self, new_data):
        self.data = new_data

        df = pd.DataFrame(self.data)
        model = PandasModel(df)
        model.horizontal_header = ["id", "日期", "品名", "規格", "數量", "單價", "金額", "備註"]
        self.tableview_widget.setModel(model)

        self.tableview_widget.hideColumn(0)

        self.SumUp()

    def __ExportSlot(self):
        pdf_writer = PDFPrinter()
        name = QFileDialog.getSaveFileName(None, "Save File", "", "*.pdf")

        self.dialog_title.hide()
        self.confirm_export.hide()
        self.cancel.hide()

        if name[0]:
            print(name[0])
            self.setStyleSheet("background-color: white;")
            pdf_writer.WritePDF(self, name[0])
            connection = ConnectWorkDiary()
            for i in range(len(self.data)):
                self.data[i]["remark"] = f"{today.toString('yyyy/MM/dd')}已輸出"
                connection.UpdateData(self.data[i])
            connection.client.close()
            self.close()
        else:
            pdf_writer.close()

            self.dialog_title.show()
            self.confirm_export.show()
            self.cancel.show()
            self.setStyleSheet(
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #fffaf0, stop: 1 #f8c3c1);"
            )

    def SumUp(self):
        total = 0
        for i in range(len(self.data)):
            total += int(self.data[i]["amount"])

        self.sum.setText(f"總計： {total}\n以上金額不含5%營業稅")


if __name__ == "__main__":
    from PySide6.QtWidgets import QFileDialog

    app = QApplication(sys.argv)
    connection = ConnectWorkDiary()
    data = connection.QueryData()
    display_target = data[-1]
    # print(display_target)
    dialog = DiaryExportDialog(display_target)
    dialog.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())

import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QFileInfo, Qt, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QCheckBox, QApplication, QDialog, QTabWidget, QLineEdit,
                               QDialogButtonBox, QFrame, QListWidget, QGroupBox, QScrollArea, QDateEdit, QComboBox,
                               QFormLayout, QPushButton, QMessageBox, QAbstractButton)
import qtawesome as qta
from dictionary import accout_list, accounting_items, expenditure_items, revenues_items
from connection1 import ConnectAccount

today = QtCore.QDate.currentDate()


class AccountDialog(QDialog):
    def __init__(self, data: dict = None, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Accounting System")
        self.resize(600, 900)
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
            connection = ConnectAccount()
            connection.UpdateData(new_data)
            # print(new_data)
            self.close()
        else:
            print("Cancel button clicked")

    def FormArea(self):
        self.summary_label = QLabel("總額： ")
        self.summary_label.setStyleSheet('font-size: 23px; color: #333; font-weight: 700')

        self.scroll = self.ScrollArea()

        self.forms = QVBoxLayout()

        self.forms.addWidget(self.summary_label)
        self.forms.addLayout(self.SummaryForm())

        finish_setting = False
        while not finish_setting:
            for i in range(len(self.data["details"])):
                added = self.DetailForm(i+1)
                self.detail_form_area.addLayout(added)
                self.detail_list.append(added.layout())

                if self.data['expenditure'] != "":
                    self._ExpenditureDetected()
                else:
                    self._RevenuesDetected()

                self.detail_list[i].itemAt(5).widget().currentTextChanged.connect(self._TextChanged)

            for i in range(len(self.data["details"])):
                self.detail_list[i].itemAt(3).widget().setText(self.data["details"][i]["code_of_accounts"])
                self.detail_list[i].itemAt(5).widget().setCurrentText(self.data["details"][i]["accounting_item"])
                # print(f"current text: {self.data['details'][i]['accounting_item']}")
                self.detail_list[i].itemAt(7).widget().setText(self.data["details"][i]["description"])

                if self.data['expenditure'] != "":
                    # print("expenditure")
                    self._ExpenditureDetected()
                    self.detail_list[i].itemAt(9).widget().setText(str(self.data["details"][i]["expenditure_details"]))

                else:
                    # print("revenues")
                    self._RevenuesDetected()
                    self.detail_list[i].itemAt(11).widget().setText(str(self.data["details"][i]["revenues_details"]))

            finish_setting = True

        self.forms.addWidget(self.scroll)

        return self.forms

    def ScrollArea(self):
        self.detail_list = []

        self.widget = QWidget(self)

        self.detail_form_area = QVBoxLayout(self)

        self.widget.setLayout(self.detail_form_area)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        return self.scroll_area

    # @Slot()
    def __CollectData(self):
        new_data = {
            "_id": self.data['_id'],
            "serial_number": self.data['serial_number'],
            "date": self.date_edit.date().toString("yyyy/MM/dd"),
            "description": self.description_le.text(),
            "account": self.account_le.currentText(),
            "expenditure": int(self.expenditure_le.text()) if self.expenditure_le.text() != "" else self.expenditure_le.text(),
            "revenues": int(self.revenues_le.text()) if self.revenues_le.text() != "" else self.revenues_le.text(),
        }

        if self.detail_form_area.count() != 0:
            new_data["details"] = []

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
                new_data["details"].append(detail_content)
        else:
            new_data["details"] = []

        return new_data

    def SummaryForm(self):
        self.serial_number_label = QLabel(f"傳票編號： {self.data['serial_number']}")
        self.serial_number_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')

        self.date_label = QLabel("日期： ")
        self.date_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.date_edit = QDateEdit(date=QtCore.QDate.fromString(self.data['date'], "yyyy/MM/dd"))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("background-color: #eee;")

        self.description_label = QLabel("總摘要： ")
        self.description_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.description_le = QLineEdit()
        self.description_le.setText(self.data['description'])

        self.account_label = QLabel("收付帳戶： ")
        self.account_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.account_le = QComboBox()
        self.account_le.addItems(accout_list)
        self.account_le.setCurrentText(self.data['account'])

        self.expenditure_label = QLabel("支出總額： ")
        self.expenditure_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.expenditure_le = QLineEdit()
        self.expenditure_le.setText(str(self.data['expenditure']))
        # self.expenditure_le.setReadOnly(True)

        self.revenues_label = QLabel("收入總額： ")
        self.revenues_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.revenues_le = QLineEdit()
        self.revenues_le.setText(str(self.data['revenues']))
        # self.revenues_le.setReadOnly(True)

        self.summary_form = QFormLayout()
        self.summary_form.addRow(self.serial_number_label)
        self.summary_form.addRow(self.date_label, self.date_edit)
        self.summary_form.addRow(self.description_label, self.description_le)
        self.summary_form.addRow(self.account_label, self.account_le)
        self.summary_form.addRow(self.expenditure_label, self.expenditure_le)
        self.summary_form.addRow(self.revenues_label, self.revenues_le)

        return self.summary_form

    def DetailForm(self, i):
        self.detail_label = QLabel(f"明細： ")
        self.detail_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                                        QtWidgets.QSizePolicy.Policy.Fixed)
        self.detail_label.setStyleSheet('font-size: 18px; color: #333; font-weight: 500')
        self.detail_le = QLineEdit(f"{i}")
        self.detail_le.setEnabled(False)

        self.accounting_item_label = QLabel("科目名稱： ")
        self.accounting_item_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.accounting_item_cb = QComboBox()
        # self.accounting_item_cb.addItems(list(accounting_items.keys()))

        self.code_of_accounts_label = QLabel("科目代號： ")
        self.code_of_accounts_label.setStyleSheet('font-size: 15px; color: #333; font-weight: 400')
        self.code_of_accounts_le = QLineEdit()
        # str(accounting_items[self.accounting_item_cb.currentText()])
        self.code_of_accounts_le.setReadOnly(True)

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

        # self.setLayout(self.detail_form)

        # self.accounting_item_cb.currentTextChanged.connect(self._TextChanged)

        return self.detail_form

    @Slot()
    def _ExpenditureDetected(self):
        self.expenditure_le.setEnabled(True)
        self.revenues_le.setEnabled(False)

        # self.accounting_item_cb.addItems(list(expenditure_items.keys()))

        if self.detail_form_area.count() != 0:
            for i in range(self.detail_form_area.count()):
                # print(self.detail_form_area.count())
                # self.detail_list[i].itemAt(5).widget().clear()
                self.detail_list[i].itemAt(5).widget().addItems(list(expenditure_items.keys()))
                self.detail_list[i].itemAt(9).widget().setEnabled(True)
                self.detail_list[i].itemAt(11).widget().setEnabled(False)

    @Slot()
    def _RevenuesDetected(self):
        self.expenditure_le.setEnabled(False)
        self.revenues_le.setEnabled(True)

        # self.accounting_item_cb.addItems(list(revenues_items.keys()))

        if self.detail_form_area.count() != 0:
            # print(self.detail_form_area.count())
            for i in range(self.detail_form_area.count()):
                # self.detail_list[i].itemAt(5).widget().clear()
                self.detail_list[i].itemAt(5).widget().addItems(list(revenues_items.keys()))
                self.detail_list[i].itemAt(9).widget().setEnabled(False)
                self.detail_list[i].itemAt(11).widget().setEnabled(True)

    @Slot()
    def _TextChanged(self, s):
        codes_items_pairs = self._FindCodele()
        # print(s)
        combo = self.sender()
        # print(self.detail_list)
        # print(f"第{self.times}次: {combo} / {'True' if combo == self.detail_list[0].itemAt(5).widget() else 'False'}")
        # print(f"from combo: {combo} select: {s}")
        if combo in codes_items_pairs:
            # print("Ture")
            # print(codes_items_pairs.index(combo))
            codes_items_pairs[int(codes_items_pairs.index(combo)) - 1].setText(
                str(accounting_items[combo.currentText()])
            )  # str(accounting_items[combo.currentText()])
            # print(accounting_items[combo.currentText()])

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
    def _Sum(self):
        # le = self.sender()

        if self.data['expenditure'] != "":
            total = 0
            for i in range(self.detail_form_area.count()):
                add = 0 if self.detail_list[i].itemAt(9).widget().text() == "" \
                    else int(self.detail_list[i].itemAt(9).widget().text())
                total += add

            self.expenditure_le.setText(str(total))

        if self.data['revenues'] != "":
            # print(f"revenues.toggled {self.revenues.isChecked()}")
            total = 0
            for i in range(self.detail_form_area.count()):
                add = 0 if self.detail_list[i].itemAt(11).widget().text() == "" \
                    else int(self.detail_list[i].itemAt(11).widget().text())
                total += add

            self.revenues_le.setText(str(total))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection = ConnectAccount()
    data = connection.QueryData()
    dialog = AccountDialog(data[-1])
    dialog.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())

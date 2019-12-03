import sys
import mysql.connector

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QPushButton, QApplication, QTableWidgetItem,
     QDialog, QLineEdit, QVBoxLayout,)
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIntValidator
import design


DB_NAME = 'wishlist'
TABLES = {}
TABLES['wishlist'] = (
    "CREATE TABLE `wishlist` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(40) NOT NULL UNIQUE,"
    "  `price` FLOAT NOT NULL,"
    "  `link` varchar(100) NOT NULL,"
    "  `description` varchar(50),"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

cnx = mysql.connector.connect(user='wishlist', password='wishlist')
cursor = cnx.cursor()


def create_database():
    print("FUNC CREATE")
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


def add_wish(name, price, link, description=""):
    add_wish = ("INSERT INTO wishlist "
                   "(name, price, link, description) "
                   "VALUES (%s, %s, %s, %s)")
    data_wish = (name, price, link, description)
    cursor.execute(add_wish, data_wish)
    cnx.commit()


def update_wish(name, price, link, description, name_old, price_old, link_old, description_old):
    update_wish = ("UPDATE wishlist "
                   "SET name=%s, price=%s, link=%s, description=%s "
                   "WHERE name=%s AND price=%s AND link=%s AND description=%s")
    data_wish = (name, price, link, description, name_old, price_old, link_old, description_old)
    cursor.execute(update_wish, data_wish)
    cnx.commit()


def delete_wish(name):
    delete_wish = ("DELETE FROM wishlist WHERE name = %s")
    cursor.execute(delete_wish, (name, ))
    cnx.commit()


def get_wishes():
    query = ("SELECT name, price, link, description FROM wishlist")
    cursor.execute(query)

    res = []
    for (name, price, link, description) in cursor:
        res.append([name, str(price), link, description])
    return res


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.wish_name = QLineEdit("Wish name")
        self.wish_price = QLineEdit("100")
        self.onlyInt = QIntValidator()
        self.wish_price.setValidator(self.onlyInt)
        self.wish_link = QLineEdit("Wish link")
        self.wish_desc = QLineEdit("Wish desc")
        self.button = QPushButton("Add wish")
        layout = QVBoxLayout()
        layout.addWidget(self.wish_name)
        layout.addWidget(self.wish_price)
        layout.addWidget(self.wish_link)
        layout.addWidget(self.wish_desc)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.button.clicked.connect(self.add)


    def add(self):
        self.accept()


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnDelete.clicked.connect(self.delete)
        self.btnAdd.clicked.connect(self.add)
        self.btnEdit.clicked.connect(self.edit)
        self.tableWidget.cellClicked.connect(self.selectRow)
        self.fill_wishes()


    def fill_wishes(self):
        wishes = get_wishes()
        self.tableWidget.setRowCount(len(wishes))
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Price", "Link", "Description"])
        row = 0
        for wish in wishes:
            col = 0
            for col in range(len(wish)):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setText(wish[col])
                self.tableWidget.setItem(row, col, item);
                col += 1
            row += 1
        self.tableWidget.setColumnWidth(0, 170)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 280)


    def selectRow(self):
        index = self.tableWidget.selectionModel().selectedRows()


    def delete(self):
        items = self.tableWidget.selectedItems()
        data = []
        for item in items:
            data.append(item.text())

        if data:
            index = self.tableWidget.selectionModel().selectedRows()
            name = index[0].data()

            delete_wish(name)
            self.tableWidget.removeRow(index[0].row())


    def add(self):
        dlg = Form(self)
        dlg.setWindowTitle("Add new wish!")

        if dlg.exec_():
            name = dlg.wish_name.text()
            price = dlg.wish_price.text()
            link = dlg.wish_link.text()
            desc = dlg.wish_desc.text()

            try:
                add_wish(name, price, link, desc)
            except mysql.connector.IntegrityError as err:
                print("Error: {} {} {} ".format(err, type(err), err.args))
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Wish name should be unique. Please choose another name')
                error_dialog.exec_()
            self.fill_wishes()


    def edit(self):
        items = self.tableWidget.selectedItems()
        data = []
        for item in items:
            data.append(item.text())

        if data:
            dlg = Form(self)
            dlg.wish_name.setText(data[0])
            dlg.wish_price.setText(data[1])
            dlg.wish_link.setText(data[2])
            dlg.wish_desc.setText(data[3])
            dlg.setWindowTitle("Update your wish!")
            dlg.button.setText("Edit")


            if dlg.exec_():
                name = dlg.wish_name.text()
                price = dlg.wish_price.text()
                link = dlg.wish_link.text()
                desc = dlg.wish_desc.text()
                update_wish(name, price, link, desc, data[0], data[1], data[2], data[3])
                self.fill_wishes()


def main():
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("TRYING TO CREATE DATABASE")
            create_database()
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    main()
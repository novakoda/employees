
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, 
    QTableWidgetItem, QVBoxLayout, QHeaderView
)
import psycopg2
import datetime
import sys

class Window(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("PyQt6 SpreadSheet")
        self.CreateTable()
        self.resize(400, 250)
        self.show()

    def CreateTable(self):
        self.table = QTableWidget(len(self.data), 5)
        self.table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team #"])

        for i, emp in enumerate(self.data):
            self.table.setItem(i,0, QTableWidgetItem(str(emp[0])))
            self.table.setItem(i,1, QTableWidgetItem(str(emp[1])))
            self.table.setItem(i,2, QTableWidgetItem(str(emp[2])))
            self.table.setItem(i,3, QTableWidgetItem(str(emp[3])))
            self.table.setItem(i,4, QTableWidgetItem(str(emp[4])))
        self.table.resizeColumnsToContents()
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.table)
        self.setLayout(self.vBox)

    def addItem(self, item, row, col):
        newitem = QtWidgets.QTableWidgetItem(str(item))
        self.setItem(row, col, newitem)

if __name__ == "__main__":
    app = QApplication(sys.argv)
        # connect to postgres
    try:
        conn = psycopg2.connect(database = "d36rgsamtnofbn", user = "jwwhxzjhgnjkcy", password = "54214aacd5940c8df5e58763635b2945441b946ce69116e903cdcc4f8200f922", host = "ec2-3-217-251-77.compute-1.amazonaws.com")
    except:
        print('Unable to connect to the database')
        sys.exit(1)

    # open a cursor to perform db operations
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees;")
    emp_list = cur.fetchall()
    # emp_data = sqlToData(emp_list)
    # print(emp_list)

    win = Window(emp_list)
    win.show()
    sys.exit(app.exec())
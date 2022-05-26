
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, 
    QTableWidgetItem, QVBoxLayout, QGridLayout, QHeaderView, QMainWindow
)
import psycopg2
import datetime
import sys

class UserInterface(QMainWindow):
    def __init__(self, data):
        super(UserInterface, self).__init__()
        self.table = EmployeeTable(data)
        self.setWindowTitle("CAPS Employees")
        self.resize(800, 400)
        self.widget = QWidget(self)
        layout = QGridLayout()
        self.widget.setLayout(layout)
        layout.addWidget(self.table)
        self.setCentralWidget(self.table)
        # self.resize(self.sizeHint())

class EmployeeTable(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.table()

    def table(self):
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team #"])
        for i, emp in enumerate(self.data):
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0])))
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2])))
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1])))
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3])))
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4])))
        self.tableWidget.resizeColumnsToContents()


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

    win = UserInterface(emp_list)
    win.show()
    
    sys.exit(app.exec())
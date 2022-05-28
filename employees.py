
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, 
    QTableWidgetItem, QVBoxLayout, QGridLayout, QHeaderView, QMainWindow, QLabel, QPushButton
)
import psycopg2
from datetime import date, timedelta
import sys

class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.table = EmployeeTable()
        self.positions = PositionInfo()
        self.setWindowTitle("CAPS Employees")
        self.resize(800, 400)
        self.widget = QWidget(self)
        layout = QVBoxLayout()
        self.widget.setLayout(layout)
        layout.addWidget(self.table)
        layout.addWidget(self.positions)
        self.setCentralWidget(self.widget)
        self.positions.empl_btn.clicked.connect(self.show_employee_form)
        # self.resize(self.sizeHint())

    def show_employee_form(self):
        self.table.hide()
        self.positions.hide()

class EmployeeTable(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM employees;")
        self.data = cur.fetchall()
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

class PositionInfo(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        self.grid()

    def grid(self):
        self.get_position_counts()
        self.label_data()
        self.layout = QGridLayout()
        self.data_btn = QPushButton("Edit Positions", self)
        self.empl_btn = QPushButton("New Employee", self)
        self.layout.addWidget(self.data_btn, 0, 0)
        self.layout.addWidget(self.empl_btn, 1, 0)
        self.layout.addWidget(self.total, 0, 1)
        self.layout.addWidget(self.open, 0, 2)
        self.layout.addWidget(self.upcoming, 1, 1)
        self.layout.addWidget(self.promotions, 1, 2)
        self.setLayout(self.layout)
        self.show()

    def label_data(self):
        self.total = QLabel("Total Positions : %s" % self.data[1])
        self.open = QLabel("Open Positions : %s" % self.data[2])
        self.upcoming = QLabel("Upcoming Openings : %s" % self.yellow_count)
        self.promotions = QLabel("Pending Promotions : %s" % self.red_count)

    def get_position_counts(self):
        nine_ago = date.today() - timedelta(days=274)
        year_ago = date.today() - timedelta(days=365)
        cur.execute("""
        SELECT COUNT(*) FROM employees WHERE
            start_date <= %s AND start_date > %s
        """, (nine_ago, year_ago))
        yellow_count = cur.fetchone()
        self.yellow_count = yellow_count[0]
        cur.execute("SELECT COUNT(*) FROM employees WHERE start_date < %s", (year_ago,))
        red_count = cur.fetchone()
        self.red_count = red_count[0]

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
    win = UserInterface()
    win.show()
    
    sys.exit(app.exec())
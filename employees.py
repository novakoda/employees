
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QGridLayout, QHeaderView, QMainWindow, QLabel, QPushButton, QGroupBox, QFormLayout, QLineEdit, QDateEdit, QCheckBox, QTabWidget
)

from PyQt6.QtGui import QColor

from PyQt6.QtCore import (
    QDate, Qt
)

import psycopg2
from datetime import date, timedelta
import sys

class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.table = EmployeeTable()
        self.tabs.addTab(self.table, "Active Employees")
        self.promoted_table = PromotedTable()
        self.tabs.addTab(self.promoted_table, "Promoted Employees")
        self.inactive_table = InactiveTable()
        self.tabs.addTab(self.inactive_table, "Inactive Employees")

        self.positions = PositionInfo()
        self.pos_form = PositionForm()
        self.emp_form = EmployeeForm()

        self.setWindowTitle("CAPS Employees")
        self.resize(700, 700)

        self.widget = QWidget(self)
        self.box_layout = QVBoxLayout()
        self.widget.setLayout(self.box_layout)
        self.box_layout.addWidget(self.tabs)
        self.box_layout.addWidget(self.positions)
        self.box_layout.addWidget(self.emp_form)
        self.box_layout.addWidget(self.pos_form)
        self.setCentralWidget(self.widget)

        self.positions.empl_btn.clicked.connect(self.show_employee_form)
        self.positions.data_btn.clicked.connect(self.show_position_form)
        self.emp_form.back_btn.clicked.connect(self.show_employee_table)
        self.pos_form.back_btn.clicked.connect(self.show_employee_table)
        # self.resize(self.sizeHint())

    def show_employee_table(self):
        self.emp_form.hide()
        self.pos_form.hide()
        self.tabs.show()
        self.positions.show()
        self.positions.empl_btn.clicked.connect(self.show_employee_form)
        self.positions.data_btn.clicked.connect(self.show_position_form)

    def show_employee_form(self, emp=None):
        self.tabs.hide()
        self.positions.hide()
        self.pos_form.hide()
        self.emp_form.display(emp)

    def show_position_form(self):
        self.emp_form.hide()
        self.tabs.hide()
        self.positions.hide()
        self.pos_form.display()

class EmployeeTable(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM employees WHERE promoted <> TRUE AND inactive <> TRUE;")
        self.data = cur.fetchall()
        self.table()

    def table(self):
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    def update(self):
        cur.execute("SELECT * FROM employees WHERE promoted <> TRUE AND inactive <> TRUE;")
        self.data = cur.fetchall()
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.createTable()
        self.layout.addWidget(self.tableWidget)


    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 6)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team #", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0])))
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1])))
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2])))
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3])))
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4])))
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            self.tableWidget.setCellWidget(i,5, edit_button)

            self.tableWidget.item(i, 3).setBackground(QColor(self.date_colors(emp[3])))

    def date_colors(self, emp_date):
        days = (date.today() - emp_date).days
        if days >= 274:
            if days >= 365:
                return "Red"
            return "Yellow"
        return "White"

        self.tableWidget.resizeColumnsToContents()
class PromotedTable(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM employees WHERE promoted <> FALSE AND inactive <> TRUE;")
        self.data = cur.fetchall()
        self.table()

    def table(self):
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    def update(self):
        cur.execute("SELECT * FROM employees WHERE promoted <> FALSE AND inactive <> TRUE;")
        self.data = cur.fetchall()
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.createTable()
        self.layout.addWidget(self.tableWidget)

    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 7)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team #", "Promotion Date", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0])))
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2])))
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1])))
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3])))
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4])))
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[6])))
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            self.tableWidget.setCellWidget(i,6, edit_button)

        self.tableWidget.resizeColumnsToContents()

class InactiveTable(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM employees WHERE inactive <> FALSE;")
        self.data = cur.fetchall()
        self.table()

    def table(self):
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    def update(self):
        cur.execute("SELECT * FROM employees WHERE inactive <> FALSE;")
        self.data = cur.fetchall()
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.createTable()
        self.layout.addWidget(self.tableWidget)

    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 7)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team #", "Inactive Date", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0])))
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2])))
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1])))
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3])))
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4])))
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[8])))
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            self.tableWidget.setCellWidget(i,6, edit_button)

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
        self.upcoming.setStyleSheet("background-color: yellow;")
        self.promotions = QLabel("Pending Promotions : %s" % self.red_count)
        self.promotions.setStyleSheet("background-color: red;")

    def get_position_counts(self):
        nine_ago = date.today() - timedelta(days=274)
        year_ago = date.today() - timedelta(days=365)
        cur.execute("""
        SELECT COUNT(*) FROM employees WHERE
            start_date <= %s AND start_date > %s AND promoted <> TRUE AND inactive <> TRUE;
        """, (nine_ago, year_ago))
        yellow_count = cur.fetchone()
        self.yellow_count = yellow_count[0]
        cur.execute("SELECT COUNT(*) FROM employees WHERE start_date < %s AND promoted <> TRUE AND inactive <> TRUE;", (year_ago, ))
        red_count = cur.fetchone()
        self.red_count = red_count[0]

    def update(self):
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.get_position_counts()
        self.label_data()
        self.data_btn = QPushButton("Edit Positions", self)
        self.empl_btn = QPushButton("New Employee", self)
        self.layout.addWidget(self.data_btn, 0, 0)
        self.layout.addWidget(self.empl_btn, 1, 0)
        self.layout.addWidget(self.total, 0, 1)
        self.layout.addWidget(self.open, 0, 2)
        self.layout.addWidget(self.upcoming, 1, 1)
        self.layout.addWidget(self.promotions, 1, 2)


class PositionForm(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        self.form()

    def form(self):
        self.layout = QFormLayout()
        self.total = QLineEdit()
        self.layout.addRow(QLabel("Total Positions: "), self.total)
        self.open = QLineEdit()
        self.layout.addRow(QLabel("Open Positions: "), self.open)

        self.back_btn = QPushButton("Back", self)
        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.clicked.connect(self.submit)
        self.layout.addRow(self.back_btn, self.submit_btn)
        self.setLayout(self.layout)
        self.hide()

    def update(self):
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        self.total.setText(str(self.data[1]))
        self.open.setText(str(self.data[2]))

    def display(self):
        self.update()
        self.show()

    def submit(self):
        try:
            pos_sql = """UPDATE positions SET (total, open) = (%s::int, %s::int) WHERE pos_id = True"""
            cur.execute(pos_sql, (self.total.text(), self.open.text()))
        except Exception as ex:
            print(ex)
        conn.commit()
        win.positions.update()
        win.show_employee_table()

class EmployeeForm(QWidget):
    def __init__(self, emp=(None,'','', date.today(), None, False, date.today(), False, date.today())):
        super().__init__()
        self.emp = emp
        self.form()
        # self.display()

    def display(self, emp=None):
        if not emp:
            self.emp = ('','','', date.today(), '', False, date.today(), False, date.today())
        else:
            self.emp = emp
        self.update() 
        self.show()

    def form(self):
        self.layout = QFormLayout()
        self.emp_id = QLineEdit()
        self.layout.addRow(QLabel("Employee ID: "), self.emp_id)
        self.first = QLineEdit()
        self.layout.addRow(QLabel("First Name: "), self.first)
        self.last = QLineEdit()
        self.layout.addRow(QLabel("Last Name: "), self.last)
        self.team = QLineEdit()
        self.layout.addRow(QLabel("Team Number: "), self.team)
        self.start = QDateEdit(calendarPopup=True, displayFormat="yyyy-MM-dd")
        self.layout.addRow(QLabel("Start Date: "), self.start)

        self.promoted = QCheckBox()
        self.layout.addRow(QLabel("Promoted: "), self.promoted)
        self.promoted.stateChanged.connect(self.promotedClick)
        self.promoted_date = QDateEdit(calendarPopup=True, displayFormat="yyyy-MM-dd")
        self.layout.addRow(QLabel("Promotion Date: "), self.promoted_date)

        self.inactive = QCheckBox()
        self.layout.addRow(QLabel("Inactive: "), self.inactive)
        self.inactive.stateChanged.connect(self.inactiveClick)
        self.inactive_date = QDateEdit(calendarPopup=True, displayFormat="yyyy-MM-dd")
        self.layout.addRow(QLabel("Inactive Date: "), self.inactive_date)

        self.back_btn = QPushButton("Back", self)
        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.clicked.connect(self.submit_form)

        self.layout.addRow(self.back_btn, self.submit_btn)
        self.setLayout(self.layout)
        self.hide()

    def submit_form(self):
        eid = self.emp_id.text()
        f_name = self.first.text()
        l_name = self.last.text()
        team = self.team.text()
        start = self.start.text()
        promoted = "TRUE" if self.promoted.isChecked() else "FALSE"
        promoted_date = "1000-01-01" if not self.promoted.isChecked() else self.promoted_date.text()

        inactive = "TRUE" if self.inactive.isChecked() else "FALSE"
        inactive_date = "1000-01-01" if not self.inactive.isChecked() else self.inactive_date.text()

        print(eid, f_name, l_name, start, team,promoted, promoted_date, inactive, inactive_date)

        try:
            employee_sql = '''
                INSERT INTO employees (id, first_name, last_name, start_date, team, promoted, promoted_date, inactive, inactive_date)
                VALUES (%s::int,%s, %s, %s, NULLIF(%s,'')::int, %s, NULLIF(%s,'1000-01-01')::date, %s, NULLIF(%s,'1000-01-01')::date)
                ON CONFLICT (id) DO UPDATE SET
                (first_name, last_name, start_date, team, promoted, promoted_date, inactive, inactive_date) = (EXCLUDED.first_name, EXCLUDED.last_name, EXCLUDED.start_date, EXCLUDED.team, EXCLUDED.promoted, EXCLUDED.promoted_date, EXCLUDED.inactive, EXCLUDED.inactive_date);
            '''

            cur.execute(employee_sql, (eid, f_name, l_name, start, team,promoted, promoted_date, inactive, inactive_date))
        except Exception as ex:
            print(ex)

        conn.commit()
        win.table.update()
        win.promoted_table.update()
        win.inactive_table.update()
        win.show_employee_table()
    
    def inactiveClick(self, state):
        if state == 0:
            self.inactive_date.setDisabled(True)
        else:
            self.inactive_date.setDisabled(False)

    def promotedClick(self, state):
        if state == 0:
            self.promoted_date.setDisabled(True)
        else:
            self.promoted_date.setDisabled(False)


    def update(self):
        if self.emp:
            self.emp_id.setText(str(self.emp[0]))
            self.first.setText(self.emp[1])
            self.last.setText(self.emp[2])
            self.team.setText(str(self.emp[4]))
            self.start.setDate(QDate.fromString(str(self.emp[3]), "yyyy-MM-dd"))
            
            if not self.emp[5]:
                self.promoted.setChecked(False)
                self.promoted_date.setDisabled(True)
            else:
                self.promoted.setChecked(True)
                self.promoted_date.setDate(QDate.fromString(str(self.emp[6]), "yyyy-MM-dd"))
            
            if not self.emp[7]:
                self.inactive.setChecked(False)
                self.inactive_date.setDisabled(True)
            else:
                self.inactive.setChecked(True)
                self.inactive_date.setDate(QDate.fromString(str(self.emp[8]), "yyyy-MM-dd"))

def create_db():
    try:
        cur.execute("""
        DROP TABLE IF EXISTS employees CASCADE;
        DROP TABLE IF EXISTS positions CASCADE;
        CREATE TABLE employees (
            id INT PRIMARY KEY NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            start_date DATE NOT NULL,
            team INT,
            promoted BOOLEAN,
            promoted_date DATE,
            inactive BOOLEAN,
            inactive_date DATE
        );
        CREATE TABLE positions (
            pos_id bool PRIMARY KEY DEFAULT TRUE,
            total INT NOT NULL,
            open INT NOT NULL,
            CONSTRAINT one_row_pos CHECK (pos_id)
        );
        REVOKE DELETE, TRUNCATE ON positions FROM public;
        INSERT INTO employees (id, first_name, last_name, start_date, team, promoted, promoted_date, inactive, inactive_date) VALUES (1084321,'Rabia','Suleiman','2022-03-13', 1, FALSE, NULL, FALSE, NULL), 
        (762256,'Isaac','Newton','2021-06-13', 1, FALSE, NULL, FALSE, NULL), 
        (9396393,'Nikola','Tesla','2021-05-27', 33, FALSE, NULL, FALSE, NULL), 
        (3620196,'Elon','Musk','2020-03-22', 33, FALSE, NULL, TRUE, '2022-01-11'), 
        (322113,'Steve','Jobs','2020-11-22', 2, TRUE, '2021-08-11', FALSE, NULL), 
        (4534234,'Hakeem','Olajuwon','2021-07-09', 34, FALSE, NULL, FALSE, NULL), 
        (8821332,'Sigmund','Freud','2021-10-22', 3, FALSE, NULL, TRUE, '2022-07-13'), 
        (2512093,'Martha','Steward','2021-10-22', 5, FALSE, NULL, FALSE, NULL), 
        (554216,'Taylor','Swift','2022-02-22', 22, TRUE, '2022-06-01', FALSE, NULL), 
        (9982109,'Michael','Jordan','2021-01-03', 23, FALSE, NULL, FALSE, NULL), 
        (240824,'Kobe','Bryant','2008-08-24', 24, FALSE, NULL, TRUE, '2020-02-04'), 
        (1024954,'Lebron','James','2021-08-04', 23, FALSE, NULL, FALSE, NULL); 
        INSERT INTO positions (total, open) VALUES (0, 0)
        """)
    except Exception as ex:
        print(ex)

    conn.commit()

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
    # create_db()
    win = UserInterface()
    win.show()
    
    sys.exit(app.exec())
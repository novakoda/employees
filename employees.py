from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QGridLayout, QHeaderView, QMainWindow, QLabel, QPushButton, QFormLayout, QLineEdit, QDateEdit, QCheckBox, QTabWidget, QAbstractItemView, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QColor, QTextDocument, QIntValidator, QPageLayout, QIcon
from PyQt6.QtCore import QDate, QSize, QMarginsF, QFileInfo
from PyQt6.QtPrintSupport import QPrinter
import psycopg2
import urllib.parse as urlparse
from datetime import date, timedelta
import os
import sys

class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('aclogo.png'))
        self.tabs = QTabWidget()
        self.table = EmployeeTable()
        self.tabs.addTab(self.table, "Active")
        self.promoted_table = PromotedTable()
        self.tabs.addTab(self.promoted_table, "Transitioned")
        self.inactive_table = InactiveTable()
        self.tabs.addTab(self.inactive_table, "Inactive")

        self.emp_form = EmployeeForm()
        self.positions = PositionInfo()
        self.pos_form = PositionForm()

        self.setWindowTitle("CAPS Employees")
        self.resize(1080, 680)
        self.showMaximized() 

        self.widget = QWidget(self)
        self.box_layout = QVBoxLayout()
        self.widget.setLayout(self.box_layout)
        self.box_layout.addWidget(self.tabs)
        self.box_layout.addWidget(self.positions)
        self.box_layout.addWidget(self.emp_form)
        self.box_layout.addWidget(self.pos_form)
        self.setCentralWidget(self.widget)

        self.positions.grid()

        self.positions.empl_btn.clicked.connect(self.show_employee_form)
        self.positions.data_btn.clicked.connect(self.show_position_form)
        self.positions.print_btn.clicked.connect(self.print_info)
        self.emp_form.back_btn.clicked.connect(self.show_employee_table)
        self.pos_form.back_btn.clicked.connect(self.show_employee_table)
        self.setStyleSheet("QTableWidget { selection-color: palette(text); selection-background-color: palette(base); }")


    def show_employee_table(self, pos_submit=False):
        self.emp_form.hide()
        self.pos_form.hide()
        self.tabs.show()
        self.positions.show()
        if pos_submit:
            self.positions.empl_btn.clicked.connect(self.show_employee_form)
            self.positions.data_btn.clicked.connect(self.show_position_form)
            self.positions.print_btn.clicked.connect(self.print_info)

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

    def print_info(self):
        global red_count, yellow_count
        dialog = QFileDialog()
        fileName, _ = dialog.getSaveFileName(self, "Save as PDF", None, "PDF files (*.pdf);;All files(*)")
        if fileName != '':
            if QFileInfo(fileName).suffix() == '' : dialog += '.pdf'

            tab = self.tabs.currentIndex()
            if tab == 0:
                table = self.table.tableWidget
                word = "Current"
            elif tab == 1:
                table = self.promoted_table.tableWidget
                word = "Transitioned"
            elif tab == 2:
                table = self.inactive_table.tableWidget
                word = "Inactive"

            self.printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
            self.printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            self.printer.setPageMargins(QMarginsF(15,15,15,15), QPageLayout.Unit.Point)
            self.printer.setOutputFileName(fileName)

            doc = QTextDocument()

            html = """
            <html>
                <head>
                    <style>
                        table, thead, td {
                            border: 1px solid black;
                            padding: 5px;
                            border-collapse: collapse;
                        }

                        table {
                            margin: 8px 0px 0px 0px;
                        }

                        p {
                            margin: 3px 0px 3px 0px;
                            font-size: 10px;
                        }
                    </style>
                </head>
                <h3>
            """
            html += word

            html += " Employees List</h3>"
            html += ("""<div>
                            <p class="data">Total Positions : %s</p>
                            <p class="data">Open Positions : %s</p>
                            <p class="data">Upcoming Openings : %s</p>
                            <p class="data">Pending Promotions : %s</p>
                        </div>
                        """ % (self.positions.data[1], self.positions.data[2], yellow_count, red_count))

            html += "<table><thead><tr>"
            for c in range(table.columnCount() - 1):
                html += "<td>{}</td>".format(table.horizontalHeaderItem(c).text())

            html += """
                        </tr>
                    </thead>
                    <tbody>
                    """

            for r in range(table.rowCount()):
                html += "<tr>"
                for c in range(table.columnCount() - 1):
                    html += "<td>{}</td>".format(table.item(r, c).text() or '')
                html += "</tr>"

            html += """
                    </tbody>
                </table>
            """

            doc.setHtml(html)
            doc.setPageSize(self.printer.pageRect(QPrinter.Unit.Point).size())
            doc.print(self.printer)

class TableDad(QWidget):
    def __init__(self, sql):
        super().__init__()
        self.sql = sql
        cur.execute(self.sql)
        data = cur.fetchall()
        data_clone = []
        for row in data:
            row_data = tuple(map(lambda x: x if x is not None else '', row))
            data_clone.append(row_data)
        data_clone.sort(key=lambda emp: emp[3])
        self.data = data_clone
        self.table()

    def table(self):
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    def update(self):
        cur.execute(self.sql)
        data = cur.fetchall()
        data_clone = []
        for row in data:
            row_data = tuple(map(lambda x: x if x is not None else '', row))
            data_clone.append(row_data)
        data_clone.sort(key=lambda emp: emp[3])
        self.data = data_clone
        self.refresh()

    def refresh(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.createTable()
        self.layout.addWidget(self.tableWidget)

    def arrange(self, col):
        if all(self.data[e][col] <= self.data[e + 1][col] for e in range(len(self.data)-1)):
            self.data.sort(key=lambda emp: (emp[col] is None, emp[col]), reverse=True)
        else:
            self.data.sort(key=lambda emp: (emp[col] is None, emp[col]))

    def onHeaderClicked(self, dataIndex):
        # Active
        if self.data and (dataIndex <= 4 or (dataIndex == 5 and self.data[0][9] == False) or \
            (dataIndex == 6 and self.data[0][9] == False)):
            self.arrange(dataIndex)
        # Inactive
        elif dataIndex == 5 and self.data and self.data[0][9] == True:
            pos_ids = []
            for emp in self.data:
                pos_ids.append(0 if emp[5] == '' else emp[5])
            if all(pos_ids[e] <= pos_ids[e + 1] for e in range(len(pos_ids)-1)):
                self.data.sort(key=lambda emp: (emp[5] == '', emp[5]))
            else:
                self.data.sort(key=lambda emp: (emp[5] == '', emp[5]), reverse=True)
        elif dataIndex == 6 and self.data and self.data[0][9] == True:
            self.arrange(10)
        # Promoted
        elif dataIndex == 7 and self.data and self.data[0][7] == True and self.data[0][9] == False:
            self.arrange(8)
        self.refresh()

class EmployeeTable(TableDad):
    def __init__(self):
        super().__init__("SELECT * FROM employees WHERE promoted <> TRUE AND inactive <> TRUE;")

    def createTable(self):
        global red_count, yellow_count
        red_count = 0
        yellow_count = 0
        self.tableWidget = QTableWidget(len(self.data), 8)
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team", "Pos #", "Supervisor", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0]))) # ID
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1]))) # First Name
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2]))) # Last Name
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3]))) # Start Date
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4]))) # Team
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[5]))) # Position
            self.tableWidget.setItem(i,6, QTableWidgetItem(str(emp[6]))) # Supervisor
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            edit_button.setFixedSize(QSize(40,30))
            self.tableWidget.setCellWidget(i,7, edit_button)
            self.tableWidget.item(i, 3).setBackground(QColor(self.date_colors(emp)))
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(7, 40)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header.sectionClicked.connect(self.onHeaderClicked)

    def date_colors(self, emp):
        global red_count, yellow_count
        days = (date.today() - emp[3]).days + (emp[11] * 30)
        if days >= 274:
            if days >= 365:
                red_count += 1
                return "Red"
            yellow_count += 1
            return "Yellow"
        return "White"

class PromotedTable(TableDad):
    def __init__(self):
        super().__init__("SELECT * FROM employees WHERE promoted <> FALSE AND inactive <> TRUE;")

    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 9)
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team", "Pos #", "Supervisor", "Promotion Date", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0]))) # ID
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1]))) # First Name
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2]))) # Last Name
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3]))) # Start Date
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4]))) # Team
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[5]))) # Position
            self.tableWidget.setItem(i,6, QTableWidgetItem(str(emp[6]))) # Supervisor
            self.tableWidget.setItem(i,7, QTableWidgetItem(str(emp[8]))) # Promoted Date
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            edit_button.setFixedSize(QSize(40,30))
            self.tableWidget.setCellWidget(i,8, edit_button)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(8, 40)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header.sectionClicked.connect(self.onHeaderClicked)

class InactiveTable(TableDad):
    def __init__(self):
        super().__init__("SELECT * FROM employees WHERE inactive <> FALSE;")
        
    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 8)
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team", "Position", "Inactive Date", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0]))) # ID
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1]))) # First Name
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2]))) # Last Name
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3]))) # Start Date
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4]))) # Team
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[5]))) # Position
            self.tableWidget.setItem(i,6, QTableWidgetItem(str(emp[10]))) # Inactive Date
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            edit_button.setFixedSize(QSize(40,30))
            self.tableWidget.setCellWidget(i,7, edit_button)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(7, 40)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header.sectionClicked.connect(self.onHeaderClicked)

class PositionInfo(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        # self.grid()

    def grid(self):
        self.layout = QGridLayout()
        self.populate_grid()
        self.setLayout(self.layout)
        self.show()

    def label_data(self):
        self.total = QLabel("Total Positions : %s" % self.data[1])
        self.open = QLabel("Open Positions : %s" % self.data[2])
        self.upcoming = QLabel("Upcoming Openings : %i" % yellow_count)
        self.upcoming.setStyleSheet("""background-color: yellow;
                                        padding: 2px;""")
        self.promotions = QLabel("Pending Promotions : %i" % red_count)
        self.promotions.setStyleSheet("""background-color: red;
                                        padding: 2px;""")

    def populate_grid(self):
        self.label_data()
        self.data_btn = QPushButton("Edit Positions", self)
        self.empl_btn = QPushButton("New Employee", self)
        self.print_btn = QPushButton("Save as PDF", self)

        self.data_btn.setFixedSize(QSize(100,30))
        self.empl_btn.setFixedSize(QSize(100,30))
        self.print_btn.setFixedSize(QSize(100,30))
        self.total.setFixedSize(QSize(200,30))
        self.open.setFixedSize(QSize(200,30))
        self.upcoming.setFixedSize(QSize(140,30))
        self.promotions.setFixedSize(QSize(140,30))

        self.layout.addWidget(self.data_btn, 0, 0)
        self.layout.addWidget(self.empl_btn, 1, 0)
        self.layout.addWidget(self.total, 0, 1)
        self.layout.addWidget(self.open, 0, 2)
        self.layout.addWidget(self.upcoming, 1, 1)
        self.layout.addWidget(self.promotions, 1, 2)
        self.layout.addWidget(self.print_btn, 0, 3)

    def update(self):
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.populate_grid()

class PositionForm(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        self.form()

    def form(self):
        self.layout = QFormLayout()
        self.total = QLineEdit()
        total_valid = QIntValidator(self.total)
        self.total.setValidator(total_valid)
        self.layout.addRow(QLabel("Total Positions: "), self.total)
        self.open = QLineEdit()
        open_valid = QIntValidator(self.open)
        self.open.setValidator(open_valid)
        self.layout.addRow(QLabel("Open Positions: "), self.open)

        self.back_btn = QPushButton("Back", self)
        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.clicked.connect(self.submit)

        self.total.setFixedSize(QSize(450,30))
        self.open.setFixedSize(QSize(450,30))
        self.back_btn.setFixedSize(QSize(70,30))
        self.submit_btn.setFixedSize(QSize(70,30))

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
        win.show_employee_table(True)

class EmployeeForm(QWidget):
    def __init__(self, emp=('', '', '', date.today(), '', '', '', False, date.today(), False, date.today(), 0)):
        super().__init__()
        self.emp = emp
        self.edited = False
        self.form()
        # self.display()

    def display(self, emp=None):
        if not emp:
            self.emp = ('', '', '', date.today(), '', '', '', False, date.today(), False, date.today(), 0)
            self.delete_btn.hide()
            self.edited = False
        else:
            self.emp = emp
            self.delete_btn.show()
            self.edited = True
        self.update() 
        self.show()

    def form(self):
        self.layout = QFormLayout()
        
        self.emp_id = QLineEdit()
        emp_valid = QIntValidator(self.emp_id)
        self.emp_id.setValidator(emp_valid)
        self.layout.addRow(QLabel("Employee ID: "), self.emp_id)

        self.first = QLineEdit()
        self.layout.addRow(QLabel("First Name: "), self.first)
        self.last = QLineEdit()
        self.layout.addRow(QLabel("Last Name: "), self.last)
        self.team = QLineEdit()
        self.layout.addRow(QLabel("Team: "), self.team)

        self.position = QLineEdit()
        position_valid = QIntValidator(self.position)
        self.position.setValidator(position_valid)
        self.layout.addRow(QLabel("Position #: "), self.position)
        
        self.supervisor = QLineEdit()
        self.layout.addRow(QLabel("Supervisor: "), self.supervisor)
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

        self.prev_exp = QLineEdit()
        exp_valid = QIntValidator(self.prev_exp)
        self.prev_exp.setValidator(exp_valid)
        self.layout.addRow(QLabel("Previous Experience (months): "), self.prev_exp)

        self.back_btn = QPushButton("Back", self)
        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.clicked.connect(self.validate)
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.clicked.connect(self.delete_emp)

        self.emp_id.setFixedSize(QSize(450,30))
        self.first.setFixedSize(QSize(450,30))
        self.last.setFixedSize(QSize(450,30))
        self.team.setFixedSize(QSize(450,30))
        self.position.setFixedSize(QSize(450,30))
        self.supervisor.setFixedSize(QSize(450,30))
        self.start.setFixedSize(QSize(450,30))
        self.promoted_date.setFixedSize(QSize(450,30))
        self.inactive_date.setFixedSize(QSize(450,30))
        self.prev_exp.setFixedSize(QSize(450,30))
        self.back_btn.setFixedSize(QSize(70,30))
        self.submit_btn.setFixedSize(QSize(70,30))
        self.delete_btn.setFixedSize(QSize(70,30))

        self.layout.addRow(self.back_btn, self.submit_btn)
        self.layout.addRow(self.delete_btn)
        self.setLayout(self.layout)
        self.hide()

    def validate(self):
        error_window = QMessageBox()
        error_window.setWindowIcon(QIcon('aclogo.ico'))
        error_window.setWindowTitle("Error")
        error_messages = []
        text = ""

        if not self.edited:
            cur.execute('SELECT * FROM employees')
            current_data = cur.fetchall()
            if any(emp[0] == int(self.emp_id.text()) for emp in current_data):
                error_messages.append("Employee ID is already in use")

        if self.emp_id.text() == "":
            error_messages.append("Employee ID cannot be empty")
        if self.first.text() == "":
            error_messages.append("First name cannot be empty")
        if self.last.text() == "":
            error_messages.append("Last name cannot be empty")
        if self.position.text() == "" and not self.inactive.isChecked():
            error_messages.append("Position cannot be empty")
        if self.start.text() == "":
            error_messages.append("Start date cannot be empty")

        if error_messages == []:
            self.submit_form()
        else:
            for i, message in enumerate(error_messages):
                if i == len(error_messages)-1:
                    text += message
                else:
                    text += message + "\n"
            error_window.setText(text)
            error_window.exec()

    def delete_emp(self):
        self.setDisabled(True)
        close = QMessageBox()
        close.setWindowIcon(QIcon('aclogo.ico'))
        close.setWindowTitle("Delete employee")
        close.setText("Are you sure?\n(There is no undo)")
        close.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        close = close.exec()

        if close == QMessageBox.StandardButton.Yes:
            try:
                delete_sql = '''
                    DELETE FROM employees WHERE id = %s::int AND first_name = %s AND last_name = %s
                '''
                cur.execute(delete_sql, (self.emp[0], self.emp[1], self.emp[2]))
            except Exception as ex:
                print(ex)

            conn.commit()
            self.setDisabled(False)
            win.table.update()
            win.positions.update()
            win.promoted_table.update()
            win.inactive_table.update()
            win.show_employee_table()
        else:
            self.setDisabled(False)


    def submit_form(self):
        eid = self.emp_id.text()
        f_name = self.first.text()
        l_name = self.last.text()
        position = None if self.position.text() == '' else self.position.text()
        supervisor = None if self.supervisor.text() == '' else self.supervisor.text()
        team = self.team.text()
        start = self.start.text()
        promoted = "TRUE" if self.promoted.isChecked() else "FALSE"
        promoted_date = "1000-01-01" if not self.promoted.isChecked() else self.promoted_date.text()
        inactive = "TRUE" if self.inactive.isChecked() else "FALSE"
        inactive_date = "1000-01-01" if not self.inactive.isChecked() else self.inactive_date.text()
        prev_exp = self.prev_exp.text()

        data = (eid, f_name, l_name, start, team, position, supervisor, promoted, promoted_date, inactive, inactive_date, prev_exp)

        if (self.promoted.isChecked() and data in win.promoted_table.data) or \
        (self.inactive.isChecked() and data in win.inactive_table.data) or \
        (data in win.table.data):
            win.show_employee_table()

        if self.inactive.isChecked() and data in win.inactive_table.data:
            win.show_employee_table()

        if data in win.table.data:
            win.show_employee_table()

        try:
            employee_sql = '''
                INSERT INTO employees (id, first_name, last_name, start_date, team, position, supervisor, promoted, promoted_date, inactive, inactive_date, previous_experience)
                VALUES (%s::int, %s, %s, %s::date, NULLIF(%s,''), %s::int, %s, %s, NULLIF(%s,'1000-01-01')::date, %s, NULLIF(%s,'1000-01-01')::date, %s::int)
                ON CONFLICT (id) DO UPDATE SET
                (first_name, last_name, start_date, team, position, supervisor, promoted, promoted_date, inactive, inactive_date, previous_experience) = (EXCLUDED.first_name, EXCLUDED.last_name, EXCLUDED.start_date, EXCLUDED.team, EXCLUDED.position, EXCLUDED.supervisor, EXCLUDED.promoted, EXCLUDED.promoted_date, EXCLUDED.inactive, EXCLUDED.inactive_date, EXCLUDED.previous_experience);
            '''

            cur.execute(employee_sql, data)
        except Exception as ex:
            print(ex)

        conn.commit()
        win.table.update()
        win.positions.update()
        win.promoted_table.update()
        win.inactive_table.update()
        win.show_employee_table()
    
    def inactiveClick(self, state):
        if state == 0:
            self.inactive_date.setDisabled(True)
        else:
            self.inactive_date.setDisabled(False)
            self.inactive_date.setDate(QDate.currentDate())

    def promotedClick(self, state):
        if state == 0:
            self.promoted_date.setDisabled(True)
        else:
            self.promoted_date.setDisabled(False)
            self.promoted_date.setDate(QDate.currentDate())

    def update(self):
        if self.emp:
            self.emp_id.setText(str(self.emp[0]))
            if self.emp[0] != '':
                self.emp_id.setDisabled(True)
            else:
                self.emp_id.setDisabled(False)
            self.first.setText(self.emp[1])
            self.last.setText(self.emp[2])
            self.start.setDate(QDate.fromString(str(self.emp[3]), "yyyy-MM-dd"))
            self.team.setText(str(self.emp[4]))
            self.position.setText(str(self.emp[5]))
            self.supervisor.setText(str(self.emp[6]))

            if not self.emp[7]:
                self.promoted.setChecked(False)
                self.promoted_date.setDisabled(True)
            else:
                self.promoted.setChecked(True)
                self.promoted_date.setDate(QDate.fromString(str(self.emp[8]), "yyyy-MM-dd"))

            if not self.emp[9]:
                self.inactive.setChecked(False)
                self.inactive_date.setDisabled(True)
            else:
                self.inactive.setChecked(True)
                self.inactive_date.setDate(QDate.fromString(str(self.emp[10]), "yyyy-MM-dd"))
            self.prev_exp.setText(str(self.emp[11]))

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
            team VARCHAR(255),
            position INT,
            supervisor VARCHAR(255),
            promoted BOOLEAN,
            promoted_date DATE,
            inactive BOOLEAN,
            inactive_date DATE,
            previous_experience INT
        );
        CREATE TABLE positions (
            pos_id bool PRIMARY KEY DEFAULT TRUE,
            total INT NOT NULL,
            open INT NOT NULL,
            CONSTRAINT one_row_pos CHECK (pos_id)
        );
        REVOKE DELETE, TRUNCATE ON positions FROM public;
        INSERT INTO positions (total, open) VALUES (0, 0)
        """)
    except Exception as ex:
        print(ex)

    conn.commit()

def seed_db():
    try:
        cur.execute("""
        INSERT INTO employees (id, first_name, last_name, start_date, team, position, supervisor, promoted, promoted_date, inactive, inactive_date, previous_experience) VALUES (1084321,'Rabia','Suleiman','2022-03-13', 'Intake-1', 234362, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (762256,'Isaac','Newton','2021-06-13', 'Intake-1', 454362, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (9396393,'Nikola','Tesla','2021-05-27', 'Permanency-3', 42646, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (4532435,'Thomas','Edison','2022-03-04', 'Intake-2', 317252, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 1), 
        (3620196,'Elon','Musk','2020-03-22', 'Permanency-2', NULL, NULL, FALSE, NULL, TRUE, '2022-01-11', 5), 
        (322113,'Steve','Jobs','2020-11-22', 'Permanency-1', 2364322, 'Sam Fisher', TRUE, '2021-08-11', FALSE, NULL, 0), 
        (4324324,'Walt','Disney','2020-11-22', 'Permanency-1', 223464, 'Arnold Schwarzenegger', FALSE, NULL, FALSE, NULL, 0), 
        (654336456,'Sam','Walton','2020-11-22', 'Permanency-1', 3472722, 'Arnold Schwarzenegger', FALSE, NULL, FALSE, NULL, 0), 
        (8821332,'Sigmund','Freud','2021-10-22', 'Intake-2', NULL, NULL, FALSE, NULL, TRUE, '2022-07-13', 0), 
        (2512093,'Mike','Tyson','2012-01-22', 'Permanency-1', 4386832, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (3324334,'Floyd','Mayweather','2021-07-29', 'Permanency-2', 863762, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (55432353,'Manny','Pacquiao','2020-11-19', 'Intake-2', 6756572, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (11223415,'Muhammad','Ali','2021-10-11', 'Intake-1', 3588652, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (66334521,'George','Foreman','2014-11-08', 'Permanency-3', 568682, 'Arnold Schwarzenegger', FALSE, NULL, FALSE, NULL, 3), 
        (54533333,'Conor','McGregor','2021-12-01', 'Intake-3', 8655672, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 3), 
        (54523454,'Martha','Steward','2021-10-22', 'Permanency-3', 685842, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (35345662,'Jack','Black','2021-07-07', 'Permanency-1', 658682, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (1231535,'Steve','Harvey','2015-03-06', 'Permanency-2', 6858472, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (12311535,'Samuel','Jackson','2013-01-26', 'Permanency-3', 3564562, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 3), 
        (35351511,'Arnold','Schwarzenegger','2014-12-11', 'Permanency-1', 356572, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 1), 
        (43214155,'Sylvester','Stallone','2015-11-12', 'Intake-4', 675772, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 3), 
        (33424325,'Johnny','Depp','2017-01-05', 'Permanency-3', 4565672, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 1), 
        (64265455,'Amber','Heard','2019-05-05', 'Intake-3', 865747, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (5345356,'Will','Smith','2015-04-07', 'Intake-1', 676542, 'Arnold Schwarzenegger', FALSE, NULL, FALSE, NULL, 3), 
        (4123456,'Jada','Smith','2018-02-26', 'Intake-3', 856652, 'Arnold Schwarzenegger', FALSE, NULL, FALSE, NULL, 1), 
        (7587884,'Jaden','Smith','2020-05-11', 'Intake-2', 8645762, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (6534536,'Willow','Smith','2019-12-22', 'Intake-3', 8765762, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 3), 
        (554216,'Taylor','Swift','2022-02-22', 'Intake-2', 547652, 'Sam Fisher', TRUE, '2022-06-01', FALSE, NULL, 4), 
        (73457774,'Jimi','Hendrix','2019-07-22', 'Intake-1', 4567672, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 1), 
        (36463467,'Rolling','Stone','2016-06-14', 'Intake-3', 767542, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (8685746,'Lil','Wayne','2012-08-19', 'Permanency-3', 876572, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (5452367,'Snoop','Dogg','2012-04-20', 'Intake-2', 8766752, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (1234125,'Martha','Steward','2016-04-21', 'Intake-1', 8645652, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (3243432,'Marty','Byrd','2019-09-20', 'Permanency-1', 456562, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 0), 
        (3454356,'Linda','Byrd','2019-09-20', 'Permanency-1', 4564332, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (7867574,'Larry','Bird','2017-10-22', 'Permanency-1', 8654752, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 1), 
        (9045615,'Magic','Johnson','2020-11-23', 'Intake-3', 6975672, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2), 
        (4534234,'Hakeem','Olajuwon','2021-07-09', 'Permanency-1', 458652, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 3), 
        (9982109,'Michael','Jordan','2021-01-03', 'Permanency-3', 754452, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 1), 
        (240824,'Kobe','Bryant','2008-08-24', 'Permanency-2', NULL, NULL, FALSE, NULL, TRUE, '2020-02-04', 3), 
        (1024954,'Lebron','James','2021-08-04', 'Intake-2', 5744442, 'Sam Fisher', FALSE, NULL, FALSE, NULL, 2); 
        INSERT INTO positions (total, open) VALUES (0, 0)
        """)
    except Exception as ex:
        print(ex)

    conn.commit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # connect to postgres
    try:
        conn = psycopg2.connect(dbname = "postgres", user = "postgres", password = "9dEP0ekzd2y5xhH6", host = "db.tpmesxnmkuayksrpgkmt.supabase.co", port = 5432)
    except:
        print('Unable to connect to the database')
        sys.exit(1)

    # open a cursor to perform db operations
    cur = conn.cursor()
    # create_db()
    # seed_db()
    yellow_count = 0
    red_count = 0
    win = UserInterface()
    win.show()

    sys.exit(app.exec())

from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QGridLayout, QHeaderView, QMainWindow, QLabel, QPushButton, QFormLayout, QLineEdit, QDateEdit, QCheckBox, QTabWidget, QAbstractItemView, QMessageBox, QFileDialog
)

from PyQt6.QtGui import QColor, QTextDocument, QIntValidator, QPageLayout, QIcon

from PyQt6.QtCore import QDate, QSize, QMarginsF, QFileInfo

from PyQt6.QtPrintSupport import QPrinter

import psycopg2
from datetime import date, timedelta
import sys

class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('aclogo.ico'))
        self.tabs = QTabWidget()
        self.table = EmployeeTable()
        self.tabs.addTab(self.table, "Active")
        self.promoted_table = PromotedTable()
        self.tabs.addTab(self.promoted_table, "Promoted")
        self.inactive_table = InactiveTable()
        self.tabs.addTab(self.inactive_table, "Inactive")

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
        self.positions.print_btn.clicked.connect(self.print_info)
        self.emp_form.back_btn.clicked.connect(self.show_employee_table)
        self.pos_form.back_btn.clicked.connect(self.show_employee_table)
        self.setStyleSheet("QTableWidget { selection-color: palette(text); selection-background-color: palette(base); }")

    def show_employee_table(self):
        self.emp_form.hide()
        self.pos_form.hide()
        self.tabs.show()
        self.positions.show()

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
                word = "Promoted"
            elif tab == 2:
                table = self.inactive_table.tableWidget
                word = "Inactive"

            self.printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
            self.printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            self.printer.setPageMargins(QMarginsF(15,15,15,15), QPageLayout.Unit.Millimeter)
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
                            margin: 10px 0px 0px 0px;
                        }

                        p {
                            margin: 5px 0px 5px 0px;
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
                        """ % (self.positions.data[1], self.positions.data[2], self.positions.yellow_count, self.positions.red_count))

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
        self.data = cur.fetchall()
        self.data.sort(key=lambda emp: emp[3])
        self.table()

    def table(self):
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    def update(self):
        cur.execute(self.sql)
        self.data = cur.fetchall()
        self.refresh()

    def refresh(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.createTable()
        self.layout.addWidget(self.tableWidget)

    def onHeaderClicked(self, dataIndex):
        if dataIndex <= 4:
            if (all(self.data[i][dataIndex] <= self.data[i + 1][dataIndex] for i in range(len(self.data)-1))):
                self.data.sort(key=lambda emp: emp[dataIndex], reverse=True)
            else:
                self.data.sort(key=lambda emp: emp[dataIndex])
            self.refresh()
        elif dataIndex == 5:
            # Promoted
            if self.data and self.data[0][5] == True and self.data[0][7] == False: 
                if (all(self.data[i][6] <= self.data[i + 1][6] for i in range(len(self.data)-1))):
                    self.data.sort(key=lambda emp: emp[6], reverse=True)
                else:
                    self.data.sort(key=lambda emp: emp[6])
            # Inactive
            elif self.data and self.data[0][7] == True:
                if (all(self.data[i][8] <= self.data[i + 1][8] for i in range(len(self.data)-1))):
                    self.data.sort(key=lambda emp: emp[8], reverse=True)
                else:
                    self.data.sort(key=lambda emp: emp[8])
            self.refresh()

class EmployeeTable(TableDad):
    def __init__(self):
        super().__init__("SELECT * FROM employees WHERE promoted <> TRUE AND inactive <> TRUE;")

    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 6)
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0]))) # ID
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1]))) # First Name
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2]))) # Last Name
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3]))) # Start Date
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4]))) # Team
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            edit_button.setFixedSize(QSize(40,30))
            self.tableWidget.setCellWidget(i,5, edit_button)
            self.tableWidget.item(i, 3).setBackground(QColor(self.date_colors(emp[3])))
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(5, 40)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header.sectionClicked.connect(self.onHeaderClicked)

    def date_colors(self, emp_date):
        days = (date.today() - emp_date).days
        if days >= 274:
            if days >= 365:
                return "Red"
            return "Yellow"
        return "White"

class PromotedTable(TableDad):
    def __init__(self):
        super().__init__("SELECT * FROM employees WHERE promoted <> FALSE AND inactive <> TRUE;")

    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 7)
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team", "Promotion Date", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0]))) # ID
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2]))) # First Name
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1]))) # Last Name
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3]))) # Start Date
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4]))) # Team
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[6]))) # Promoted Date
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            edit_button.setFixedSize(QSize(40,30))
            self.tableWidget.setCellWidget(i,6, edit_button)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(6, 40)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header.sectionClicked.connect(self.onHeaderClicked)

class InactiveTable(TableDad):
    def __init__(self):
        super().__init__("SELECT * FROM employees WHERE inactive <> FALSE;")
        
    def createTable(self):
        self.tableWidget = QTableWidget(len(self.data), 7)
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Start Date", "Team", "Inactive Date", ""])
        for i, emp in enumerate(self.data):
            edit_button = QPushButton("Edit", self)
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(emp[0]))) # ID
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(emp[2]))) # First Name
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(emp[1]))) # Last Name
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(emp[3]))) # Start Date
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(emp[4]))) # Team
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(emp[8]))) # Inactive Date
            edit_button.clicked.connect(lambda clicked, j=i: win.show_employee_form(self.data[j]))
            edit_button.setFixedSize(QSize(40,30))
            self.tableWidget.setCellWidget(i,6, edit_button)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(6, 40)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header.sectionClicked.connect(self.onHeaderClicked)

class PositionInfo(QWidget):
    def __init__(self):
        super().__init__()
        cur.execute("SELECT * FROM positions")
        self.data = cur.fetchone()
        self.grid()

    def grid(self):
        self.layout = QGridLayout()
        self.populate_grid()
        self.setLayout(self.layout)
        self.show()

    def label_data(self):
        self.total = QLabel("Total Positions : %s" % self.data[1])
        self.open = QLabel("Open Positions : %s" % self.data[2])
        self.upcoming = QLabel("Upcoming Openings : %s" % self.yellow_count)
        self.upcoming.setStyleSheet("""background-color: yellow;
                                        padding: 2px;""")
        self.promotions = QLabel("Pending Promotions : %s" % self.red_count)
        self.promotions.setStyleSheet("""background-color: red;
                                        padding: 2px;""")

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

    def populate_grid(self):
        self.get_position_counts()
        self.label_data()
        self.data_btn = QPushButton("Edit Positions", self)
        self.empl_btn = QPushButton("New Employee", self)
        self.print_btn = QPushButton("Save as PDF", self)

        self.data_btn.setFixedSize(QSize(100,30))
        self.empl_btn.setFixedSize(QSize(100,30))
        self.print_btn.setFixedSize(QSize(100,30))
        self.total.setFixedSize(QSize(200,30))
        self.open.setFixedSize(QSize(200,30))
        self.upcoming.setFixedSize(QSize(135,30))
        self.promotions.setFixedSize(QSize(135,30))

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
            self.delete_btn.hide()
        else:
            self.emp = emp
            self.delete_btn.show()
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
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.clicked.connect(self.delete_emp)

        self.back_btn.setFixedSize(QSize(70,30))
        self.submit_btn.setFixedSize(QSize(70,30))
        self.delete_btn.setFixedSize(QSize(70,30))

        self.layout.addRow(self.back_btn, self.submit_btn)
        self.layout.addRow(self.delete_btn)
        self.setLayout(self.layout)
        self.hide()

    def delete_emp(self):
        self.setDisabled(True)
        close = QMessageBox()
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
            win.promoted_table.update()
            win.inactive_table.update()
            win.show_employee_table()
        else:
            self.setDisabled(False)


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
                VALUES (%s::int, %s, %s, %s, NULLIF(%s,''), %s, NULLIF(%s,'1000-01-01')::date, %s, NULLIF(%s,'1000-01-01')::date)
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
            team VARCHAR(255),
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
        INSERT INTO employees (id, first_name, last_name, start_date, team, promoted, promoted_date, inactive, inactive_date) VALUES (1084321,'Rabia','Suleiman','2022-03-13', 'Intake-1', FALSE, NULL, FALSE, NULL), 
        (762256,'Isaac','Newton','2021-06-13', 'Intake-1', FALSE, NULL, FALSE, NULL), 
        (9396393,'Nikola','Tesla','2021-05-27', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (4532435,'Thomas','Edison','2022-03-04', 'Intake-2', FALSE, NULL, FALSE, NULL), 
        (3620196,'Elon','Musk','2020-03-22', 'Permanency-2', FALSE, NULL, TRUE, '2022-01-11'), 
        (322113,'Steve','Jobs','2020-11-22', 'Permanency-1', TRUE, '2021-08-11', FALSE, NULL), 
        (4324324,'Walt','Disney','2020-11-22', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (654336456,'Sam','Walton','2020-11-22', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (8821332,'Sigmund','Freud','2021-10-22', 'Intake-2', FALSE, NULL, TRUE, '2022-07-13'), 
        (2512093,'Mike','Tyson','2012-01-22', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (3324334,'Floyd','Mayweather','2021-07-29', 'Permanency-2', FALSE, NULL, FALSE, NULL), 
        (55432353,'Manny','Pacquiao','2020-11-19', 'Intake-2', FALSE, NULL, FALSE, NULL), 
        (11223415,'Muhammad','Ali','2021-10-11', 'Intake-1', FALSE, NULL, FALSE, NULL), 
        (66334521,'George','Foreman','2014-11-08', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (54533333,'Conor','McGregor','2021-12-01', 'Intake-3', FALSE, NULL, FALSE, NULL), 
        (54523454,'Martha','Steward','2021-10-22', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (35345662,'Jack','Black','2021-07-07', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (1231535,'Steve','Harvey','2015-03-06', 'Permanency-2', FALSE, NULL, FALSE, NULL), 
        (12311535,'Samuel','Jackson','2013-01-26', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (35351511,'Arnold','Schwarzenegger','2014-12-11', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (43214155,'Sylvester','Stallone','2015-11-12', 'Intake-4', FALSE, NULL, FALSE, NULL), 
        (33424325,'Johnny','Depp','2017-01-05', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (64265455,'Amber','Heard','2019-05-05', 'Intake-3', FALSE, NULL, FALSE, NULL), 
        (5345356,'Will','Smith','2015-04-07', 'Intake-1', FALSE, NULL, FALSE, NULL), 
        (4123456,'Jada','Smith','2018-02-26', 'Intake-3', FALSE, NULL, FALSE, NULL), 
        (7587884,'Jaden','Smith','2020-05-11', 'Intake-2', FALSE, NULL, FALSE, NULL), 
        (6534536,'Willow','Smith','2019-12-22', 'Intake-3', FALSE, NULL, FALSE, NULL), 
        (554216,'Taylor','Swift','2022-02-22', 'Intake-2', TRUE, '2022-06-01', FALSE, NULL), 
        (73457774,'Jimi','Hendrix','2019-07-22', 'Intake-1', FALSE, NULL, FALSE, NULL), 
        (36463467,'Rolling','Stone','2016-06-14', 'Intake-3', FALSE, NULL, FALSE, NULL), 
        (8685746,'Lil','Wayne','2012-08-19', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (5452367,'Snoop','Dogg','2012-04-20', 'Intake-2', FALSE, NULL, FALSE, NULL), 
        (1234125,'Martha','Steward','2016-04-21', 'Intake-1', FALSE, NULL, FALSE, NULL), 
        (3243432,'Marty','Byrd','2019-09-20', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (3454356,'Linda','Byrd','2019-09-20', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (7867574,'Larry','Bird','2017-10-22', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (9045615,'Magic','Johnson','2020-11-23', 'Intake-3', FALSE, NULL, FALSE, NULL), 
        (4534234,'Hakeem','Olajuwon','2021-07-09', 'Permanency-1', FALSE, NULL, FALSE, NULL), 
        (9982109,'Michael','Jordan','2021-01-03', 'Permanency-3', FALSE, NULL, FALSE, NULL), 
        (240824,'Kobe','Bryant','2008-08-24', 'Permanency-2', FALSE, NULL, TRUE, '2020-02-04'), 
        (1024954,'Lebron','James','2021-08-04', 'Intake-2', FALSE, NULL, FALSE, NULL); 
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

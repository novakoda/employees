#!/usr/local/bin/python3

import psycopg2
from tkinter import *
from tkcalendar import DateEntry
from datetime import date, timedelta

def reset_window():
    for widget in canvas.winfo_children():
        widget.destroy()

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
            inactive BOOLEAN
        );
        CREATE TABLE positions (
            pos_id bool PRIMARY KEY DEFAULT TRUE,
            total INT NOT NULL,
            open INT NOT NULL,
            CONSTRAINT one_row_pos CHECK (pos_id)
        );
        REVOKE DELETE, TRUNCATE ON positions FROM public;
        INSERT INTO employees (id, first_name, last_name, start_date, team, promoted, inactive) VALUES (1084321,'Rabia','Suleiman','2022-03-13', 1, FALSE, FALSE), (762256,'Isaac','Newton','2021-06-13', 1, FALSE, FALSE), (9396393,'Nikola','Tesla','2021-05-27', 33, FALSE, FALSE), (3620196,'Elon','Musk','2020-03-22', 33, FALSE, TRUE), (322113,'Steve','Jobs','2020-11-22', 2, TRUE, FALSE), (4534234,'Hakeem','Olajuwon','2021-07-09', 34, FALSE, FALSE), (8821332,'Sigmund','Freud','2021-10-22', 3, FALSE, FALSE), (2512093,'Martha','Steward','2021-10-22', 5, FALSE, FALSE), (554216,'Taylor','Swift','2022-02-22', 22, FALSE, FALSE), (9982109,'Michael','Jordan','2021-01-03', 23, FALSE, FALSE), (1024954,'Lebron','James','2021-08-04', 23, FALSE, FALSE); 
        INSERT INTO positions (total, open) VALUES (0, 0)
        """)
    except Exception as ex:
        print(ex)

    conn.commit()

def submit_form(eid,f_name,l_name,date,team,promoted,inactive):
    try:
        employee_sql = '''
            INSERT INTO employees (id, first_name, last_name, start_date, team, promoted, inactive)
            VALUES (%s::int,%s, %s, %s, NULLIF(%s,'')::int, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
            (first_name,last_name,start_date,team,promoted,inactive) = (EXCLUDED.first_name, EXCLUDED.last_name, EXCLUDED.start_date, EXCLUDED.team, EXCLUDED.promoted, EXCLUDED.inactive);
        '''

        cur.execute(employee_sql, (eid, f_name,l_name,date,team,promoted,inactive))
    
    except Exception as ex:
        print(ex)

    conn.commit()
    list_employees()

def employee_form(emp=(None,'','', date.today(), None, False, False)):
    reset_window()
    # Create text boxes
    eid = make_entry(canvas, emp[0], 0, 1)
    if emp[0]: eid.config(state='readonly')

    f_name = make_entry(canvas, emp[1], 1, 1)
    l_name = make_entry(canvas, emp[2], 2, 1)
    team = make_entry(canvas, emp[4], 3, 1)

    date = DateEntry(canvas, date_pattern="yyyy-mm-dd")
    date.set_date(emp[3])
    date.grid(row=4, column=1)

    promoted_var = IntVar(canvas, 1 if emp[5] else 0)
    promoted = Checkbutton(canvas, variable=promoted_var)
    promoted.grid(row=5, column=1)

    inactive_var = IntVar(canvas, 1 if emp[6] else 0)
    inactive = Checkbutton(canvas, variable=inactive_var)
    inactive.grid(row=6, column=1)

    make_button(canvas, "Back", lambda : list_employees(), 7, 0)
    make_button(canvas, "Submit", lambda : submit_form(eid.get(), f_name.get(), l_name.get(), date.get_date(), team.get(), "TRUE" if promoted_var.get() else "FALSE", "TRUE" if inactive_var.get() else "FALSE"), 7, 1)

    # Create text labels
    make_label(canvas, "Employee ID", 0, 0)
    make_label(canvas, "First Name", 1, 0)
    make_label(canvas, "Last Name", 2, 0)
    make_label(canvas, "Team #", 3, 0)
    make_label(canvas, "Start Date", 4, 0)
    make_label(canvas, "Promoted", 5, 0)
    make_label(canvas, "Inactive", 6, 0)

    root.mainloop()

def make_label(window, text, row, column, color="white"):
    label_element = Label(window, text=text, bg=color)
    label_element.grid(row=row, column=column)
    return label_element

def make_button(window, text, command, row, column):
    button_element = Button(window, text=text, command=command)
    button_element.grid(row=row, column=column)


def make_entry(window, text, row, column, color="white"):
    entry_element = Entry(window, bg=color)
    entry_element.grid(row=row, column=column)
    entry_element.insert(0,'' if text == None else text)
    return entry_element

def date_colors(emp_date):
    days = (date.today() - emp_date).days
    if days >= 274:
        if days >= 365:
            return "red"
        return "yellow"
    return "white"

def get_position_counts():
    nine_ago = date.today() - timedelta(days=274)
    year_ago = date.today() - timedelta(days=365)
    cur.execute("""
    SELECT COUNT(*) FROM employees WHERE
        start_date <= %s AND start_date > %s
    """, (nine_ago, year_ago))
    yellow_count = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM employees WHERE start_date < %s", (year_ago,))
    red_count = cur.fetchone()
    return yellow_count[0], red_count[0]

def position_form(total, open):
    reset_window()
    make_label(canvas, "Total Positions", 0, 0)
    make_label(canvas, "Open Positions", 1, 0)
    total_positions = make_entry(canvas, total, 0, 1)
    open_positions = make_entry(canvas, open, 1, 1)
    make_button(canvas, "Back", lambda : list_employees(), 3, 0)
    make_button(canvas, "Submit", lambda : update_positions(total_positions.get(), open_positions.get()), 3, 1)

def update_positions(total, open):
    try:
        pos_sql = """UPDATE positions SET (total, open) = (%s::int, %s::int) WHERE pos_id = True"""
        cur.execute(pos_sql, (total, open))
    except Exception as ex:
        print(ex)
    conn.commit()
    list_employees()

def list_employees():
    reset_window()
    cur.execute("SELECT * FROM employees;")
    emp_list = cur.fetchall()
    grid_canvas = Canvas(canvas)
    grid_canvas.pack()
    pos_canvas = Canvas(canvas)
    pos_canvas.pack()
    # Employee List
    make_label(grid_canvas, "Employee ID", 0, 0)
    make_label(grid_canvas, "Last Name", 0, 1)
    make_label(grid_canvas, "First Name", 0, 2)
    make_label(grid_canvas, "Team #", 0, 3)
    make_label(grid_canvas, "Start Date", 0, 4)
    make_label(grid_canvas, "Promoted", 0, 5)
    make_label(grid_canvas, "Inactive", 0, 6)
    make_label(grid_canvas, "Edit Info", 0, 7)
    for i, emp in enumerate(emp_list):
        # (id, first_name, last_name, start_date, team, promoted, inactive)
        make_label(grid_canvas, emp[0], i+1, 0) # Employee ID
        make_label(grid_canvas, emp[2], i+1, 1) # Last name
        make_label(grid_canvas, emp[1], i+1, 2) # First name
        make_label(grid_canvas, emp[4], i+1, 3) # Team number
        make_label(grid_canvas, emp[3], i+1, 4, date_colors(emp[3])) # Start date
        make_label(grid_canvas, emp[5], i+1, 5) # promoted
        make_label(grid_canvas, emp[6], i+1, 6) # inactive
        make_button(grid_canvas, "Edit", lambda current_emp=emp : employee_form(current_emp), i+1, 7)
    # Positions Info
    cur.execute("SELECT * FROM positions")
    data = cur.fetchone()
    upcoming, pending = get_position_counts()
    make_button(pos_canvas, "New Employee", lambda : employee_form(), 0, 0)
    make_button(pos_canvas, "Edit Positions", lambda : position_form(data[1], data[2]), 1, 0)
    make_label(pos_canvas, "Total Positions: ", 1, 1)
    make_label(pos_canvas, data[1], 1, 2)
    make_label(pos_canvas, "Open Positions: ", 1, 3)
    make_label(pos_canvas, data[2], 1, 4)
    make_label(pos_canvas, "Pending Promotions: ", 0, 1)
    make_label(pos_canvas, pending, 0, 2, "red")
    make_label(pos_canvas, "Upcoming Openings: ", 0, 3)
    make_label(pos_canvas, upcoming, 0, 4, "yellow")
    root.mainloop()


root = Tk()
root.title('CAPS Employee Program')
root.resizable(True, True)
canvas = Canvas(root)
canvas.pack()


# connect to postgres
try:
    conn = psycopg2.connect(database = "d36rgsamtnofbn", user = "jwwhxzjhgnjkcy", password = "54214aacd5940c8df5e58763635b2945441b946ce69116e903cdcc4f8200f922", host = "ec2-3-217-251-77.compute-1.amazonaws.com")
except:
    print('Unable to connect to the database')

# open a cursor to perform db operations
cur = conn.cursor()



create_db()
list_employees()
# employee_form()

# conn.commit()
# conn.close()
# cur.close()
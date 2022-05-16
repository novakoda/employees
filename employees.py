import psycopg2
from tkinter import *
from tkcalendar import Calendar, DateEntry
from datetime import date, datetime

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
        INSERT INTO employees (id, first_name, last_name, start_date, team, promoted, inactive) VALUES (101,'Sam','Fisher','2022-03-13', 1, FALSE, FALSE), (113,'Steve','Jobs','2022-04-22', 2, FALSE, FALSE);
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
    date.grid(row=4, column=1)
    date.set_date(emp[3])

    promoted_var = IntVar(canvas, 1 if emp[5] else 0)
    promoted = Checkbutton(canvas, variable=promoted_var)
    promoted.grid(row=5, column=1)

    inactive_var = IntVar(canvas, 1 if emp[6] else 0)
    inactive = Checkbutton(canvas, variable=inactive_var)
    inactive.grid(row=6, column=1)

    back = Button(canvas, text="Back", width=10, command=lambda : list_employees())
    back.grid(row=7, column=0)
    submit = Button(canvas, text="Submit", width=10, command=lambda : submit_form(eid.get(), f_name.get(), l_name.get(), date.get_date(), team.get(), "TRUE" if promoted_var.get() else "FALSE", "TRUE" if inactive_var.get() else "FALSE"))
    submit.grid(row=7, column=1)

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

def list_employees():
    reset_window()
    cur.execute("SELECT * FROM employees;")
    emp_list = cur.fetchall()
    
    make_label(canvas, "Employee ID", 0, 0)
    make_label(canvas, "First Name", 0, 1)
    make_label(canvas, "Last Name", 0, 2)
    make_label(canvas, "Team #", 0, 3)
    make_label(canvas, "Start Date", 0, 4)
    make_label(canvas, "Promoted", 0, 5)
    make_label(canvas, "Inactive", 0, 6)
    make_label(canvas, "Edit Info", 0, 7)

    # (id, first_name, last_name, start_date, team, promoted, inactive)
    for i, emp in enumerate(emp_list):
        make_label(canvas, emp[0], i+1, 0) # Employee ID
        make_label(canvas, emp[1], i+1, 1) # First name
        make_label(canvas, emp[2], i+1, 2) # Last name
        make_label(canvas, emp[4], i+1, 3) # Team number
        make_label(canvas, emp[3], i+1, 4, date_colors(emp[3])) # Start date
        make_label(canvas, emp[5], i+1, 5) # promoted
        make_label(canvas, emp[6], i+1, 6) # inactive

        edit = Button(canvas, text="Edit", width=10, command=lambda current_emp=emp : employee_form(current_emp))
        edit.grid(row=i+1, column=7)

        if i == len(emp_list)-1:
            back = Button(canvas, text="New Employee", command=lambda : employee_form())
            back.grid(row=i+2, column=0)

    # print(emp_list)
    root.mainloop()


root = Tk()
root.title('CAPS Employee Program')
canvas = Canvas(root)
canvas.pack()


# connect to postgres
try:
    conn = psycopg2.connect(database = "caps_employees", user = "employees", password = "caps")
except:
    print('Unable to connect to the database')

# open a cursor to perform db operations
cur = conn.cursor()



# create_db()
list_employees()
# employee_form()

# conn.commit()
# conn.close()
# cur.close()
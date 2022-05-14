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
            inactive BOOLEAN NOT NULL
        );
        CREATE TABLE positions (
            id SERIAL PRIMARY KEY NOT NULL,
            is_open BOOLEAN NOT NULL,
            filled_date DATE,
            employee_id INT REFERENCES employees(id),
            incoming_id INT REFERENCES employees(id),
            is_b BOOLEAN NOT NULL
        );
        ALTER TABLE employees
            ADD position_id INT REFERENCES positions(id),
            ADD upcoming_id INT REFERENCES positions(id)
        ;

        INSERT INTO employees (id, first_name, last_name, start_date, team, inactive, position_id, upcoming_id) VALUES (101,'Sam','Fisher','2022-03-13', 1, FALSE, NULL, NULL), (113,'Steve','Jobs','2022-04-22', 2, FALSE, NULL, NULL);
        INSERT INTO positions (is_open, filled_date, employee_id, incoming_id, is_b) VALUES (FALSE,'2022-03-13', 101, 113, FALSE);
        """)
    except Exception as ex:
        print(ex)

    conn.commit()

def submit_form(eid,f_name,l_name,date,team,inactive,position,upcoming):
    try:
        insert_sql = '''
            INSERT INTO employees (id, first_name,last_name,start_date,team,inactive,position_id,upcoming_id)
            VALUES (%s::int,%s, %s, %s, NULLIF(%s,'')::int, %s, NULLIF(%s,'')::int, NULLIF(%s,'')::int)
            ON CONFLICT (id) DO UPDATE SET
            (first_name,last_name,start_date,team,inactive,position_id,upcoming_id) = (EXCLUDED.first_name, EXCLUDED.last_name, EXCLUDED.start_date, EXCLUDED.team, EXCLUDED.inactive, EXCLUDED.position_id, EXCLUDED.upcoming_id);
        '''
        cur.execute(insert_sql, (eid, f_name,l_name,date,team,inactive,position,upcoming))
    # cur.execute("INSERT INTO employees (id, first_name,last_name,start_date,team,inactive,position_id,upcoming_id) VALUES (%s::int,%s, %s, %s, NULLIF(%s,'')::int, %s, NULLIF(%s,'')::int, NULLIF(%s,'')::int)", (f_name,l_name,date,team,inactive,position,upcoming))
    except Exception as ex:
        print(ex)

    conn.commit()
    list_employees()

def employee_form(emp=(None,'','', date.today(), None, False, None, None)):
    reset_window()
    # Create text boxes
    eid = make_entry(canvas, emp[0], 0, 1)
    if emp[0]: eid.config(state='readonly')

    f_name = make_entry(canvas, emp[1], 1, 1)
    l_name = make_entry(canvas, emp[2], 2, 1)
    team = make_entry(canvas, emp[4], 3, 1)
    position = make_entry(canvas, emp[6], 4, 1)
    upcoming = make_entry(canvas, emp[7], 5, 1)

    date = DateEntry(canvas, date_pattern="yyyy-mm-dd")
    date.grid(row=6, column=1)
    date.set_date(emp[3])

    inactive_var = "FALSE" if emp[5] else "TRUE"
    inactive = Checkbutton(canvas, offvalue="FALSE", onvalue="TRUE", variable=inactive_var)
    inactive.grid(row=7, column=1)

    back = Button(canvas, text="Back", width=10, command=lambda : list_employees())
    back.grid(row=8, column=0)
    submit = Button(canvas, text="Submit", width=10, command=lambda : submit_form(eid.get(), f_name.get(), l_name.get(), date.get_date(), team.get(), inactive_var, position.get(), upcoming.get()))
    submit.grid(row=8, column=1)

    # Create text labels
    make_label(canvas, "Employee ID", 0, 0)
    make_label(canvas, "First Name", 1, 0)
    make_label(canvas, "Last Name", 2, 0)
    make_label(canvas, "Team #", 3, 0)
    make_label(canvas, "Position ID", 4, 0)
    make_label(canvas, "Upcoming Pos. ID", 5, 0)
    make_label(canvas, "Start Date", 6, 0)
    make_label(canvas, "Inactive", 7, 0)

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
    make_label(canvas, "Position ID", 0, 4)
    make_label(canvas, "Upcoming Pos. ID", 0, 5)
    make_label(canvas, "Start Date", 0, 6)
    make_label(canvas, "Inactive", 0, 7)
    make_label(canvas, "Edit Info", 0, 8)

    for i, emp in enumerate(emp_list):
        make_label(canvas, emp[0], i+1, 0) # Employee ID
        make_label(canvas, emp[1], i+1, 1) # First name
        make_label(canvas, emp[2], i+1, 2) # Last name
        make_label(canvas, emp[4], i+1, 3) # Team number
        make_label(canvas, emp[6], i+1, 4) # Position id
        make_label(canvas, emp[7], i+1, 5) # Upcoming pos id
        make_label(canvas, emp[3], i+1, 6, date_colors(emp[3])) # Start date
        make_label(canvas, emp[5], i+1, 7) # inactive

        date_colors(emp[3])
        edit = Button(canvas, text="Edit", width=10, command=lambda current_emp=emp : employee_form(current_emp))
        edit.grid(row=i+1, column=8)

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
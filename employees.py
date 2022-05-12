import psycopg2
from tkinter import *
from tkcalendar import Calendar
from datetime import date

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

def submit_form(f_name,l_name,date,team,inactive,position,upcoming):
    try:
        cur.execute("INSERT INTO employees (id, first_name,last_name,start_date,team,inactive,position_id,upcoming_id) VALUES (%s::int,%s, %s, %s, NULLIF(%s,'')::int, %s, NULLIF(%s,'')::int, NULLIF(%s,'')::int)", (f_name,l_name,date,team,inactive,position,upcoming))
    except:
        print("Unable to add item to database")

    conn.commit()

def employee_form(emp=(None,'','', date.today(), None, False, None, None)):
    reset_window()
    # Create text boxes
    eid = Entry(canvas, width=30)
    eid.grid(row=0, column=1)
    eid.insert(0,'' if emp[0] == None else emp[0])

    f_name = Entry(canvas, width=30)
    f_name.grid(row=1, column=1)
    f_name.insert(0,emp[1])

    l_name = Entry(canvas, width=30)
    l_name.grid(row=2, column=1)
    l_name.insert(0,emp[2])
    
    team = Entry(canvas, width=30)
    team.grid(row=3, column=1)
    position = Entry(canvas, width=30)
    position.grid(row=4, column=1)
    upcoming = Entry(canvas, width=30)
    upcoming.grid(row=5, column=1)
    date = Calendar(canvas, date_pattern="yyyy-mm-dd")
    date.grid(row=6, column=1)
    inactive_var = StringVar()
    inactive = Checkbutton(canvas, offvalue="FALSE", onvalue="TRUE", variable=inactive_var)
    inactive.grid(row=7, column=1)

    back = Button(canvas, text="Back", width=10, command=lambda : list_employees())
    back.grid(row=8, column=0)
    submit = Button(canvas, text="Submit", width=10, command=lambda : submit_form(f_name.get(),l_name.get(),date.get_date(),team.get(),inactive_var.get(),position.get(),upcoming.get()))
    submit.grid(row=8, column=1)

    # Create text labels
    eid_label = Label(canvas, text="Employee ID")
    eid_label.grid(row=0, column=0)
    f_name_label = Label(canvas, text="First Name")
    f_name_label.grid(row=1, column=0)
    l_name_label = Label(canvas, text="Last Name")
    l_name_label.grid(row=2, column=0)
    team_label = Label(canvas, text="Team #")
    team_label.grid(row=3, column=0)
    position_label = Label(canvas, text="Position ID")
    position_label.grid(row=4, column=0)
    upcoming_label = Label(canvas, text="Upcoming Pos. ID")
    upcoming_label.grid(row=5, column=0)
    date_label = Label(canvas, text="Start Date")
    date_label.grid(row=6, column=0)
    inactive_label = Label(canvas, text="Inactive")
    inactive_label.grid(row=7, column=0)

    root.mainloop()

def list_employees():
    reset_window()
    cur.execute("SELECT * FROM employees;")
    emp_list = cur.fetchall()
    
    eid_label = Label(canvas, text="Employee")
    eid_label.grid(row=0, column=0)
    f_name_label = Label(canvas, text="First Name")
    f_name_label.grid(row=0, column=1)
    l_name_label = Label(canvas, text="Last Name")
    l_name_label.grid(row=0, column=2)
    team_label = Label(canvas, text="Team #")
    team_label.grid(row=0, column=3)
    position_label = Label(canvas, text="Position ID")
    position_label.grid(row=0, column=4)
    upcoming_label = Label(canvas, text="Upcoming Pos. ID")
    upcoming_label.grid(row=0, column=5)
    date_label = Label(canvas, text="Start Date")
    date_label.grid(row=0, column=6)
    inactive_label = Label(canvas, text="Inactive")
    inactive_label.grid(row=0, column=7)
    edit_label = Label(canvas, text="Edit Info")
    edit_label.grid(row=0, column=8)

    for i, emp in enumerate(emp_list):
        eid = Label(canvas, text=emp[0])
        eid.grid(row=i+1, column=0)
        f_name = Label(canvas, text=emp[1])
        f_name.grid(row=i+1, column=1)
        l_name = Label(canvas, text=emp[2])
        l_name.grid(row=i+1, column=2)
        team = Label(canvas, text=emp[4])
        team.grid(row=i+1, column=3)
        position = Label(canvas, text=emp[6])
        position.grid(row=i+1, column=4)
        upcoming = Label(canvas, text=emp[7])
        upcoming.grid(row=i+1, column=5)
        date = Label(canvas, text=emp[3])
        date.grid(row=i+1, column=6)
        inactive = Label(canvas, text=emp[5])
        inactive.grid(row=i+1, column=7)
        edit = Button(canvas, text="Edit", width=10, command=lambda : employee_form(emp))
        edit.grid(row=i+1, column=8)

    print(emp_list)
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
# list_employees()
employee_form()

# conn.commit()
# conn.close()
# cur.close()
# task_manager.py
# Task Manager Database Application
# Connects to SQLite and lets users view, add, update, delete, and search tasks.

import sqlite3

# ─────────────────────────────────────────
# CONSTANTS  (the settings) 
# ─────────────────────────────────────────
DB_NAME          = "Task_Manager_Database.db"  # name of the database file
TABLE_NAME       = "Task"                       # name of the table we work with
MAX_NAME_LENGTH  = 40                           # task name cannot be longer than this
VALID_PRIORITIES = ["High", "Medium", "Low"]   # only these three are allowed
VALID_STATUSES   = ["Not Started", "In Progress", "Complete"]  # only these three


# ─────────────────────────────────────────
# DATABASE SETUP (connects and creates the table)
# ─────────────────────────────────────────

def connect_to_database(): #cai nay la se ket noi voi SQL cua may tinh
    """
    Opens a connection to the SQLite database file.
    Returns the connection so other functions can use it.
    """
    connection = sqlite3.connect(DB_NAME)
    return connection


def setup_table(connection): #"make the table only if it doesn't already exist
    """
    Creates the Task table if it does not already exist.
    Runs every time the program starts — safe to run again and again.
    """
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            task_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT(40)  NOT NULL,
            priority TEXT(40)  NOT NULL,
            status   TEXT      NOT NULL,
            due_date TEXT      NOT NULL
        )
    """)
    connection.commit()


# ─────────────────────────────────────────
# INPUT HELPER FUNCTIONS  (checks what the user types)
# ─────────────────────────────────────────

def get_valid_task_name(prompt): # ask the user input valid or nor
    """
    Asks for a task name and checks two things:
    1. It is not empty (blank input)
    2. It is not longer than MAX_NAME_LENGTH characters
    Keeps asking until both checks pass.
    """
    while True:
        name = input(prompt).strip()
        if name == "":
            print("  >> Task name cannot be empty. Please try again.")
        elif len(name) > MAX_NAME_LENGTH:
            print(f"  >> Task name is too long. Maximum is {MAX_NAME_LENGTH} characters.")
        else:
            return name


def get_choice_from_list(prompt, valid_choices): # Neu nguoi dung nhap Xin chao hay la xin chao thi van hoat dong
    """
    Shows the valid options and keeps asking until the user picks one.
    The check is case-insensitive (e.g. 'high' works as well as 'High').
    Returns the correctly capitalised version.
    """
    options_string = " / ".join(valid_choices)
    while True:
        user_input = input(f"{prompt} ({options_string}): ").strip()
        for choice in valid_choices:
            if user_input.lower() == choice.lower():
                return choice
        print(f"  >> Invalid choice. Please pick from: {options_string}")


def get_valid_date(prompt):  #checks the day is exactly YYYY-MM-DD
    """
    Asks for a date in YYYY-MM-DD format.
    Checks that the string is exactly 10 characters and has dashes in the right spots.
    Keeps asking until the format is correct.
    """
    while True:
        date_input = input(f"{prompt} (YYYY-MM-DD): ").strip()
        if (len(date_input) == 10
                and date_input[4] == "-"
                and date_input[7] == "-"
                and date_input[:4].isdigit()
                and date_input[5:7].isdigit()
                and date_input[8:].isdigit()):
            return date_input
        else:
            print("  >> Date must be in YYYY-MM-DD format. Example: 2026-06-01")


# ─────────────────────────────────────────
# CORE FEATURE FUNCTIONS
# ─────────────────────────────────────────

def view_all_tasks(connection):
    """
    Fetches every task from the database and prints them in a tidy table.
    If there are no tasks yet, tells the user so.
    """
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    tasks = cursor.fetchall()

    if len(tasks) == 0:
        print("\n  No tasks found in the database.\n")
        return

    print("\n" + "-" * 75)
    print(f"{'ID':<5} {'Name':<35} {'Priority':<10} {'Status':<14} {'Due Date'}")
    print("-" * 75)

    for task in tasks:
        task_id, name, priority, status, due_date_old, due_date = task
        print(f"{task_id:<5} {name:<35} {priority:<10} {status:<14} {due_date}")

    print("-" * 75 + "\n")


def add_task(connection):
    """
    Asks the user for task details, validates every field,
    then saves a new task row to the database.
    """
    print("\n--- Add New Task ---")

    name     = get_valid_task_name("  Task name: ")
    priority = get_choice_from_list("  Priority", VALID_PRIORITIES)
    status   = get_choice_from_list("  Status", VALID_STATUSES)
    due_date = get_valid_date("  Due date")

    cursor = connection.cursor()
    cursor.execute(
        f"INSERT INTO {TABLE_NAME} (name, priority, status, due_date) VALUES (?, ?, ?, ?)",
        (name, priority, status, due_date)
    )
    connection.commit()

    print(f"\n  >> Task '{name}' has been added successfully!\n")


def update_task_status(connection):
    """
    Shows all tasks, asks for an ID, checks it exists,
    then lets the user pick a new status for that task.
    Handles letters entered instead of a number (ValueError).
    """
    print("\n--- Update Task Status ---")
    view_all_tasks(connection)

    try:
        task_id = int(input("  Enter the Task ID to update: ").strip())
    except ValueError:
        print("  >> Task ID must be a number. Update cancelled.\n")
        return

    cursor = connection.cursor()
    cursor.execute(f"SELECT task_id FROM {TABLE_NAME} WHERE task_id = ?", (task_id,))
    result = cursor.fetchone()

    if result is None:
        print(f"  >> No task found with ID {task_id}. Update cancelled.\n")
        return

    new_status = get_choice_from_list("  New status", VALID_STATUSES)

    cursor.execute(
        f"UPDATE {TABLE_NAME} SET status = ? WHERE task_id = ?",
        (new_status, task_id)
    )
    connection.commit()
    print(f"  >> Task {task_id} status updated to '{new_status}'.\n")


def delete_task(connection):
    """
    Shows all tasks, asks for an ID, confirms the delete with the user,
    then removes that task from the database.
    After deleting, renumbers all remaining IDs so there are no gaps.
    Handles letters entered instead of a number, and non-existent IDs.
    """
    print("\n--- Delete Task ---")
    view_all_tasks(connection)

    try:
        task_id = int(input("  Enter the Task ID to delete: ").strip())
    except ValueError:
        print("  >> Task ID must be a number. Delete cancelled.\n")
        return

    cursor = connection.cursor()
    cursor.execute(f"SELECT name FROM {TABLE_NAME} WHERE task_id = ?", (task_id,))
    result = cursor.fetchone()

    if result is None:
        print(f"  >> No task found with ID {task_id}. Delete cancelled.\n")
        return

    task_name = result[0]
    confirm = input(f"  Are you sure you want to delete '{task_name}'? (yes/no): ").strip().lower()

    if confirm == "yes":
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE task_id = ?", (task_id,))

        # After deleting, shift every ID above the deleted one down by 1.
        # Example: tasks 1, 2, 3 — delete 2 — remaining become 1, 2.
        # WHERE task_id > ? means only tasks AFTER the deleted one get renumbered.
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET task_id = task_id - 1 WHERE task_id > ?",
            (task_id,)
        )

        connection.commit()
        print(f"  >> Task '{task_name}' has been deleted.\n")
    else:
        print("  >> Delete cancelled.\n")


def search_by_priority(connection):
    """
    Asks the user to pick a priority level,
    then shows only the tasks that match that priority.
    Uses a WHERE clause in SQL to filter the results.
    """
    print("\n--- Search Tasks by Priority ---")
    priority = get_choice_from_list("  Choose priority to search", VALID_PRIORITIES)

    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE priority = ?", (priority,))
    tasks = cursor.fetchall()

    if len(tasks) == 0:
        print(f"\n  No tasks found with priority '{priority}'.\n")
        return

    print(f"\n  Tasks with priority '{priority}':")
    print("-" * 75)
    print(f"{'ID':<5} {'Name':<35} {'Priority':<10} {'Status':<14} {'Due Date'}")
    print("-" * 75)

    for task in tasks:
        task_id, name, priority_col, status, due_date_old, due_date = task
        print(f"{task_id:<5} {name:<35} {priority_col:<10} {status:<14} {due_date}")

    print("-" * 75 + "\n")


def delete_all_tasks(connection):
    """
    Deletes every single task in the database at once.
    Asks the user to type DELETE (all capitals) to confirm.
    This stops someone wiping everything by accident.
    """
    print("\n--- Delete All Tasks ---")
    view_all_tasks(connection)

    # Double confirmation — the user must type the word DELETE exactly.
    # A simple yes/no is too easy to hit by accident for something this permanent.
    confirm = input("  Type DELETE to wipe all tasks, or anything else to cancel: ").strip()

    if confirm == "DELETE":
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME}")
        connection.commit()
        print("  >> All tasks have been deleted.\n")
    else:
        print("  >> Delete all cancelled.\n")


# ─────────────────────────────────────────
# MAIN MENU LOOP (the menu that runs everything)
# ─────────────────────────────────────────

def show_menu():
    """
    Prints the main menu. Kept in its own function so the main loop stays clean.
    """
    print("=" * 40)
    print("       TASK MANAGER DATABASE")
    print("=" * 40)
    print("  1. View all tasks")
    print("  2. Add a new task")
    print("  3. Update task status")
    print("  4. Delete a task")
    print("  5. Search tasks by priority")
    print("  6. Delete ALL tasks")
    print("  7. Exit")
    print("=" * 40)


def main():
    """
    Starts the program: connects to the database, sets up the table,
    then runs the menu loop until the user chooses Exit.
    """
    connection = connect_to_database()
    setup_table(connection)

    print("\nWelcome to the Task Manager Database!\n")

    while True:
        show_menu()
        choice = input("  Enter your choice (1-7): ").strip()

        if choice == "1":
            view_all_tasks(connection)
        elif choice == "2":
            add_task(connection)
        elif choice == "3":
            update_task_status(connection)
        elif choice == "4":
            delete_task(connection)
        elif choice == "5":
            search_by_priority(connection)
        elif choice == "6":
            delete_all_tasks(connection)
        elif choice == "7":
            print("\n  Goodbye! Your tasks have been saved.\n")
            connection.close()
            break
        else:
            print("\n  >> Invalid choice. Please enter a number from 1 to 7.\n")


if __name__ == "__main__":
    main()

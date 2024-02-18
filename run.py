import gspread
from google.oauth2.service_account import Credentials

import datetime


ascii_art_header = r"""


|_   _|__ _  ___ | | __|  \/  |  __ _  ___ | |_  ___  _ __
   | | / _` |/ __|| |/ /| |\/| | / _` |/ __|| __|/ _ \| '__|
   | || (_| |\__ \|   < | |  | || (_| |\__ \| |_|  __/| |
   |_| \__,_||___/|_|\_\|_|  |_| \__,_||___/ \__|\___||_|


"""



def get_google_sheets_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file('creds.json', scopes=scope)
    return gspread.authorize(creds)


def load_tasks():
    global tasks
    global new_sheet

    client = get_google_sheets_client()
    spreadsheet_id = '1PM_ACIIU43m6-EZ6sq2tG_m6t0YRe7MQaOeVikFu4YI'
    sheet_title = 'Tasks'
    new_sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_title)
    tasks = new_sheet.get_all_records()


def save_tasks():
    new_sheet.update('A1', [tasks])


def add_task(title, description, status='Pending', priority=None):
    deadline = input("Enter task deadline (YYYY-MM-DD) or leave empty: ")
    if deadline:
        try:
            datetime.datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            print("Invalid deadline format. Please enter in YYYY-MM-DD.")
            return

    new_task = {
        'title': title,
        'description': description,
        'status': status,
        'priority': priority,  
        'deadline': deadline
    }

    global new_sheet
    new_sheet.append_row(list(new_task.values()))
    print("Task added successfully.")


def update_task(index, title=None, description=None, status=None):
    global client

    if title:
        new_sheet.update_cell(index + 1, 1, title)
        print("Title updated successfully.")
    if description:
        new_sheet.update_cell(index + 1, 2, description)
        print("Description updated successfully.")
    if status:
        new_sheet.update_cell(index + 1, 3, status)
        print("Status updated successfully.")


def list_tasks():
    print("List of Tasks:")
    rows = new_sheet.get_all_values()
    for i, row in enumerate(rows[1:]):
        task = {
            'title': row[0],
            'description': row[1],
            'status': row[2],
            'deadline': row[3]
        }

        formatted_deadline = row[3]
        if formatted_deadline and formatted_deadline != "Medium":
            formatted_deadline = (
                datetime.datetime.strptime(formatted_deadline, "%Y-%m-%d")
                .strftime("%Y-%m-%d")
            )
        elif formatted_deadline == "Medium":
            formatted_deadline = "None"
        else:
            formatted_deadline = "None"

        print(f"{i + 1}. Title: {task['title']}, "
              f"Description: {task['description']}, "
              f"Status: {task['status']}, "
              f"Deadline: {formatted_deadline}")


def delete_task(index):
    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    global new_sheet
    new_sheet.delete_rows(index + 2)
    print("Task deleted successfully.")


def filter_tasks():
    print("\nTask Filtering")
    print("1. Filter by Priority")
    print("2. Filter by Due Date")
    print("3. Filter by Status")
    choice = input("Enter your choice: ")

    global new_sheet
    filtered_tasks = new_sheet.get_all_records()

    if choice == "1":
        priority = input("Enter priority level (High, Medium, Low): ")
        filter_by_priority(filtered_tasks, priority)
    elif choice == "2":
        filter_by_due_date(filtered_tasks)
    elif choice == "3":
        filter_by_status(filtered_tasks)
    else:
        print("Invalid choice. Please enter a valid option.")


def filter_by_priority(tasks, priority):
    filtered_tasks = [
        task for task in tasks if task.get('priority') == priority
    ]
    if not filtered_tasks:
        print(f"No tasks matching the specified priority level ({priority}).")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(
                f"{i + 1}. Title: {task['title']}, "
                f"Priority: {task['priority']}"
            )


def filter_by_due_date(filtered_tasks):
    due_date = input("Enter the due date (YYYY-MM-DD): ")
    filtered_tasks = [
        task for task in filtered_tasks if task.get("deadline") == due_date
    ]
    if not filtered_tasks:
        print("No tasks matching the specified due date.")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(
                f"{i + 1}. Title: {task['title']}, "
                f"Due Date: {task['deadline']}"
            )


def filter_by_status(filtered_tasks):
    status = input("Enter the status (e.g., Pending, In Completed): ")
    filtered_tasks = [
        task for task in filtered_tasks if task.get('status') == status
    ]

    if not filtered_tasks:
        print("No tasks matching the specified status.")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(f"{i + 1}. Title: {task['title']}, Status: {task['status']}")


def sort_tasks():
    global tasks
    tasks.sort(key=lambda x: (x.get('priority', ''), x.get('status', '')))

    print("\nTask sorted by priority and status.")
    list_tasks()


def sort_tasks_by_priority():
    global tasks
    tasks.sort(key=lambda x: (x.get('priority', ''), x.get('status', '')))

    print("\nTask sorted by priority and status.")
    list_tasks()


def sort_tasks_by_status():
    global tasks
    tasks.sort(key=lambda x: (x.get('status', ''), x.get('priority', '')))

    print("\nTask sorted by status and priority.")
    list_tasks()


def task_master():
    print(ascii_art_header)
    load_tasks()

    while True:
        print("\nTaskMaster - Task Management App!")
        print("1. Add Task")
        print("2. Update Task")
        print("3. List Tasks")
        print("4. Delete Task")
        print("5. Filter Tasks")
        print("6. Sort Tasks")
        print("7. Exit")

        choice = input("Enter your choice: ")

        try:
            choice = int(choice)
            if choice < 1 or choice > 7:
                raise ValueError("Invalid choice.")
        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter a valid integer between 1 and 7.")
            continue

        if choice == 1:
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            add_task("Title", "Description", "Status", "Priority")
        elif choice == 2:
            list_tasks()
            index = int(input("Enter the index of the task to update: ")) - 1
            print("1. Update Title")
            print("2. Update Description")
            print("3. Update Status")
            update_choice = input("Enter your choice: ")

            if update_choice == "1":
                title = input("Enter new title: ")
                update_task(index, title=title)
            elif update_choice == "2":
                description = input("Enter new description: ")
                update_task(index, description=description)
            elif update_choice == "3":
                status = input("Enter new status: ")
                update_task(index, status=status)
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == 3:
            list_tasks()
        elif choice == 4:
            list_tasks()
            index = int(input("Enter the index of the task to delete: ")) - 1
            delete_task(index)
        elif choice == 5:
            filter_tasks()
        elif choice == 6:
            print("1. Sort by Due Date")
            print("2. Sort by Priority")
            print("3. Sort by Status")
            sort_choice = input("Enter your choice: ")

            if sort_choice == "1":
                sort_tasks()
            elif sort_choice == "2":
                sort_tasks_by_priority()
            elif sort_choice == "3":
                sort_tasks_by_status()
            else:
                print("Invalid choice. Please enter a valid option.")
        elif choice == 7:
            print("Exiting TaskMaster. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":

    task_master()

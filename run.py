import os
from dotenv import load_dotenv
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime

ASCII_ART_HEADER = r"""

|_   _|__ _  ___ | | __|  \/  |  __ _  ___ | |_  ___  _ __
   | | / _` |/ __|| |/ /| |\/| | / _` |/ __|| __|/ _ \| '__|
   | || (_| |\__ \|   < | |  | || (_| |\__ \| |_|  __/| |
   |_| \__,_||___/|_|\_\|_|  |_| \__,_||___/ \__|\___||_|
"""

load_dotenv()
spreadsheet_id = os.getenv('SPREADSHEET_ID')


def open_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error opening file: {e}")
        raise


def load_credentials_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} file not found.")
    return open_file(file_path)


def get_google_sheets_client():
    creds_info = load_credentials_from_file('creds.json')
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
    return gspread.authorize(creds)


def get_worksheet(client, spreadsheet_id, sheet_title):
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_title)
        return worksheet
    except gspread.exceptions.SpreadsheetNotFound as e:
        print(f"Spreadsheet not found: {e}")
        raise
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Worksheet not found: {e}")
        raise


def load_tasks(client, spreadsheet_id):
    sheet_title = 'Tasks'
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_title)
        values = worksheet.get_all_values()
        tasks = [dict(zip(values[0], row)) for row in values[1:]]
        return tasks, worksheet
    except gspread.exceptions.SpreadsheetNotFound as e:
        print(f"Spreadsheet not found: {e}")
        raise
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Worksheet not found: {e}")
        raise
    except gspread.exceptions.APIError as e:
        print(f"Error accessing Google Sheets: {e}")
        raise


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]


def add_task(
        title,
        description,
        status='Pending',
        priority=None,
        deadline=None,
        sheet=None):
    """
    Add a new task to the task list.

    Args:
        title (str): The title of the task.
        description (str): The description of the task.
        status (str, optional): The status of the task (default is 'Pending').
        priority (str, optional): The priority of the task (default is None).
        deadline (str): The deadline of the task in 'YYYY-MM-DD' format.
        sheet (Worksheet): The worksheet object to add the task to.

    Returns:
        None
    """
    if not title.strip() or not description.strip():
        print("Title/description cannot be blank. Please provide valid input.")
        return

    if deadline:
        try:
            datetime.datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            print("Invalid format. Please enter in YYYY-MM-DD format.")
            return

    new_task = {
        'title': title,
        'description': description,
        'status': status,
        'priority': priority,
        'deadline': deadline
    }

    try:
        if sheet:
            sheet.append_row([new_task[key] for key in new_task])
            print("Task added successfully.")
    except Exception as e:
        print(f"An error occurred while adding the task: {e}")


def update_task(
        index,
        title=None,
        description=None,
        status=None,
        priority=None,
        deadline=None,
        tasks=None,
        sheet=None):
    """
    Update an existing task with the given index.

    Args:
        index (int): The index of the task to update.
        title (str, optional): The new title for the task (default is None).
        description (str): The new description for the task (default is None).
        status (str, optional): The new status for the task (default is None).
        priority (str): The new priority for the task (default is None).
        deadline (str): The new deadline for the task (default is None).
        tasks (list): List of tasks.
        sheet (Worksheet): The worksheet object containing the tasks.

    Returns:
        None
    """
    if not tasks:
        print("Tasks list is empty.")
        return

    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    if title is not None:
        tasks[index]['title'] = title
        print("Title updated successfully.")
        if sheet:            
            sheet.update_cell(index + 2, 1, title)

    if description is not None:
        tasks[index]['description'] = description
        print("Description updated successfully.")
        if sheet:            
            sheet.update_cell(index + 2, 2, description)

    if status is not None:
        tasks[index]['status'] = status
        print("Status updated successfully.")
        if sheet:            
            sheet.update_cell(index + 2, 3, status)

    if priority is not None:
        tasks[index]['priority'] = priority
        print("Priority updated successfully.")
        if sheet:           
            sheet.update_cell(index + 2, 4, priority)

    if deadline is not None:
        tasks[index]['deadline'] = deadline
        print("Deadline updated successfully.")
        if sheet:            
            sheet.update_cell(index + 2, 5, deadline)


def list_tasks(sheet):
    """
    Lists all tasks stored in the task list.

    Prints the title, description, status, priority, and deadline of each task.

    Returns:
        None
    """
    print("List of Tasks:")
    rows = sheet.get_all_values()
    print(f"{'Topic':<15}", end="")
    print(f"{'Description':<15}", end="")
    print(f"{'Status':<15}", end="")
    print(f"{'Priority':<15}", end="")
    print(f"{'Deadline':<15}")

    for i, row in enumerate(rows[1:], start=1):
        task = {
            'title': row[0],
            'description': row[1],
            'status': row[2],
            'priority': row[3],
            'deadline': row[4]
        }

        raw_deadline = row[4].strip()
        if raw_deadline:
            try:
                formatted_deadline = datetime.datetime.strptime(
                    raw_deadline, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                formatted_deadline = "Invalid date format"
        else:
            formatted_deadline = "None"

        print(f"{task['title']:<15}", end="")
        print(f"{task['description']:<15}", end="")
        print(f"{task['status']:<15}", end="")
        print(f"{task['priority']:<15}", end="")
        print(f"{formatted_deadline:<15}")


def delete_task(index, tasks=None, sheet=None):
    """
    Deletes a task from the task list based on the given index.

    Args:
        index (int): The index of the task to delete.
        tasks (list): List of tasks.
        sheet (Worksheet): The worksheet object containing the tasks.

    Returns:
        None
    """
    if not tasks:
        print("Tasks list is empty.")
        return

    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    try:
        if sheet:
            sheet.delete_rows(index + 2)
        print("Task deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting the task: {e}")


def filter_tasks(sheet):
    """
    Filters tasks based on user input.

    Args:
        sheet (Worksheet): The worksheet object containing the tasks.

    Returns:
        None
    """
    print("Task Filtering")
    print("1. Filter by Priority")
    print("2. Filter by Due Date")
    print("3. Filter by Status")
    choice = input("Enter your choice: ")

    if choice == '1':
        priority = input("Enter priority level (High, Medium, Low): ")
        filter_by_priority(sheet, priority)
    elif choice == '2':
        due_date = input("Enter the due date (YYYY-MM-DD): ")
        filter_by_due_date(sheet, due_date)
    elif choice == '3':
        status = input(
            "Enter the status (e.g., Pending, In Progress, Completed): ")
        filter_by_status(sheet, status)
    else:
        print("Invalid choice.")


def filter_by_priority(sheet, priority):
    """
    Filters tasks based on priority level.

    Args:
        sheet (Worksheet): The worksheet object containing the tasks.
        priority (str): Priority level to filter tasks (High, Medium, Low).

    Returns:
        None
    """
    priority = priority.lower()

    rows = sheet.get_all_values()
    filtered_tasks = [task for task in rows[1:] if task[3].strip(
    ).lower() == priority]  
    if not filtered_tasks:
        print(f"No tasks matching the specified priority level ({priority}).")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(
                f"{i + 1}. Title: {task[0]}, "
                f"Priority: {task[3]}"
            )


def filter_by_due_date(sheet, due_date):
    """
    Filters tasks based on due date.

    Args:
        sheet (Worksheet): The worksheet object containing the tasks.
        due_date (str): Due date to filter tasks (in "YYYY-MM-DD" format).

    Returns:
        None
    """   
    due_date = due_date.strip()

    rows = sheet.get_all_values()   
    filtered_tasks = [task for task in rows[1:] if task[4].strip() == due_date]
    if not filtered_tasks:
        print(f"No tasks matching the specified due date ({due_date}).")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(
                f"{i + 1}. Title: {task[0]}, "
                f"Due Date: {task[4]}"
            )


def filter_by_status(sheet, status):
    """
    Filters tasks based on status.

    Args:
        sheet (Worksheet): The worksheet object containing the tasks.
        status (str): Status to filter tasks (e.g., "Pending", "In Progress").

    Returns:
        None
    """
    status = status.lower()

    rows = sheet.get_all_values()
    filtered_tasks = [task for task in rows[1:] if task[2].strip(
    ).lower() == status]  
    if not filtered_tasks:
        print(f"No tasks matching the specified status ({status}).")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(
                f"{i + 1}. Title: {task[0]}, "
                f"Status: {task[2]}"
            )


def sort_tasks(tasks, sheet, sort_criteria='priority'):
    """
    Sorts tasks based on the specified criteria.

    Args:
        tasks (list): List of tasks to sort.
        sort_criteria (str): Criteria to sort tasks (default is 'priority').
            Possible values: 'priority', 'status'

    Returns:
        None
    """
    if sort_criteria == 'priority':
        tasks.sort(key=lambda x: (x.get('priority', ''), x.get('status', '')))
    elif sort_criteria == 'status':
        tasks.sort(key=lambda x: (x.get('status', ''), x.get('priority', '')))
    else:
        print("Invalid sort criteria. Sorting by priority.")
        tasks.sort(key=lambda x: (x.get('priority', ''), x.get('status', '')))

    print("\nTasks sorted by", sort_criteria)
    list_tasks(sheet)


def main_menu():
    print(ASCII_ART_HEADER)
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    client = get_google_sheets_client()
    if client:
        tasks, sheet = load_tasks(client, spreadsheet_id)
        if tasks and sheet:
            while True:
                print("\nTaskMaster - Task Management App!")
                print("1. Add Task")
                print("2. Update Task")
                print("3. List Tasks")
                print("4. Delete Task")
                print("5. Filter Tasks")
                print("6. Sort Tasks")
                print("7. Exit")

                choice = get_user_choice()
                handle_user_choice(choice, tasks, sheet)
        else:
            print("Error: Failed to load tasks or sheet.")
    else:
        print("Error: Failed to initialize Google Sheets client.")


def get_user_choice():
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if choice in range(1, 8):
                return choice
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid choice. Please select a valid option.")


def handle_user_choice(choice, tasks, sheet):
    """
    Handles user choice and performs corresponding actions.

    Args:
        choice (int): User's choice from the main menu.
        tasks (list): List of tasks.
        sheet (Worksheet): The worksheet object containing the tasks.

    Returns:
        None
    """
    if choice == 1:
        title = input("Enter task title: ")
        description = input("Enter task description: ")
        status = input(
            "Enter task status (e.g., Pending, In Progress, Completed): ")
        priority = input("Enter task priority (e.g., High, Medium, Low): ")
        deadline = input("Enter task deadline (YYYY-MM-DD) or leave empty: ")
        add_task(title, description, status, priority, deadline, sheet)
    elif choice == 2:
        list_tasks(sheet)
        index = int(input("Enter the index of the task to update: ")) - 1

        if 0 <= index < len(tasks):
            print("1. Update Title")
            print("2. Update Description")
            print("3. Update Status")
            print("4. Update Priority")
            print("5. Update Deadline")
            update_choice = input("Enter your choice: ")

            if update_choice == "1":
                title = input("Enter new title: ")
                update_task(index, title=title, tasks=tasks, sheet=sheet)
            elif update_choice == "2":
                description = input("Enter new description: ")
                update_task(
                    index,
                    description=description,
                    tasks=tasks,
                    sheet=sheet)
            elif update_choice == "3":
                status = input("Enter new status: ")
                update_task(index, status=status, tasks=tasks, sheet=sheet)
            elif update_choice == "4":
                priority = input("Enter new priority: ")
                update_task(index, priority=priority, tasks=tasks, sheet=sheet)
            elif update_choice == "5":
                deadline = input("Enter new deadline: ")
                update_task(index, deadline=deadline, tasks=tasks, sheet=sheet)
            else:
                print("Invalid choice. Please enter a valid option.")
        else:
            print("Invalid task index.")
    elif choice == 3:
        list_tasks(sheet)
    elif choice == 4:
        list_tasks(sheet)
        index = int(input("Enter the index of the task to delete: ")) - 1
        delete_task(index, tasks, sheet)
    elif choice == 5:
        filter_tasks(sheet)
    elif choice == 6:
        sort_criteria = input("Enter sort criteria (priority, status): ")
        sort_tasks(tasks, sheet, sort_criteria)
    elif choice == 7:
        print("Exiting TaskMaster. Goodbye!")
        exit()
    else:
        print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main_menu()

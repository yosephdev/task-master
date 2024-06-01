import os
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials
import re
from dotenv import load_dotenv

load_dotenv()  

ascii_art_header = r"""
___
 | _. _|  |\/| _. __|_ _ ._
 |(_|_>|< |  |(_|_> |_(/_|

"""

def get_google_sheets_client():
    creds_path = 'creds.json'  
    if not os.path.exists(creds_path):
        print(f"Error: {creds_path} file not found.")
        return None

    try:
        with open(creds_path) as f:
            creds = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in creds.json file.")
        return None

    try:
        return gspread.service_account_from_dict(creds)
    except Exception as e:
        print(f"Error: {e}")
        return None

def load_tasks():
    client = get_google_sheets_client()
    if client is None:
        print("Error: Unable to authenticate with Google Sheets API.")
        return []

    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id:
        print("Error: SPREADSHEET_ID environment variable is not set.")
        return []

    try:
        sheet = client.open_by_key(spreadsheet_id).worksheet('Tasks')
        tasks_data = sheet.get_all_records()
    except gspread.exceptions.APIError as e:
        print(f"Error accessing Google Sheets API: {e}")
        return []

    tasks = []
    for task in tasks_data:
        tasks.append({
            'title': task.get('Topic '),
            'description': task.get('Description '),
            'status': task.get('Status'),
            'priority': task.get('Priority'),
            'deadline': task.get(' Deadline')
        })

    return tasks

valid_statuses = ['Pending', 'In Progress', 'Completed']
valid_priorities = ['High', 'Medium', 'Low']

def add_task(sheet, tasks, title, description, status='Pending', priority=None, deadline=None):
    if not title.strip() or not description.strip():
        print("Task title and description cannot be empty.")
        return
    
    if status not in valid_statuses:
        print(f"Invalid status. Valid options are: {', '.join(valid_statuses)}")
        return

    if priority and priority not in valid_priorities:
        print(f"Invalid priority. Valid options are: {', '.join(valid_priorities)}")
        return

    if deadline:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", deadline):
            print("Invalid deadline format. Please enter in YYYY-MM-DD.")
            return

    new_task = {
        'title': title,
        'description': description,
        'status': status,
        'priority': priority,
        'deadline': deadline
    }

    sheet.append_row(list(new_task.values()))
    tasks.append(new_task)
    print("Task added successfully.")

def update_task(sheet, tasks, index, title=None, description=None, status=None, priority=None, deadline=None):
    if index < 0 or index >= len(tasks):
        print(f"Invalid task index. Please enter a value between 0 and {len(tasks) - 1}.")
        return
    
    if status and status not in valid_statuses:
        print(f"Invalid status. Valid options are: {', '.join(valid_statuses)}")
        return

    if priority and priority not in valid_priorities:
        print(f"Invalid priority. Valid options are: {', '.join(valid_priorities)}")
        return

    sheet_index = index + 2

    if title is not None:
        tasks[index]['title'] = title
        sheet.update_cell(sheet_index, 1, title)
    if description is not None:
        tasks[index]['description'] = description
        sheet.update_cell(sheet_index, 2, description)
    if status is not None:
        tasks[index]['status'] = status
        sheet.update_cell(sheet_index, 3, status)
    if priority is not None:
        tasks[index]['priority'] = priority
        sheet.update_cell(sheet_index, 4, priority)
    if deadline is not None:
        try:
            datetime.datetime.strptime(deadline, "%Y-%m-%d")
            tasks[index]['deadline'] = deadline
            sheet.update_cell(sheet_index, 5, deadline)
        except ValueError:
            print("Invalid deadline format. Please enter in YYYY-MM-DD.")

    print("Task updated successfully.")

def list_tasks(tasks):
    print("Number of tasks:", len(tasks))
    print("List of Tasks:")
    for i, task in enumerate(tasks):
        print(f"{i + 1}. Title: {task['title']}, "
              f"Description: {task['description']}, "
              f"Status: {task['status']}, "
              f"Priority: {task['priority']}, "
              f"Deadline: {task['deadline']}")

def delete_task(sheet, tasks, index):
    if not tasks:
        print("No tasks to delete.")
        return

    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    sheet.delete_rows(index + 2)
    tasks.pop(index)
    print("Task deleted successfully.")

def filter_tasks(tasks):
    print("\nTask Filtering")
    print("1. Filter by Priority")
    print("2. Filter by Due Date")
    print("3. Filter by Status")
    choice = input("Enter your choice: ")

    if choice == "1":
        priority = input("Enter priority level (High, Medium, Low): ")
        filter_by_priority(tasks, priority)
    elif choice == "2":
        filter_by_due_date(tasks)
    elif choice == "3":
        filter_by_status(tasks)
    else:
        print("Invalid choice. Please enter a valid option.")

def filter_by_priority(tasks, priority):
    filtered_tasks = [task for task in tasks if task.get('priority', '').lower() == priority.lower()]
    if not filtered_tasks:
        print(f"No tasks matching the specified priority level ({priority}).")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(f"{i + 1}. Title: {task['title']}, "
                  f"Description: {task['description']}, "
                  f"Status: {task['status']}, "
                  f"Priority: {task['priority']}, "
                  f"Deadline: {task['deadline']}")

def filter_by_due_date(tasks):
    due_date_str = input("Enter due date (YYYY-MM-DD): ")
    try:
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please enter in YYYY-MM-DD.")
        return

    filtered_tasks = [task for task in tasks if task.get('deadline') and datetime.datetime.strptime(task['deadline'], "%Y-%m-%d").date() <= due_date]
    if not filtered_tasks:
        print(f"No tasks due on or before {due_date_str}.")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(f"{i + 1}. Title: {task['title']}, "
                  f"Description: {task['description']}, "
                  f"Status: {task['status']}, "
                  f"Priority: {task['priority']}, "
                  f"Deadline: {task['deadline']}")

def filter_by_status(tasks):
    status = input("Enter task status (Pending, In Progress, Completed): ")
    filtered_tasks = [task for task in tasks if task.get('status', '').lower() == status.lower()]
    if not filtered_tasks:
        print(f"No tasks matching the specified status ({status}).")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(f"{i + 1}. Title: {task['title']}, "
                  f"Description: {task['description']}, "
                  f"Status: {task['status']}, "
                  f"Priority: {task['priority']}, "
                  f"Deadline: {task['deadline']}")

def sort_tasks(tasks, key):
    tasks.sort(key=lambda x: x.get(key))
    print("Tasks sorted successfully.")

def get_user_choice():
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 1 <= choice <= 7:
                return choice
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def handle_user_choice(sheet, tasks, choice):
    if choice == 1:
        title = input("Enter task title: ")
        description = input("Enter task description: ")
        status = input("Enter task status (Pending, In Progress, Completed): ")
        priority = input("Enter task priority (High, Medium, Low): ")
        deadline = input("Enter task deadline (YYYY-MM-DD): ")
        add_task(sheet, tasks, title, description, status, priority, deadline)
    elif choice == 2:
        index = int(input("Enter the index of the task to update: ")) - 1
        if 0 <= index < len(tasks):
            print("Select field to update:")
            print("1. Update Title")
            print("2. Update Description")
            print("3. Update Status")
            print("4. Update Priority")
            print("5. Update Deadline")
            update_choice = input("Enter your choice: ")
            if update_choice == "1":
                title = input("Enter new title: ")
                update_task(sheet, tasks, index, title=title)
            elif update_choice == "2":
                description = input("Enter new description: ")
                update_task(sheet, tasks, index, description=description)
            elif update_choice == "3":
                status = input("Enter new status (e.g., Pending, Completed): ")
                update_task(sheet, tasks, index, status=status)
            elif update_choice == "4":
                priority = input("Enter new priority (High, Medium, Low): ")
                update_task(sheet, tasks, index, priority=priority)
            elif update_choice == "5":
                deadline = input("Enter new deadline (YYYY-MM-DD): ")
                update_task(sheet, tasks, index, deadline=deadline)
            else:
                print("Invalid choice. Please enter a valid option.")
        else:
            print("Invalid task index.")
    elif choice == 3:
        list_tasks(tasks)
    elif choice == 4:
        index = int(input("Enter the index of the task to delete: ")) - 1
        delete_task(sheet, tasks, index)
    elif choice == 5:
        filter_tasks(tasks)
    elif choice == 6:
        handle_sort_tasks(tasks)
    elif choice == 7:
        print("Exiting TaskMaster. Goodbye!")
        exit()
    else:
        print("Invalid choice. Please select a valid option.")

def handle_sort_tasks(tasks):
    print("1. Sort by Due Date")
    print("2. Sort by Priority")
    print("3. Sort by Status")
    sort_choice = input("Enter your choice: ")
    if sort_choice == "1":
        sort_tasks(tasks, 'deadline')
    elif sort_choice == "2":
        sort_tasks(tasks, 'priority')
    elif sort_choice == "3":
        sort_tasks(tasks, 'status')
    else:
        print("Invalid choice. Please enter a valid option.")

def main_menu():
    print(ascii_art_header)
    tasks = load_tasks()
    client = get_google_sheets_client()
    if client is None:
        return
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id:
        print("Error: SPREADSHEET_ID environment variable is not set.")
        return
    sheet = client.open_by_key(spreadsheet_id).worksheet('Tasks')
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
        handle_user_choice(sheet, tasks, choice)

if __name__ == "__main__":
    main_menu()

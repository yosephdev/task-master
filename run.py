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
    tasks = new_sheet.get_all_records()[1:]


def add_task(
        title,
        description,
        status='Pending',
        priority=None,
        deadline=None):
    """
    Add a new task to the task list.

    Args:
        title (str): The title of the task.
        description (str): The description of the task.
        status (str, optional): The status of the task (default is 'Pending').
        priority (str, optional): The priority of the task (default is None).
        deadline (str): The deadline of the task in 'YYYY-MM-DD' format.

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
            print(
                "Invalid format. Please enter in YYYY-MM-DD format.")
            return

    new_task = {
        'title': title,
        'description': description,
        'status': status,
        'priority': priority,
        'deadline': deadline
    }

    try:
        global new_sheet
        new_sheet.append_row(list(new_task.values()))
        print("Task added successfully.")
    except Exception as e:
        print(f"An error occurred while adding the task: {e}")


def update_task(
        index,
        title=None,
        description=None,
        status=None,
        priority=None):
    """
    Update an existing task with the given index.

    Args:
        index (int): The index of the task to update.
        title (str, optional): The new title for the task (default is None).
        description (str): The new description for the task (default is None).
        status (str, optional): The new status for the task (default is None).
        priority (str): The new priority for the task (default is None).

    Returns:
        None
    """
    global tasks

    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    if title:
        tasks[index]['title'] = title
        print("Title updated successfully.")
    if description:
        tasks[index]['description'] = description
        print("Description updated successfully.")
    if status:
        tasks[index]['status'] = status
        print("Status updated successfully.")

        new_sheet.update_cell(index + 2, 3, status)
    if priority:
        tasks[index]['priority'] = priority
        print("Priority updated successfully.")


def list_tasks():
    """
    Lists all tasks stored in the task list.

    Prints the title, description, status, deadline of each task in the list.

    Returns:
        None
    """
    print("List of Tasks:")
    rows = new_sheet.get_all_values()
    for i, row in enumerate(rows[1:], start=1):
        task = {
            'title': row[0],
            'description': row[1],
            'status': row[2],
            'deadline': row[3]
        }

        formatted_deadline = row[3]
        if formatted_deadline and formatted_deadline != "Priority":
            try:
                formatted_deadline = (
                    datetime.datetime.strptime(formatted_deadline, "%Y-%m-%d")
                    .strftime("%Y-%m-%d")
                )
            except ValueError:
                formatted_deadline = "Invalid date format"
        elif formatted_deadline == "Priority":
            formatted_deadline = "None"
        else:
            formatted_deadline = "None"

        print(f"{i}. Title: {task['title']}, "
              f"Description: {task['description']}, "
              f"Status: {task['status']}, "
              f"Deadline: {formatted_deadline}")


def delete_task(index):
    """
    Deletes a task from the task list based on the given index.

    Args:
        index (int): The index of the task to delete.

    Returns:
        None
    """
    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    global new_sheet
    new_sheet.delete_rows(index + 2)
    print("Task deleted successfully.")


def filter_tasks():
    """
    Filters tasks based on user-defined criteria.

    Provides options for filtering tasks by priority, due date, or status.
    Prints the filtered tasks based on the user's selection.

    Returns:
        None
    """
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
    """
    Filters tasks based on priority level.

    Args:
        tasks (list): List of tasks to filter.
        priority (str): Priority level to filter tasks (High, Medium, Low).

    Returns:
        None
    """
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
    """
    Filters tasks based on the due date.

    Args:
        filtered_tasks (list): List of tasks to filter.

    Returns:
        None
    """
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
    """
    Filters tasks based on the status.

    Args:
        filtered_tasks (list): List of tasks to filter.

    Returns:
        None
    """
    status = input(
        "Enter the status (e.g., Pending, In Progress, Completed): ")
    filtered_tasks = [
        task for task in filtered_tasks if task.get('status') == status
    ]

    if not filtered_tasks:
        print("No tasks matching the specified status.")
    else:
        print("Filtered Tasks:")
        for i, task in enumerate(filtered_tasks):
            print(f"{i + 1}. Title: {task['title']}, Status: {task['status']}")


def sort_tasks(sort_criteria='priority'):
    """
    Sorts tasks based on the specified criteria.

    Args:
        sort_criteria (str): Criteria to sort tasks (default is 'priority').
            Possible values: 'priority', 'status'

    Returns:
        None
    """
    global tasks
    if sort_criteria == 'priority':
        tasks.sort(key=lambda x: (x.get('priority', ''), x.get('status', '')))
    elif sort_criteria == 'status':
        tasks.sort(key=lambda x: (x.get('status', ''), x.get('priority', '')))
    else:
        print("Invalid sort criteria. Sorting by priority.")
        tasks.sort(key=lambda x: (x.get('priority', ''), x.get('status', '')))

    print("\nTasks sorted by", sort_criteria)
    list_tasks()


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


def handle_user_choice(choice):
    """
    Handles user choice and performs corresponding actions.

    Args:
        choice (int): User's choice from the main menu.

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
        add_task(title, description, status, priority, deadline)
    elif choice == 2:
        list_tasks()
        index = int(input("Enter the index of the task to update: ")) - 1

        if 0 <= index < len(tasks):
            print("1. Update Title")
            print("2. Update Description")
            print("3. Update Status")
            print("4. Update Priority")
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
            elif update_choice == "4":
                priority = input("Enter new priority: ")
                update_task(index, priority=priority)
            else:
                print("Invalid choice. Please enter a valid option.")
        else:
            print("Invalid task index.")
    elif choice == 3:
        list_all_tasks()
    elif choice == 4:
        handle_delete_task()
    elif choice == 5:
        handle_filter_tasks()
    elif choice == 6:
        handle_sort_tasks()
    elif choice == 7:
        print("Exiting TaskMaster. Goodbye!")
        exit()
    else:
        print("Invalid choice. Please select a valid option.")


def list_all_tasks():
    list_tasks()


def handle_update_task():
    list_tasks()
    index = int(input("Enter the index of the task to update: ")) - 1

    print("Number of tasks:", len(tasks))

    if 0 <= index < len(tasks):
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
    else:
        print("Invalid task index.")


def handle_delete_task():
    list_tasks()
    index = int(input("Enter the index of the task to delete: ")) - 1
    delete_task(index)


def handle_filter_tasks():
    filter_tasks()


def handle_sort_tasks():
    print("1. Sort by Due Date")
    print("2. Sort by Priority")
    print("3. Sort by Status")
    sort_choice = input("Enter your choice: ")

    if sort_choice == "1":
        sort_tasks('deadline')
    elif sort_choice == "2":
        sort_tasks('priority')
    elif sort_choice == "3":
        sort_tasks('status')
    else:
        print("Invalid choice. Please enter a valid option.")


def main_menu():
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

        choice = get_user_choice()
        handle_user_choice(choice)


if __name__ == "__main__":
    main_menu()

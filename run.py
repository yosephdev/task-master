import json
import datetime


ascii_art_header = r"""


|_   _|__ _  ___ | | __|  \/  |  __ _  ___ | |_  ___  _ __
   | | / _` |/ __|| |/ /| |\/| | / _` |/ __|| __|/ _ \| '__|
   | || (_| |\__ \|   < | |  | || (_| |\__ \| |_|  __/| |
   |_| \__,_||___/|_|\_\|_|  |_| \__,_||___/ \__|\___||_|


"""


tasks = []


def load_tasks():
    global tasks

    try:
        with open('tasks.json', 'r') as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []


def save_tasks():
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file)


def add_task(title, description, status='Pending'):
    deadline = input("Enter task deadline (YYYY-MM-DD) or leave empty: ")
    
    if deadline == "":
        deadline = None
    else:
        try:
            datetime.datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            print("Invalid deadline format. Please enter in YYYY-MM-DD format.")
            return

    new_task = {
        'title': title,
        'description': description,
        'status': status,
        "deadline": deadline
    }    
    
    tasks.append(new_task)
    save_tasks()
    print("Tasks added successfully.")


def update_task(index, title=None, description=None, status=None):
    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    task = tasks[index]
    if title is not None:
        task['title'] = title
    if description is not None:
        task['description'] = description
    if status is not None:
        task['status'] = status

    save_tasks()
    print("Task updated successfully.")


def list_tasks():
    print("List of Tasks:")
    for i, task in enumerate(tasks):
        deadline = task.get('deadline')
        formatted_deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d").strftime("%Y-%m-%d") if deadline else "None"
        print(f"{i + 1}. Title: {task['title']}, "
              f"Description: {task['description']}, "
              f"Status: {task['status']}, "
              f"Deadline: {formatted_deadline}")


def delete_task(index):
    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    del tasks[index]
    save_tasks()
    print("Task deleted successfully.")


def task_master():
    print(ascii_art_header)
    load_tasks()

    while True:
        print("\nWelcome to TaskMaster - Task Management App!")
        print("1. Add Task")
        print("2. Update Task")
        print("3. List Tasks")
        print("4. Delete Task")
        print("5. Exit")

        try:
            choice = int(input("Enter your choice: "))
            if choice < 1 or choice > 5:
                raise ValueError("Invalid choice.")
        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter a valid integer between 1 and 5.")
            continue

        if choice == 1:
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            add_task(title, description)
        elif choice == 2:
            list_tasks()
            index = int(input("Enter the index of the task to update: ")) - 1
            title = input("Enter new title: ")
            description = input("Enter new description: ")
            status = input("Enter new status: ")
            update_task(index, title, description, status)
        elif choice == 3:
            list_tasks()
        elif choice == 4:
            list_tasks()
            index = int(input("Enter the index of the task to delete: ")) - 1
            delete_task(index)
        elif choice == 5:
            print("Exiting TaskMaster. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":

    task_master()

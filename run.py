import json

tasks = []

def load_tasks():
    global tasks
    try:
        with open('tasks.json', 'r') as file:
            tasks = json.load(file)
    except FileFoundError:
        tasks = []

def save_tasks():
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file)

def add_task(title, description, status='Pending'):
    tasks.append({'title': title, 'description': description, 'status': status})
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
        print(f"{i + 1}. Title: {task['title']}, Description: {task['description']}, Status: {task['status']}")

def delete_task(index):
    if index < 0 or index >= len(tasks):
        print("Invalid task index.")
        return

    del tasks[index]
    save_tasks()
    print("Task deleted successfully.")

def task_master():
    load_tasks()

    while True:
        print("\nTaskMaster - Task Management App")
        print("1. Add Task")
        print("2. Update Task")
        print("3. List Tasks")
        print("4. Delete Task")
        print("5. Exit")

        choice = input("Enter your choice")

        if choice == '1':
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            add_task(title, description)
        elif choice == '2':
            list_tasks()
            index = int(input("Enter the index of the task to update: ")) - 1
            title = input("Enter new title (leave empty to keep unchanged): ")
            description = input("Enter new description (leave empty to keep unchanged): ")
            status = input("Enter new status (leave empty to keep unchanged): ")
            update_task(index, title, description, status)
        elif choice == '3':
            list_tasks()
        elif choice == '4':
            list_tasks()
            index = int(input("Enter the index of the task to delete: ")) - 1
            delete_task(index)
        elif choice == '5':
            print("Exiting TaskMaster. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    task_master()
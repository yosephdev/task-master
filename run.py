import json

tasks = []

def load_tasks():
    global tasks
    try:
        with open('tasks.json', r') as file:
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
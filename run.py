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
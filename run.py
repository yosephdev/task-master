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
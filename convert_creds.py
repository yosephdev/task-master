import json

# Open the creds.json file
with open('creds.json', 'r') as f:
    data = json.load(f)

# Convert the Python dictionary into a JSON string
json_str = json.dumps(data)

print(json_str)

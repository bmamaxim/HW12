import json

path = "questions.json"

with open(path, "r", encoding='utf-8') as f:
    quiz_data = json.loads(f.read())

print(quiz_data)

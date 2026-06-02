import json, re

with open('C:/ClaudeProjects/VSCodeSIMPL+Plugin/scripts/function-db.json', encoding='utf-8') as f:
    db = json.load(f)

for e in db:
    if e['name'].upper() == 'CONTINUE':
        print("=== CONTINUE example from DB ===")
        print(repr(e['example']))
        print()
        print("=== Rendered ===")
        print(e['example'])
        break

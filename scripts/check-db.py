import json

with open('C:/ClaudeProjects/VSCodeSIMPL+Plugin/scripts/function-db.json', encoding='utf-8') as f:
    db = json.load(f)

sample_cats = ['String Parsing', 'Mathematical', 'Wait Events', 'Direct Socket', 'File Functions']
shown = set()
for entry in db:
    cat = entry['category'].replace('&amp;', '&')
    match = next((s for s in sample_cats if s in cat), None)
    if match and match not in shown:
        shown.add(match)
        print('NAME:', entry['name'])
        print('CAT: ', cat)
        print('SYN: ', entry['syntax'][:150])
        print('EX:  ', entry['example'][:200])
        print()

import re
with open(r'Phase5\static\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open(r'Phase5\static\find_out.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if 'loadFormHelpers' in line:
            out.write(f"Line {i+1}: {line.strip()}\n")

import re

# Read the corrupted file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first occurrence of <!DOCTYPE html>
first_doctype = content.find('<!DOCTYPE html>')
if first_doctype == -1:
    print("No DOCTYPE found")
    exit(1)

# Find the second occurrence of <!DOCTYPE html> (the duplicate)
second_doctype = content.find('<!DOCTYPE html>', first_doctype + 1)

if second_doctype > 0:
    # Keep only the content from the second DOCTYPE onwards (the complete version)
    content = content[second_doctype:]
    print(f"Removed duplicate content. File starts at position {second_doctype}")
else:
    print("No duplicate found, file might be OK")

# Write the fixed content
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("File fixed successfully")

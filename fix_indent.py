import re

# Read the corrupted file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove leading whitespace from each line
fixed_lines = []
for line in lines:
    # Remove leading spaces/tabs but keep the line structure
    fixed_line = line.lstrip(' \t')
    # If the line is not empty, add it
    if fixed_line.strip() or not fixed_line:
        fixed_lines.append(fixed_line)

# Write the fixed content
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"Fixed {len(fixed_lines)} lines")

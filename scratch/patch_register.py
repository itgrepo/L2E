import sys

path = 'backendold/Astro_backend/app/ServiceConfig/register.py'
patch_path = 'backendold/Astro_backend/app/ServiceConfig/verify_patch.txt'

with open(path, 'r') as f:
    lines = f.readlines()

with open(patch_path, 'r') as f:
    patch_content = f.read()

# Lines to replace: 559 to 645 (1-indexed)
# In 0-indexed: lines[558:645]
start_line = 559
end_line = 645

new_lines = lines[:start_line-1] + [patch_content] + lines[end_line:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print("Successfully patched getEmailFromToken")

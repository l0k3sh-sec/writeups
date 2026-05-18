import os

LABS_DIR = "labs"

for folder in sorted(os.listdir(LABS_DIR)):
    lab_path = os.path.join(LABS_DIR, folder)
    
    if not os.path.isdir(lab_path):
        continue
    
    meta_path = os.path.join(lab_path, "meta.yml")
    
    if os.path.isfile(meta_path):
        continue
    
    # convert folder name to readable title
    name = folder.replace("-", " ").title()
    
    content = f"""name: {name}
platform: PortSwigger
difficulty: Apprentice
category: Uncategorized
"""
    
    with open(meta_path, "w") as f:
        f.write(content)
    
    print(f"created meta.yml for {folder}")

import os
import yaml

LABS_DIR = "labs"
README_PATH = os.path.join(LABS_DIR, "README.md")

labs_by_category = {}

for folder in sorted(os.listdir(LABS_DIR)):
    meta_path = os.path.join(LABS_DIR, folder, "meta.yml")
    if not os.path.isfile(meta_path):
        continue
    with open(meta_path, "r") as f:
        meta = yaml.safe_load(f)
    category = meta.get("category", "Uncategorized")
    if category not in labs_by_category:
        labs_by_category[category] = []
    labs_by_category[category].append({
        "name": meta.get("name", folder),
        "platform": meta.get("platform", "-"),
        "difficulty": meta.get("difficulty", "-"),
        "folder": folder
    })

lines = []
lines.append("# Lab Writeups Index")
lines.append("")
lines.append("All labs I've completed across various platforms.")
lines.append("")
lines.append("---")
lines.append("")

for category, labs in sorted(labs_by_category.items()):
    lines.append(f"## {category}")
    lines.append("")
    lines.append("| Lab | Platform | Difficulty | Writeup |")
    lines.append("|-----|----------|------------|---------|")
    for lab in labs:
        lines.append(f"| {lab['name']} | {lab['platform']} | {lab['difficulty']} | [→]({lab['folder']}/) |")
    lines.append("")

lines.append("---")
lines.append("*updated as I complete labs*")

with open(README_PATH, "w") as f:
    f.write("\n".join(lines))

print("index updated.")

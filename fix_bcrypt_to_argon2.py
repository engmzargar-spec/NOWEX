import os
import re
import shutil

PROJECT_ROOT = "D:/NOWEX-Platform/backend"

REPLACEMENTS = {
    r"from\s+passlib\.hash\s+import\s+bcrypt": "from passlib.hash import argon2",
    r"bcrypt\.hash": "argon2.hash",
    r"bcrypt\.verify": "argon2.verify",
}

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        backup_path = file_path + ".bak"
        shutil.copy(file_path, backup_path)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✔ Fixed: {file_path}  (backup created: {backup_path})")


def scan_project():
    print("🔍 Scanning backend/ for bcrypt usage...")

    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                process_file(full_path)

    print("\n🎉 Done! All bcrypt imports and usages replaced with argon2.")


if __name__ == "__main__":
    scan_project()

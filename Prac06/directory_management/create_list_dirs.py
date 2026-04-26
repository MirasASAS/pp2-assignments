import os
import shutil
from pathlib import Path

print("=== os.getcwd() - Current directory ===")
print(f"  {os.getcwd()}")

print("\n=== os.mkdir() - Create single directory ===")
os.makedirs("test_dir", exist_ok=True)
print("  Created: test_dir/")

print("\n=== os.makedirs() - Create nested directories ===")
os.makedirs("project/src/utils", exist_ok=True)
os.makedirs("project/data/raw", exist_ok=True)
os.makedirs("project/data/processed", exist_ok=True)
print("  Created: project/src/utils, project/data/raw, project/data/processed")

for folder in ["project/src", "project/data/raw", "project/data/processed"]:
    open(f"{folder}/sample.txt", "w").close()

print("\n=== os.listdir() - List directory contents ===")
print(f"  project/ contains: {os.listdir('project')}")
print(f"  project/data/ contains: {os.listdir('project/data')}")

print("\n=== Find files by extension ===")
for root, dirs, files in os.walk("project"):
    for file in files:
        if file.endswith(".txt"):
            print(f"  Found .txt: {os.path.join(root, file)}")

print("\n=== pathlib.Path - Modern path operations ===")
p = Path("project")
print(f"  Path exists: {p.exists()}")
print(f"  Is directory: {p.is_dir()}")
for txt_file in p.rglob("*.txt"):
    print(f"  Found via pathlib: {txt_file}")

print("\n=== os.chdir() - Change directory ===")
original = os.getcwd()
os.chdir("test_dir")
print(f"  Changed to: {os.getcwd()}")
os.chdir(original)
print(f"  Back to: {os.getcwd()}")

print("\n=== Cleanup ===")
shutil.rmtree("project")
os.rmdir("test_dir")
print("  Removed: project/, test_dir/")
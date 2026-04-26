import os
import shutil

with open("original.txt", "w") as f:
    f.write("This is the original file.\n")
    f.write("It will be copied and then deleted.\n")

print("=== shutil.copy() - Copy file ===")
shutil.copy("original.txt", "copy.txt")
print(f"Copied: original.txt -> copy.txt")
print(f"copy.txt exists: {os.path.exists('copy.txt')}")

print("\n=== shutil.copy2() - Copy with metadata ===")
shutil.copy2("original.txt", "copy_with_meta.txt")
print(f"Copied with metadata: original.txt -> copy_with_meta.txt")

print("\n=== Backup file ===")
os.makedirs("backup", exist_ok=True)
shutil.copy("original.txt", "backup/original_backup.txt")
print(f"Backup created at: backup/original_backup.txt")

print("\n=== os.rename() - Rename file ===")
os.rename("copy.txt", "renamed.txt")
print(f"Renamed: copy.txt -> renamed.txt")
print(f"renamed.txt exists: {os.path.exists('renamed.txt')}")

print("\n=== os.remove() - Delete file safely ===")
for fname in ["renamed.txt", "copy_with_meta.txt"]:
    if os.path.exists(fname):
        os.remove(fname)
        print(f"Deleted: {fname}")

print("\n=== shutil.rmtree() - Delete directory ===")
if os.path.exists("backup"):
    shutil.rmtree("backup")
    print("Deleted: backup/")

os.remove("original.txt")
print("\nAll cleanup done.")
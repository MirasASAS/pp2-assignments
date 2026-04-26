import os
import shutil

os.makedirs("source", exist_ok=True)
os.makedirs("destination", exist_ok=True)
os.makedirs("archive", exist_ok=True)

for i in range(1, 4):
    with open(f"source/file{i}.txt", "w") as f:
        f.write(f"Content of file {i}\n")
with open("source/image.png", "w") as f:
    f.write("fake image data")
with open("source/data.csv", "w") as f:
    f.write("name,age\nAlice,30\n")

print("=== shutil.move() - Move a single file ===")
shutil.move("source/file1.txt", "destination/file1.txt")
print(f"  Moved: source/file1.txt -> destination/file1.txt")

print("\n=== shutil.copy() - Copy file between directories ===")
shutil.copy("source/file2.txt", "archive/file2_backup.txt")
print(f"  Copied: source/file2.txt -> archive/file2_backup.txt")

print("\n=== Move all .txt files from source to destination ===")
for fname in os.listdir("source"):
    if fname.endswith(".txt"):
        shutil.move(f"source/{fname}", f"destination/{fname}")
        print(f"  Moved: {fname}")

print("\n=== destination/ now contains ===")
for f in os.listdir("destination"):
    print(f"  {f}")

print("\n=== source/ now contains ===")
for f in os.listdir("source"):
    print(f"  {f}")

print("\n=== shutil.copytree() - Copy entire directory ===")
if os.path.exists("destination_copy"):
    shutil.rmtree("destination_copy")
shutil.copytree("destination", "destination_copy")
print("  Copied entire destination/ -> destination_copy/")

print("\n=== Cleanup ===")
for d in ["source", "destination", "archive", "destination_copy"]:
    shutil.rmtree(d)
print("  Done.")
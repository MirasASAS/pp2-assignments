print("=== Mode 'w' - Write (creates or overwrites) ===")
with open("output.txt", "w") as f:
    f.write("First line written\n")
    f.write("Second line written\n")

with open("output.txt", "r") as f:
    print(f.read())

print("=== Mode 'a' - Append (adds to existing file) ===")
with open("output.txt", "a") as f:
    f.write("Third line appended\n")
    f.write("Fourth line appended\n")

with open("output.txt", "r") as f:
    print(f.read())

print("=== Mode 'x' - Exclusive create (fails if file exists) ===")
import os

if os.path.exists("new_file.txt"):
    os.remove("new_file.txt")

try:
    with open("new_file.txt", "x") as f:
        f.write("Created with mode x\n")
    print("File created successfully with mode 'x'")
except FileExistsError:
    print("File already exists - mode 'x' failed")

print("\n=== Writing multiple lines with writelines() ===")
lines = ["Apple\n", "Banana\n", "Cherry\n", "Date\n"]
with open("fruits.txt", "w") as f:
    f.writelines(lines)

with open("fruits.txt", "r") as f:
    print(f.read())

os.remove("output.txt")
os.remove("new_file.txt")
os.remove("fruits.txt")
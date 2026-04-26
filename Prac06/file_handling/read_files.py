with open("sample.txt", "w") as f:
    f.write("Line 1: Hello, World!\n")
    f.write("Line 2: Python file handling\n")
    f.write("Line 3: Reading files is easy\n")
    f.write("Line 4: Practice makes perfect\n")
    f.write("Line 5: Keep coding!\n")

print("=== read() - entire file at once ===")
with open("sample.txt", "r") as f:
    content = f.read()
print(content)

print("=== readline() - one line at a time ===")
with open("sample.txt", "r") as f:
    line = f.readline()
    while line:
        print(line, end="")
        line = f.readline()

print("\n\n=== readlines() - list of all lines ===")
with open("sample.txt", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    print(f"  Line {i}: {line.strip()}")

print(f"\nTotal lines: {len(lines)}")
print(f"Total characters: {sum(len(l) for l in lines)}")
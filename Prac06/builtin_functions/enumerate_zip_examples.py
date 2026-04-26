print("=== enumerate() - Index + value pairs ===")
fruits = ["apple", "banana", "cherry", "date", "elderberry"]

for index, fruit in enumerate(fruits):
    print(f"  {index}: {fruit}")

print()
for index, fruit in enumerate(fruits, start=1):
    print(f"  {index}. {fruit}")

print("\n=== enumerate() on a file (line numbers) ===")
sample_lines = [
    "Name: Alice\n",
    "Age: 30\n",
    "City: Almaty\n",
    "Job: Developer\n",
]
for line_num, line in enumerate(sample_lines, start=1):
    print(f"  Line {line_num}: {line.strip()}")

print("\n=== zip() - Pair up multiple iterables ===")
names  = ["Alice", "Bob", "Charlie", "Diana"]
ages   = [30, 25, 35, 28]
cities = ["Almaty", "London", "New York", "Paris"]

for name, age, city in zip(names, ages, cities):
    print(f"  {name} | Age: {age} | City: {city}")

print("\n=== zip() to create a dictionary ===")
keys   = ["name", "age", "language", "level"]
values = ["Alice", 30, "Python", "Intermediate"]
profile = dict(zip(keys, values))
print(f"  Profile: {profile}")

print("\n=== zip() to pair questions and answers ===")
questions = ["What is 2+2?", "Capital of France?", "Best language?"]
answers   = ["4", "Paris", "Python"]

for q, a in zip(questions, answers):
    print(f"  Q: {q}")
    print(f"  A: {a}")
    print()

print("=== Combining enumerate() and zip() ===")
products = ["Milk", "Bread", "Eggs"]
prices   = [2.99, 1.49, 5.49]

for i, (product, price) in enumerate(zip(products, prices), start=1):
    print(f"  {i}. {product:<10} ${price:.2f}")

total = sum(prices)
print(f"  {'TOTAL':<12} ${total:.2f}")

print("\n=== zip() to transpose a matrix ===")
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed = list(zip(*matrix))
print(f"  Original  : {matrix}")
print(f"  Transposed: {[list(row) for row in transposed]}")
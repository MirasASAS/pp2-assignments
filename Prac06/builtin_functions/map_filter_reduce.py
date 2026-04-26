from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
words = ["hello", "world", "python", "code", "map"]
prices = [29.99, 9.99, 49.99, 4.99, 19.99]

print("=== map() - Apply function to every item ===")
squared = list(map(lambda x: x ** 2, numbers))
print(f"  Original : {numbers}")
print(f"  Squared  : {squared}")

uppercased = list(map(str.upper, words))
print(f"  Words    : {words}")
print(f"  Uppercased: {uppercased}")

rounded_prices = list(map(lambda p: round(p), prices))
print(f"  Prices rounded: {rounded_prices}")

print("\n=== filter() - Keep items that match condition ===")
evens = list(filter(lambda x: x % 2 == 0, numbers))
odds  = list(filter(lambda x: x % 2 != 0, numbers))
print(f"  Numbers : {numbers}")
print(f"  Evens   : {evens}")
print(f"  Odds    : {odds}")

long_words = list(filter(lambda w: len(w) > 4, words))
print(f"  Words longer than 4 chars: {long_words}")

affordable = list(filter(lambda p: p < 20, prices))
print(f"  Prices under $20: {affordable}")

print("\n=== reduce() - Aggregate to single value ===")
total = reduce(lambda a, b: a + b, numbers)
print(f"  Sum of {numbers} = {total}")

product = reduce(lambda a, b: a * b, [1, 2, 3, 4, 5])
print(f"  Product of [1,2,3,4,5] = {product}")

longest = reduce(lambda a, b: a if len(a) >= len(b) else b, words)
print(f"  Longest word in {words} = '{longest}'")

total_price = reduce(lambda a, b: a + b, prices)
print(f"  Total price: ${total_price:.2f}")

print("\n=== Chaining map + filter + reduce ===")
result = reduce(
    lambda a, b: a + b,
    filter(lambda x: x > 25, map(lambda x: x ** 2, numbers))
)
print(f"  Sum of squares > 25 from {numbers}: {result}")

print("\n=== len(), sum(), min(), max() ===")
print(f"  len(numbers)  = {len(numbers)}")
print(f"  sum(numbers)  = {sum(numbers)}")
print(f"  min(numbers)  = {min(numbers)}")
print(f"  max(numbers)  = {max(numbers)}")
print(f"  min(prices)   = {min(prices)}")
print(f"  max(prices)   = {max(prices)}")

print("\n=== sorted() ===")
unsorted = [5, 2, 9, 1, 7, 3]
print(f"  sorted asc  : {sorted(unsorted)}")
print(f"  sorted desc : {sorted(unsorted, reverse=True)}")
print(f"  words by len: {sorted(words, key=len)}")

print("\n=== Type conversion functions ===")
print(f"  int('42')     = {int('42')}")
print(f"  float('3.14') = {float('3.14')}")
print(f"  str(100)      = {str(100)}")
print(f"  bool(0)       = {bool(0)}")
print(f"  bool(1)       = {bool(1)}")
print(f"  list('abc')   = {list('abc')}")
print(f"  tuple([1,2])  = {tuple([1, 2])}")
print(f"  set([1,1,2])  = {set([1, 1, 2])}")
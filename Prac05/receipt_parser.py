import re
import json

with open("raw.txt", "r") as f:
    receipt_text = f.read()

print("=" * 50)
print("        RECEIPT PARSER - RegEx Practice")
print("=" * 50)


print("\n[TASK 1] All Prices Found:")

price_pattern = r"-?\$\d+\.\d{2}"
prices = re.findall(price_pattern, receipt_text)

for price in prices:
    print(f"  {price}")


print("\n[TASK 2] Product Names:")

items_block = re.search(
    r"ITEMS PURCHASED:\n-+\n(.*?)\n-+\nSUBTOTAL",
    receipt_text,
    re.DOTALL
)

if items_block:
    items_text = items_block.group(1)
    product_pattern = r"^([A-Za-z][\w\s\(\)\-]+?)\s{2,}\$"
    products = re.findall(product_pattern, items_text, re.MULTILINE)
    for p in products:
        print(f"  - {p.strip()}")


print("\n[TASK 3] Financial Summary:")

subtotal_match = re.search(r"SUBTOTAL:\s+\$(\d+\.\d{2})", receipt_text)
tax_match      = re.search(r"TAX \([^)]+\):\s+\$(\d+\.\d{2})", receipt_text)
discount_match = re.search(r"DISCOUNT \([^)]+\):\s+-\$(\d+\.\d{2})", receipt_text)
total_match    = re.search(r"^TOTAL:\s+\$(\d+\.\d{2})", receipt_text, re.MULTILINE)

if subtotal_match:
    print(f"  Subtotal : ${subtotal_match.group(1)}")
if tax_match:
    print(f"  Tax      : ${tax_match.group(1)}")
if discount_match:
    print(f"  Discount : -${discount_match.group(1)}")
if total_match:
    print(f"  TOTAL    : ${total_match.group(1)}")

positive_prices = re.findall(r"(?<!-)\$(\d+\.\d{2})", receipt_text)
item_prices = [float(p) for p in positive_prices if float(p) < 50]
print(f"\n  Prices found (positive, <$50): {item_prices}")


print("\n[TASK 4] Date & Time:")

date_match = re.search(r"Date:\s+(\d{2}/\d{2}/\d{4})", receipt_text)
time_match = re.search(r"Time:\s+(\d{2}:\d{2}:\d{2})", receipt_text)

if date_match:
    print(f"  Date : {date_match.group(1)}")
if time_match:
    print(f"  Time : {time_match.group(1)}")


print("\n[TASK 5] Payment Information:")

pay_method = re.search(r"Payment Method:\s+([A-Z ]+?)(?=\n)", receipt_text)
card_type  = re.search(r"Card Type:\s+(\w+)", receipt_text)
card_num   = re.search(r"Card Number:\s+([\*\d\s]+)", receipt_text)
auth_num   = re.search(r"Authorization:\s+(#\w+)", receipt_text)

if pay_method:
    print(f"  Method        : {pay_method.group(1).strip()}")
if card_type:
    print(f"  Card Type     : {card_type.group(1)}")
if card_num:
    print(f"  Card Number   : {card_num.group(1).strip()}")
if auth_num:
    print(f"  Authorization : {auth_num.group(1)}")


print("\n[TASK 6] Structured JSON Output:")

store_match = re.search(r"^\s+([A-Z][A-Z\s]+[A-Z])\s*$", receipt_text, re.MULTILINE)
phone_match = re.search(r"Tel:\s+(\(?\d{3}\)?[\s\-]\d{3}[\-]\d{4})", receipt_text)

structured_items = []
if items_block:
    line_pattern = r"^([A-Za-z][\w\s\(\)\-]+?)\s{2,}\$(\d+\.\d{2})$"
    for match in re.finditer(line_pattern, items_text, re.MULTILINE):
        structured_items.append({
            "product": match.group(1).strip(),
            "price": float(match.group(2))
        })

receipt_data = {
    "store": {
        "name": store_match.group(1).strip() if store_match else "N/A",
        "phone": phone_match.group(1) if phone_match else "N/A"
    },
    "transaction": {
        "date": date_match.group(1) if date_match else "N/A",
        "time": time_match.group(1) if time_match else "N/A",
    },
    "items": structured_items,
    "totals": {
        "subtotal": float(subtotal_match.group(1)) if subtotal_match else 0,
        "tax":      float(tax_match.group(1))      if tax_match      else 0,
        "discount": float(discount_match.group(1)) if discount_match else 0,
        "total":    float(total_match.group(1))    if total_match    else 0,
    },
    "payment": {
        "method":        pay_method.group(1).strip() if pay_method else "N/A",
        "card_type":     card_type.group(1)          if card_type  else "N/A",
        "card_last4":    re.search(r"(\d{4})$", card_num.group(1).strip()).group(1)
                         if card_num else "N/A",
        "authorization": auth_num.group(1)           if auth_num   else "N/A",
    }
}

print(json.dumps(receipt_data, indent=2))


print("\n" + "=" * 50)
print("   BONUS: RegEx Concepts Demonstrated")
print("=" * 50)

sample = receipt_text

print("\n[META] Lines starting with a letter (^):")
starts_letter = re.findall(r"^[A-Za-z].+", sample, re.MULTILINE)
for line in starts_letter[:4]:
    print(f"  {line}")

print("\n[SPECIAL] All digit groups (\\d+):")
digits = re.findall(r"\d+", sample)
print(f"  First 8 groups: {digits[:8]}")

print("\n[SPECIAL] All word tokens (\\w+), first 10:")
words = re.findall(r"\w+", sample)
print(f"  {words[:10]}")

print("\n[SPECIAL] Split on whitespace (\\s+):")
first_line = "TOTAL:                     $39.66"
parts = re.split(r"\s{2,}", first_line)
print(f"  '{first_line}'  →  {parts}")

print("\n[SUB] Mask card number digits:")
masked = re.sub(r"\d(?=\d{0,3}\b)", "*", "4821")
print(f"  4821  →  {masked}")

redacted = re.sub(r"\(?\d{3}\)?[\s\-]\d{3}\-\d{4}", "[REDACTED]", sample)
phone_line = re.search(r"Tel:.+", redacted)
print(f"  {phone_line.group() if phone_line else ''}")

print("\n[MATCH vs SEARCH]")
test = "Date: 04/26/2026"
print(f"  re.match (from start) : {re.match(r'Date', test)}")
print(f"  re.match (not start)  : {re.match(r'04/26', test)}")
print(f"  re.search (anywhere)  : {re.search(r'04/26', test)}")

print("\n[FLAGS] re.IGNORECASE:")
found = re.findall(r"total", sample, re.IGNORECASE)
print(f"  'total' (any case) found {len(found)} times: {found}")

print("\n[FLAGS] re.MULTILINE — match 'TOTAL' at line start:")
ml = re.findall(r"^TOTAL", sample, re.MULTILINE)
print(f"  Matches: {ml}")

print("\n[SETS] Vowels in 'SUPERMART GROCERY':")
vowels = re.findall(r"[AEIOU]", "SUPERMART GROCERY")
print(f"  {vowels}")

print("\n[SETS] Non-digit chars in total line (\\D):")
non_digits = re.findall(r"\D", "$39.66")
print(f"  {non_digits}")

print("\n[QUANTIFIERS]")
q1 = re.findall(r'\d{2}', '04/26/2026 14:35:22')
q2 = re.findall(r'[A-Z]{2,}', sample)[:5]
q3 = re.findall(r'\d{2,4}', '04 2026 3 55 1234')
print(f"  Exactly 2 digits {{2}}    : {q1}")
print(f"  2+ uppercase {{2,}}       : {q2}")
print(f"  2-4 digits {{2,4}}        : {q3}")

print("\n" + "=" * 50)
print("  Parsing complete! See receipt_data for JSON.")
print("=" * 50)
# Practice 5 – Python RegEx & Receipt Parsing

## Overview
This practice covers Python Regular Expressions using the `re` module,
applied to a real-world receipt parsing problem.

## Files
| File | Description |
|---|---|
| `receipt_parser.py` | Main parser — all 6 tasks + bonus RegEx demos |
| `raw.txt` | Sample grocery receipt used as input |

## How to Run
```bash
python3 receipt_parser.py
```

## Tasks Completed
1. **Extract all prices** — `re.findall()` with `\$\d+\.\d{2}`
2. **Find all product names** — `re.search()` with `re.DOTALL` flag
3. **Calculate total amount** — individual `re.search()` for each line
4. **Extract date and time** — `\d{2}/\d{2}/\d{4}` and `\d{2}:\d{2}:\d{2}`
5. **Find payment method** — card type, masked number, authorization
6. **Structured JSON output** — combined result as a Python dict → JSON

## RegEx Concepts Covered
- Metacharacters: `. * + ? ^ $ [] | () \`
- Special sequences: `\d \w \s \D \W \S \A \Z`
- Sets and character classes: `[A-Z]` `[^abc]`
- Quantifiers: `{n}` `{n,}` `{n,m}`
- Functions: `re.search()` `re.findall()` `re.split()` `re.sub()` `re.match()` `re.finditer()`
- Flags: `re.IGNORECASE` `re.MULTILINE` `re.DOTALL`
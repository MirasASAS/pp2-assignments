import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="Miko0808",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        position VARCHAR(100),
        hire_date DATE
    );
""")
conn.commit()

# Insert a row
cursor.execute(
    "INSERT INTO employees (name, position, hire_date) VALUES (%s, %s, %s)",
    ("Alice", "Engineer", "2024-01-15")
)
conn.commit()

# Select and print
cursor.execute("SELECT * FROM employees")
rows = cursor.fetchall()
for row in rows:
    print(row)
    
import psycopg2
import csv

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="Miko0808",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(20) UNIQUE
    );
""")
conn.commit()

def insert_from_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO phonebook (first_name, last_name, phone)
                VALUES (%s, %s, %s)
                ON CONFLICT (phone) DO NOTHING
            """, (row['first_name'], row['last_name'], row['phone']))
    conn.commit()
    print("CSV data inserted.")

def insert_from_console():
    first = input("First name: ")
    last = input("Last name: ")
    phone = input("Phone: ")
    cursor.execute("""
        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone) DO NOTHING
    """, (first, last, phone))
    conn.commit()
    print("Contact added.")

def update_contact():
    phone = input("Enter phone of contact to update: ")
    print("What to update? 1 - First name  2 - Phone")
    choice = input("Choice: ")
    if choice == "1":
        new_name = input("New first name: ")
        cursor.execute("UPDATE phonebook SET first_name = %s WHERE phone = %s", (new_name, phone))
    elif choice == "2":
        new_phone = input("New phone: ")
        cursor.execute("UPDATE phonebook SET phone = %s WHERE phone = %s", (new_phone, phone))
    conn.commit()
    print("Contact updated.")

def query_contacts():
    print("Search by: 1 - Name  2 - Phone prefix")
    choice = input("Choice: ")
    if choice == "1":
        name = input("Enter name: ")
        cursor.execute("""
            SELECT * FROM phonebook
            WHERE first_name ILIKE %s OR last_name ILIKE %s
        """, (f"%{name}%", f"%{name}%"))
    elif choice == "2":
        prefix = input("Enter phone prefix (e.g. +7701): ")
        cursor.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (f"{prefix}%",))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("No contacts found.")

def delete_contact():
    print("Delete by: 1 - Username  2 - Phone")
    choice = input("Choice: ")
    if choice == "1":
        name = input("Enter first name: ")
        cursor.execute("DELETE FROM phonebook WHERE first_name = %s", (name,))
    elif choice == "2":
        phone = input("Enter phone: ")
        cursor.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
    conn.commit()
    print("Contact deleted.")

while True:
    print("\n--- PhoneBook ---")
    print("1. Import from CSV")
    print("2. Add contact manually")
    print("3. Update contact")
    print("4. Search contacts")
    print("5. Delete contact")
    print("6. Exit")
    choice = input("Choose: ")

    if choice == "1":
        insert_from_csv("contacts.csv")
    elif choice == "2":
        insert_from_console()
    elif choice == "3":
        update_contact()
    elif choice == "4":
        query_contacts()
    elif choice == "5":
        delete_contact()
    elif choice == "6":
        break

cursor.close()
conn.close()
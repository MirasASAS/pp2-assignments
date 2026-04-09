import json
import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Miko0808",
        host="localhost",
        port="5432"
    )
    return conn

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(20) UNIQUE
    );
""")

cursor.execute("""
CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT p.id, p.first_name, p.last_name, p.phone
        FROM phonebook p
        WHERE p.first_name ILIKE '%' || pattern || '%'
           OR p.last_name  ILIKE '%' || pattern || '%'
           OR p.phone      ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;
""")

cursor.execute("""
CREATE OR REPLACE FUNCTION get_contacts_paged(lim INT, offs INT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT p.id, p.first_name, p.last_name, p.phone
        FROM phonebook p
        ORDER BY p.id
        LIMIT lim OFFSET offs;
END;
$$ LANGUAGE plpgsql;
""")

cursor.execute("""
CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_last_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE phone = p_phone) THEN
        UPDATE phonebook SET first_name = p_first_name, last_name = p_last_name WHERE phone = p_phone;
    ELSE
        INSERT INTO phonebook (first_name, last_name, phone) VALUES (p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;
""")

cursor.execute("""
CREATE OR REPLACE PROCEDURE insert_many_contacts(p_data JSON)
LANGUAGE plpgsql AS $$
DECLARE
    item JSON;
    p_first VARCHAR;
    p_last VARCHAR;
    p_phone VARCHAR;
    invalid_list TEXT := '';
BEGIN
    FOR item IN SELECT * FROM json_array_elements(p_data)
    LOOP
        p_first := item->>'first_name';
        p_last  := item->>'last_name';
        p_phone := item->>'phone';
        IF p_phone ~ '^\+[0-9]{10,}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE phone = p_phone) THEN
                UPDATE phonebook SET first_name = p_first, last_name = p_last WHERE phone = p_phone;
            ELSE
                INSERT INTO phonebook (first_name, last_name, phone) VALUES (p_first, p_last, p_phone);
            END IF;
        ELSE
            invalid_list := invalid_list || p_first || ' ' || p_last || ' (' || p_phone || '), ';
        END IF;
    END LOOP;
    IF invalid_list <> '' THEN
        RAISE NOTICE 'Invalid entries: %', invalid_list;
    END IF;
END;
$$;
""")

cursor.execute("""
CREATE OR REPLACE PROCEDURE delete_contact(p_username VARCHAR DEFAULT NULL, p_phone VARCHAR DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_phone IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone = p_phone;
    ELSIF p_username IS NOT NULL THEN
        DELETE FROM phonebook WHERE first_name = p_username;
    END IF;
END;
$$;
""")

conn.commit()


def search(pattern):
    cursor.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cursor.fetchall()
    for row in rows:
        print(row)


def upsert(first, last, phone):
    cursor.execute("CALL upsert_contact(%s, %s, %s)", (first, last, phone))
    conn.commit()
    print("Done.")

def insert_many(data_list):
    cursor.execute("CALL insert_many_contacts(%s)", (json.dumps(data_list),))
    conn.commit()
    print("Done.")

def get_paged(limit, offset):
    cursor.execute("SELECT * FROM get_contacts_paged(%s, %s)", (limit, offset))
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def delete(username=None, phone=None):
    cursor.execute("CALL delete_contact(%s, %s)", (username, phone))
    conn.commit()
    print("Deleted.")


while True:
    print("\n--- PhoneBook v2 ---")
    print("1. Search")
    print("2. Add/Update one contact")
    print("3. Add many contacts")
    print("4. Show page")
    print("5. Delete contact")
    print("6. Exit")
    choice = input("Choose: ")

    if choice == "1":
        pattern = input("Search pattern: ")
        search(pattern)

    elif choice == "2":
        first = input("First name: ")
        last  = input("Last name: ")
        phone = input("Phone: ")
        upsert(first, last, phone)

    elif choice == "3":
        data = []
        n = int(input("How many contacts? "))
        for _ in range(n):
            first = input("First name: ")
            last  = input("Last name: ")
            phone = input("Phone: ")
            data.append({"first_name": first, "last_name": last, "phone": phone})
        insert_many(data)

    elif choice == "4":
        limit  = int(input("How many per page? "))
        offset = int(input("Skip how many? "))
        get_paged(limit, offset)

    elif choice == "5":
        print("Delete by: 1 - Name  2 - Phone")
        d = input("Choice: ")
        if d == "1":
            name = input("First name: ")
            delete(username=name)
        else:
            phone = input("Phone: ")
            delete(phone=phone)

    elif choice == "6":
        break

cursor.close()
conn.close()
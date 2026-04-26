import csv
import json
import sys
import pg8000.dbapi
from connect import get_connection


def _rows_to_dicts(cursor):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _print_contacts(rows):
    if not rows:
        print("  (no contacts found)")
        return
    print(f"  {'ID':<5} {'Name':<22} {'Email':<28} {'Birthday':<12} {'Group':<10} {'Phones'}")
    print("  " + "-" * 95)
    for r in rows:
        phones = r.get("phone_list") or r.get("phone") or ""
        print(f"  {str(r.get('id','')):<5} {str(r.get('name','')):<22} "
              f"{str(r.get('email') or ''):<28} "
              f"{str(r.get('birthday') or ''):<12} "
              f"{str(r.get('group_name') or ''):<10} {phones}")


def _ask_sort():
    print("Sort by: [1] name  [2] birthday  [3] date added (id)")
    choice = input("Choice [1]: ").strip() or "1"
    return {"1": "c.name", "2": "c.birthday NULLS LAST", "3": "c.id"}.get(choice, "c.name")


def get_groups():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM groups ORDER BY name;")
    rows = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    return rows


def search_all_fields():
    query = input("Search query: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s);", (query,))
    rows = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    print(f"\nSearch results for '{query}':")
    _print_contacts(rows)


def filter_by_group():
    groups = get_groups()
    print("\nAvailable groups:")
    for g in groups:
        print(f"  [{g['id']}] {g['name']}")
    group_name = input("Enter group name: ").strip()
    sort_col = _ask_sort()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday,
               g.name AS group_name,
               c.phone,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phone_list
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE g.name ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.phone
        ORDER BY {sort_col};
    """, (group_name,))
    rows = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    print(f"\nContacts in group '{group_name}':")
    _print_contacts(rows)


def search_by_email():
    query = input("Email search (partial): ").strip()
    sort_col = _ask_sort()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday,
               g.name AS group_name,
               c.phone,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phone_list
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.email ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.phone
        ORDER BY {sort_col};
    """, (f"%{query}%",))
    rows = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    print(f"\nResults for email '{query}':")
    _print_contacts(rows)


def paginated_browse():
    page_size = 5
    page = 1
    sort_col = _ask_sort()

    while True:
        offset = (page - 1) * page_size
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday,
                   g.name AS group_name,
                   c.phone,
                   STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ') AS phone_list
            FROM contacts c
            LEFT JOIN groups g  ON g.id  = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.phone
            ORDER BY {sort_col}
            LIMIT %s OFFSET %s;
        """, (page_size, offset))
        rows = _rows_to_dicts(cur)

        cur.execute("SELECT COUNT(*) FROM contacts;")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()

        total_pages = max(1, (total + page_size - 1) // page_size)
        print(f"\n-- Page {page}/{total_pages} --")
        _print_contacts(rows)
        print("Commands: next | prev | quit")
        cmd = input("> ").strip().lower()
        if cmd == "next":
            if page < total_pages:
                page += 1
            else:
                print("Already on last page.")
        elif cmd == "prev":
            if page > 1:
                page -= 1
            else:
                print("Already on first page.")
        elif cmd == "quit":
            break
        else:
            print("Unknown command.")


def export_to_json(filepath="contacts_export.json"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email,
               c.birthday::TEXT,
               g.name AS group_name,
               c.phone AS legacy_phone
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.name;
    """)
    contacts = _rows_to_dicts(cur)

    for contact in contacts:
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id;",
                    (contact["id"],))
        contact["phones"] = _rows_to_dicts(cur)

    cur.close()
    conn.close()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(contacts)} contacts to '{filepath}'.")


def _resolve_group(cur, group_name):
    if not group_name:
        return None
    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                (group_name,))
    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


def import_from_json(filepath="contacts_export.json"):
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return

    conn = get_connection()
    cur = conn.cursor()
    for contact in data:
        name = contact.get("name", "").strip()
        if not name:
            continue
        cur.execute("SELECT id FROM contacts WHERE name = %s;", (name,))
        existing = cur.fetchone()
        contact_id = None
        if existing:
            print(f"Duplicate found: '{name}'")
            choice = input("  [s]kip / [o]verwrite? ").strip().lower()
            if choice != "o":
                print(f"  Skipping '{name}'.")
                continue
            contact_id = existing[0]
            cur.execute("""
                UPDATE contacts SET email=%s, birthday=%s, phone=%s WHERE id=%s;
            """, (contact.get("email"), contact.get("birthday"),
                  contact.get("legacy_phone"), contact_id))
        else:
            group_id = _resolve_group(cur, contact.get("group_name"))
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, phone, group_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (name, contact.get("email"), contact.get("birthday"),
                  contact.get("legacy_phone"), group_id))
            contact_id = cur.fetchone()[0]

        if contact_id:
            cur.execute("DELETE FROM phones WHERE contact_id = %s;", (contact_id,))
            for ph in contact.get("phones", []):
                cur.execute("""
                    INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);
                """, (contact_id, ph.get("phone"), ph.get("type")))

    conn.commit()
    cur.close()
    conn.close()
    print("JSON import complete.")


def import_from_csv(filepath="contacts.csv"):
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return

    inserted = skipped = 0
    conn = get_connection()
    cur = conn.cursor()
    for row in rows:
        name = row.get("name", "").strip()
        if not name:
            continue
        cur.execute("SELECT id FROM contacts WHERE name = %s;", (name,))
        if cur.fetchone():
            skipped += 1
            continue
        group_id = _resolve_group(cur, row.get("group", "").strip() or None)
        birthday = row.get("birthday", "").strip() or None
        email    = row.get("email", "").strip() or None
        phone    = row.get("phone", "").strip() or None
        cur.execute("""
            INSERT INTO contacts (name, email, birthday, phone, group_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (name, email, birthday, phone, group_id))
        contact_id = cur.fetchone()[0]
        phone_type = row.get("phone_type", "").strip()
        if phone and phone_type in ("home", "work", "mobile"):
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);
            """, (contact_id, phone, phone_type))
        inserted += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"CSV import: {inserted} inserted, {skipped} skipped.")


def call_add_phone():
    contact_name = input("Contact name: ").strip()
    phone        = input("Phone number: ").strip()
    phone_type   = input("Type (home/work/mobile): ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL add_phone(%s, %s, %s);", (contact_name, phone, phone_type))
    conn.commit()
    cur.close()
    conn.close()
    print("Phone added.")


def call_move_to_group():
    contact_name = input("Contact name: ").strip()
    group_name   = input("Group name: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL move_to_group(%s, %s);", (contact_name, group_name))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Moved '{contact_name}' to group '{group_name}'.")


MENU = """
+==========================================+
|       TSIS 1 - PhoneBook Extended        |
+==========================================+
|  Search & Filter                         |
|  1. Search all fields (DB function)      |
|  2. Filter by group                      |
|  3. Search by email                      |
|  4. Browse with pagination               |
+==========================================+
|  Import / Export                         |
|  5. Export contacts to JSON              |
|  6. Import contacts from JSON            |
|  7. Import contacts from CSV             |
+==========================================+
|  Phone & Group Management                |
|  8. Add phone to contact                 |
|  9. Move contact to group                |
+==========================================+
|  0. Exit                                 |
+==========================================+
"""


def main():
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        try:
            if   choice == "1": search_all_fields()
            elif choice == "2": filter_by_group()
            elif choice == "3": search_by_email()
            elif choice == "4": paginated_browse()
            elif choice == "5":
                fp = input("Output file [contacts_export.json]: ").strip() or "contacts_export.json"
                export_to_json(fp)
            elif choice == "6":
                fp = input("JSON file [contacts_export.json]: ").strip() or "contacts_export.json"
                import_from_json(fp)
            elif choice == "7":
                fp = input("CSV file [contacts.csv]: ").strip() or "contacts.csv"
                import_from_csv(fp)
            elif choice == "8": call_add_phone()
            elif choice == "9": call_move_to_group()
            elif choice == "0":
                print("Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice.")
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted.")
            sys.exit(0)


if __name__ == "__main__":
    main()
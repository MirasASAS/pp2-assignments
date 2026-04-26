import psycopg2

def get_connection():
    conn = psycopg2.connect(
        "host=127.0.0.1 dbname=phonebook user=postgres password=Miko0808"
    )
    conn.set_client_encoding('UTF8')
    return conn
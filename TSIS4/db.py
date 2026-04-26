import pg8000.dbapi
from config import DB_CONFIG


def get_conn():
    return pg8000.dbapi.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
    )


def init_db():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id;",
                    (username,))
        pid = cur.fetchone()[0]
        conn.commit()
    cur.close()
    conn.close()
    return pid


def save_session(player_id, score, level_reached):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s);
    """, (player_id, score, level_reached))
    conn.commit()
    cur.close()
    conn.close()


def get_leaderboard():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached,
               gs.played_at::TEXT
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_personal_best(player_id):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT MAX(score) FROM game_sessions WHERE player_id = %s;
    """, (player_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row and row[0] else 0
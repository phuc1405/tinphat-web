import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")


# ================= CONNECT DB =================
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


# ================= INIT DATABASE =================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            price INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_log (
            id SERIAL PRIMARY KEY,
            product_id INTEGER,
            action TEXT,
            quantity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
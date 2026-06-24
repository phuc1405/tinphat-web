import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    if not DATABASE_URL:
        raise Exception("Missing DATABASE_URL")

    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # PRODUCTS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            price INTEGER DEFAULT 0
        )
    """)

    # STOCK LOG (quan trọng nhất)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_log (
            id SERIAL PRIMARY KEY,
            product_id INTEGER,
            action TEXT,
            quantity INTEGER,
            price INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
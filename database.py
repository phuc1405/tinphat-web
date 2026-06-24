import os
import psycopg2
import os
import psycopg2



DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    print("DEBUG DB:", DATABASE_URL)

    if not DATABASE_URL:
        raise Exception("Không đọc được DATABASE_URL")

    return psycopg2.connect(DATABASE_URL)


# ================= INIT DATABASE =================
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

    # STOCK LOG (lịch sử nhập/xuất)
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
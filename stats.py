import sqlite3

def get_earnings():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(total_price) FROM exports")
    total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(total_price)
        FROM exports
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m','now')
    """)
    monthly = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(total_price)
        FROM exports
        WHERE strftime('%Y', date) = strftime('%Y','now')
    """)
    yearly = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total": total,
        "monthly": monthly,
        "yearly": yearly
    }
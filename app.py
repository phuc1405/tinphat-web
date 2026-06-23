from flask import Flask, render_template, request, redirect, session, send_file
from database import init_db, get_db
import pandas as pd
from docx import Document
import os

app = Flask(__name__)
app.secret_key = "erp_pro_max"

init_db()

users = {
    "admin": {"password": "123456", "role": "admin"},
    "kho1": {"password": "123456", "role": "warehouse"},
    "sale1": {"password": "123456", "role": "sales"}
}

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u]["password"] == p:
            session["user"] = u
            session["role"] = users[u]["role"]
            return redirect("/dashboard")

        return render_template("login.html", error="Sai tài khoản")

    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    total_items = cur.fetchone()[0]

    cur.execute("SELECT SUM(quantity) FROM products")
    total_stock = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM products WHERE quantity < 5")
    low_stock = cur.fetchone()[0]

    cur.execute("""
        SELECT SUM(stock_log.quantity * products.price)
        FROM stock_log
        JOIN products ON stock_log.product_id = products.id
        WHERE stock_log.action = 'SELL'
    """)
    revenue = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT category, COUNT(*)
        FROM products
        GROUP BY category
    """)

    rows = cur.fetchall()

    pie_labels = [r[0] for r in rows]
    pie_values = [r[1] for r in rows]

    conn.close()

    return render_template(
        "dashboard.html",
        total_items=total_items,
        total_stock=total_stock,
        low_stock=low_stock,
        today_income=revenue,
        month_income=revenue,
        pie_labels=pie_labels,
        pie_values=pie_values
    )


# ================= PRODUCTS =================
@app.route("/products", methods=["GET", "POST"])
def products():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        quantity = int(request.form["quantity"])
        price = int(request.form["price"])

        # FIX POSTGRESQL SYNTAX
        cur.execute("""
            INSERT INTO products(name, category, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (name, category, quantity, price))

    search = request.args.get("search")

    if search:
        cur.execute("SELECT * FROM products WHERE name LIKE %s", ('%' + search + '%',))
    else:
        cur.execute("SELECT * FROM products")

    data = cur.fetchall()

    conn.commit()
    conn.close()

    return render_template("products.html", products=data)


# ================= SELL =================
@app.route("/sell/<int:id>", methods=["POST"])
def sell(id):
    conn = get_db()
    cur = conn.cursor()

    qty = int(request.form["quantity"])

    cur.execute("SELECT quantity FROM products WHERE id=%s", (id,))
    item = cur.fetchone()

    if item and item[0] >= qty:

        cur.execute("""
            UPDATE products
            SET quantity = quantity - %s
            WHERE id=%s
        """, (qty, id))

        cur.execute("""
            INSERT INTO stock_log(product_id, action, quantity)
            VALUES (%s, 'SELL', %s)
        """, (id, qty))

    conn.commit()
    conn.close()

    return redirect("/products")


# ================= IMPORT =================
@app.route("/import/<int:id>", methods=["POST"])
def import_stock(id):
    conn = get_db()
    cur = conn.cursor()

    qty = int(request.form["quantity"])

    cur.execute("""
        UPDATE products
        SET quantity = quantity + %s
        WHERE id=%s
    """, (qty, id))

    cur.execute("""
        INSERT INTO stock_log(product_id, action, quantity)
        VALUES (%s, 'IMPORT', %s)
    """, (id, qty))

    conn.commit()
    conn.close()

    return redirect("/products")


# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/products")


# ================= EXPORT EXCEL =================
@app.route("/export/excel")
def export_excel():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, category, quantity, price FROM products")
    data = cur.fetchall()

    df = pd.DataFrame(data, columns=["name", "category", "quantity", "price"])

    file_path = "products.xlsx"
    df.to_excel(file_path, index=False)

    conn.close()

    return send_file(file_path, as_attachment=True)


# ================= EXPORT WORD =================
@app.route("/export/word")
def export_word():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, category, quantity, price FROM products")
    data = cur.fetchall()

    doc = Document()
    doc.add_heading("Báo cáo kho hàng", 0)

    for row in data:
        doc.add_paragraph(f"{row[0]} | {row[1]} | SL: {row[2]} | Giá: {row[3]}")

    file_path = "products.docx"
    doc.save(file_path)

    conn.close()

    return send_file(file_path, as_attachment=True)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
from db import get_conn

def add_product(name, category, price, stock):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
              (name, category, price, stock))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_product(product_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

import sqlite3
from db import DB_NAME

def create_purchase_order(supplier, items, total_quantity):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Thêm đơn nhập hàng
    c.execute("""
        INSERT INTO purchase_orders (supplier, total, date)
        VALUES (?, ?, datetime('now'))
    """, (supplier, total_quantity))
    order_id = c.lastrowid

    for item in items:
        c.execute("""
            INSERT INTO purchase_items (purchase_order_id, product_id, quantity, cost)
            VALUES (?, ?, ?, ?)
        """, (order_id, item["id"], item["quantity"], 0))  # cost mặc định là 0

        # Cập nhật tồn kho
        c.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE id = ?
        """, (item["quantity"], item["id"]))

    conn.commit()
    conn.close()


import sqlite3
from db import DB_NAME

def get_purchase_orders_with_items():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT po.id, po.supplier, po.date, 
               pi.product_id, p.name, pi.quantity
        FROM purchase_orders po
        JOIN purchase_items pi ON po.id = pi.purchase_order_id
        JOIN products p ON pi.product_id = p.id
        ORDER BY po.date DESC
    """)
    results = c.fetchall()
    conn.close()
    return results

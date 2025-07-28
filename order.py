from db import get_conn
from debt import add_debt
from datetime import datetime

def create_order(customer, items, total):
    conn = get_conn()
    c = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Ghi đơn hàng
        c.execute("INSERT INTO orders (customer, total, date) VALUES (?, ?, ?)", (customer, total, now))
        order_id = c.lastrowid

        if not order_id:
            raise Exception("❌ Không lấy được order_id sau khi tạo đơn hàng.")

        # Ghi chi tiết đơn hàng
        for item in items:
            c.execute("""
                INSERT INTO order_details (order_ref, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item['id'], item['quantity'], item['price']))

            # Trừ tồn kho
            c.execute("""
                UPDATE products SET stock = stock - ? WHERE id = ?
            """, (item['quantity'], item['id']))

        conn.commit()
        print("✅ Đã tạo đơn hàng thành công.")
        

    except Exception as e:
        print("❌ Lỗi khi tạo đơn hàng:", e)
        

    finally:
        conn.close()
    if total > 0:
        add_debt(customer, total, note="Tự động ghi nợ từ đơn hàng")

def get_orders(start_date=None, end_date=None, customer=None):
    conn = get_conn()
    c = conn.cursor()

    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    if start_date:
        query += " AND date >= ?"
        params.append(start_date + " 00:00:00")
    if end_date:
        query += " AND date <= ?"
        params.append(end_date + " 23:59:59")
    if customer:
        query += " AND customer LIKE ?"
        params.append(f"%{customer}%")

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows
from db import get_conn

def get_order_items(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT oi.product_id, p.name, oi.quantity, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,))
    return c.fetchall()

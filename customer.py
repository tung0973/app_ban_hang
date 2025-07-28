from db import get_conn

def add_customer(name):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO customers (name) VALUES (?)", (name,))
        conn.commit()
    except:
        pass  # Đã tồn tại
    conn.close()

def get_all_customers():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name FROM customers ORDER BY name")
    result = [row[0] for row in c.fetchall()]
    conn.close()
    return result

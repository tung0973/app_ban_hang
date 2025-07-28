import sqlite3
from db import get_conn

# ✅ Thêm công nợ mới
def add_debt(customer, amount, note=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO debts (customer, amount, note, date)
        VALUES (?, ?, ?, datetime('now'))
    """, (customer, amount, note))
    conn.commit()
    conn.close()

# ✅ Lấy tất cả công nợ
def get_debts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM debts ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ✅ Xoá công nợ (nếu cần)
def delete_debt(debt_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
    conn.commit()
    conn.close()

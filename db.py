import sqlite3

DB_NAME = "database.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Bảng người dùng
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Bảng sản phẩm
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    # Bảng đơn hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            total REAL,
            date TEXT
        )
    ''')

    # Chi tiết đơn hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')

    # Bảng công nợ
    c.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            amount REAL,
            note TEXT,
            date TEXT
        )
    ''')

    # Bảng khách hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # ✅ Bảng đơn nhập hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT,
            total REAL,
            date TEXT
        )
    ''')

    # ✅ Bảng chi tiết đơn nhập
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            cost REAL,
            FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')

    conn.commit()
    conn.close()

import sqlite3
from db import DB_NAME

def create_purchase_order(supplier, items):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Tạo bảng nếu chưa có
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(order_id) REFERENCES purchase_orders(id)
        )
    """)

    # Thêm đơn nhập hàng
    c.execute("INSERT INTO purchase_orders (supplier) VALUES (?)", (supplier,))
    order_id = c.lastrowid

    # Thêm từng sản phẩm và cập nhật tồn kho
    for item in items:
        c.execute("""
            INSERT INTO purchase_items (order_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (order_id, item["id"], item["quantity"]))

        # Cập nhật tồn kho
        c.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE id = ?
        """, (item["quantity"], item["id"]))

    conn.commit()
    conn.close()


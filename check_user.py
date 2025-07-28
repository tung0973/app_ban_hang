import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()
rows = c.execute("SELECT username, password, role FROM users").fetchall()
conn.close()

for row in rows:
    print(f"Tên đăng nhập: {row[0]}, Mật khẩu mã hóa: {row[1][:20]}..., Quyền: {row[2]}")

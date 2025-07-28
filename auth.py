import sqlite3
from bcrypt import checkpw
from db import DB_NAME

def login(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        hashed_pw, role = result
        if checkpw(password.encode(), hashed_pw):
            return True, role
    return False, None

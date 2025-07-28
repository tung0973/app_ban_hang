from db import init_db, add_test_user
from auth import login

# Tạo database và người dùng test
init_db()
add_test_user()

# Đăng nhập thử
print("Đăng nhập thử: admin / admin123")
user = input("Tên đăng nhập: ")
pwd = input("Mật khẩu: ")

success, role = login(user, pwd)

if success:
    print(f"✅ Đăng nhập thành công với vai trò: {role}")
else:
    print("❌ Sai tên đăng nhập hoặc mật khẩu")

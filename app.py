import streamlit as st
import pandas as pd
from auth import login
from db import init_db
from product import add_product, get_all_products
from order import create_order, get_orders, get_order_items
from debt import add_debt, get_debts
from datetime import date

init_db()
st.set_page_config(page_title="App Bán Hàng", layout="centered")

# Khởi tạo session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# Giao diện đăng nhập
if not st.session_state.logged_in:
    st.title("🔐 Đăng nhập hệ thống")
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        success, role = login(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
        else:
            st.error("❌ Sai tên đăng nhập hoặc mật khẩu")
else:
    st.sidebar.title("📋 MENU")
    menu = st.sidebar.radio("📌 Chọn chức năng", [
        "📦 Quản lý sản phẩm",
        "🧾 Bán hàng",
        "📋 Hóa đơn",
        "💳 Công nợ"
    ])

    st.markdown(f"**👤 Xin chào:** {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # Quản lý sản phẩm
    if menu == "📦 Quản lý sản phẩm":
        st.header("📦 Quản lý sản phẩm")
        products = get_all_products()
        if products:
            df = pd.DataFrame(products, columns=["ID", "Tên", "Danh mục", "Giá", "Tồn"])
            df["Giá"] = df["Giá"].apply(lambda x: f"{x:,.0f} đ")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Chưa có sản phẩm.")

        with st.expander("➕ Thêm sản phẩm mới"):
            name = st.text_input("Tên sản phẩm")
            category = st.text_input("Danh mục")
            price = st.number_input("Giá bán", min_value=0.0)
            stock = st.number_input("Tồn kho", min_value=0)
            if st.button("Thêm sản phẩm"):
                add_product(name, category, price, stock)
                st.success("✅ Đã thêm sản phẩm")
                st.rerun()

    # Bán hàng
    elif menu == "🧾 Bán hàng":
        st.header("🧾 Tạo đơn hàng")
        products = get_all_products()
        if not products:
            st.warning("⚠️ Chưa có sản phẩm.")
        else:
            cart = []
            for p in products:
                qty = st.number_input(f"{p[1]} ({p[2]}) - Tồn {p[4]}", 0, p[4], key=f"p_{p[0]}")
                if qty > 0:
                    cart.append({"id": p[0], "name": p[1], "quantity": qty, "price": p[3]})
            if cart:
                total = sum(i["quantity"] * i["price"] for i in cart)
                customer = st.text_input("Tên khách hàng")
                st.markdown(f"**Tổng tiền:** {total:,.0f} đ")
                payment = st.number_input("💵 Khách thanh toán", min_value=0.0, max_value=float(total), value=0.0)
                if st.button("💾 Lưu đơn hàng"):
                    create_order(customer, cart, total)
                    if payment < total:
                        add_debt(customer, total - payment, "Tự động ghi nợ đơn hàng")
                    st.success("✅ Đã lưu đơn hàng")
                    st.rerun()

    # Hóa đơn
    elif menu == "📋 Hóa đơn":
        st.header("📋 Tra cứu hóa đơn")
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("Từ ngày", date.today())
        with col2:
            end = st.date_input("Đến ngày", date.today())
        customer_filter = st.text_input("Tên khách hàng")
        orders = get_orders(str(start), str(end), customer_filter)
        if orders:
            for o in orders:
                with st.expander(f"🧾 HĐ#{o[0]} - {o[1]} ({o[3]})"):
                    st.markdown(f"- Khách hàng: **{o[1]}**")
                    st.markdown(f"- Ngày: {o[3]}")
                    st.markdown(f"- Tổng tiền: **{o[2]:,.0f} đ**")
                    items = get_order_items(o[0])
                    for i in items:
                        st.write(f"• {i[1]} x {i[2]} - {i[3]:,.0f} đ")

        else:
            st.warning("Không tìm thấy hóa đơn.")

    # Công nợ
    elif menu == "💳 Công nợ":
        st.header("💳 Quản lý công nợ")
        debts = get_debts()
        if debts:
            df = pd.DataFrame(debts, columns=["ID", "Khách", "Số tiền", "Ghi chú", "Ngày"])
            df["Số tiền"] = df["Số tiền"].apply(lambda x: f"{x:,.0f} đ")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Không có công nợ.")

        with st.expander("➕ Ghi nhận công nợ"):
            customer = st.text_input("👤 Khách hàng")
            amount = st.number_input("💰 Số tiền", min_value=0.0)
            note = st.text_input("📝 Ghi chú")
            if st.button("📥 Lưu công nợ"):
                add_debt(customer, amount, note)
                st.success("✅ Đã thêm công nợ")
                st.rerun()

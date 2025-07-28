import streamlit as st
import pandas as pd
from auth import login
from db import init_db
from product import add_product, get_all_products
from purchase import create_purchase_order
from purchase import get_purchase_orders_with_items
from order import create_order, get_orders, get_order_items
from debt import add_debt, get_debts
from datetime import date
from customer import add_customer, get_all_customers  # thêm dòng này ở đầu


# Khởi tạo database
init_db()
st.set_page_config(page_title="App Bán Hàng", layout="wide", initial_sidebar_state="auto")

# Session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# ------------------------------
# 🔐 Đăng nhập
# ------------------------------
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

# ------------------------------
# ✅ Giao diện chính
# ------------------------------
else:
    st.sidebar.title("📋 MENU")
    menu = st.sidebar.radio("📌 Chọn chức năng", [
        "📦 Quản lý sản phẩm",
        "🧾 Bán hàng",
        "📥 Đơn nhập hàng",
        "📋 Hóa đơn",
        "💳 Công nợ"
    ])

    st.success(f"Xin chào {st.session_state.username} ({st.session_state.role})")

    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # ------------------------------
    # 📦 Quản lý sản phẩm
    # ------------------------------
    if menu == "📦 Quản lý sản phẩm":
        st.markdown("## 📦 Quản lý sản phẩm")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("### ➕ Thêm sản phẩm")
            name = st.text_input("Tên sản phẩm")
            category = st.text_input("Danh mục")
            price = st.number_input("Giá bán", min_value=0.0)
            stock = st.number_input("Tồn kho", min_value=0)

            if st.button("Thêm sản phẩm"):
                add_product(name, category, price, stock)
                st.success("✅ Đã thêm sản phẩm")
                st.rerun()

        with col2:
            st.markdown("### 📋 Danh sách sản phẩm")
            products = get_all_products()
            if products:
                df = pd.DataFrame(products, columns=["ID", "Tên sản phẩm", "Danh mục", "Giá", "Tồn kho"])
                df["Giá"] = df["Giá"].apply(lambda x: f"{x:,.0f} đ")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("🛒 Chưa có sản phẩm nào.")

    # ------------------------------
    # 🧾 Bán hàng
    # ------------------------------
    elif menu == "🧾 Bán hàng":
        st.markdown("## 🧾 Tạo đơn hàng mới")

        products = get_all_products()
        if not products:
            st.warning("⚠️ Chưa có sản phẩm nào.")
        else:
        # Khởi tạo session cart
            if "cart" not in st.session_state:
                st.session_state.cart = []

        # Danh sách khách hàng
            customers = get_all_customers()
            selected = st.selectbox("👤 Chọn khách hàng", customers + ["➕ Khách mới"])
            if selected == "➕ Khách mới":
                customer = st.text_input("Nhập tên khách hàng mới")
            else:
             customer = selected

        # Thêm sản phẩm vào giỏ
            product_options = {f"{p[1]} - ({p[2]}) - tồn: {p[4]}": p for p in products}
            selected_label = st.selectbox("🔍 Chọn sản phẩm", list(product_options.keys()))
            selected_product = product_options[selected_label]

            quantity = st.number_input("Số lượng", min_value=1, max_value=selected_product[4], step=1)
            if st.button("➕ Thêm vào giỏ hàng"):
                st.session_state.cart.append({
                    "id": selected_product[0],
                    "name": selected_product[1],
                    "quantity": quantity,
                    "price": selected_product[3]
                })
                st.success(f"Đã thêm {selected_product[1]} ({quantity}) vào giỏ hàng")

        # Hiển thị giỏ hàng
            if st.session_state.cart:
                st.subheader("🛒 Giỏ hàng")
                df = pd.DataFrame(st.session_state.cart)
                df["Thành tiền"] = df["quantity"] * df["price"]
                df["price"] = df["price"].apply(lambda x: f"{x:,.0f} đ")
                df["Thành tiền"] = df["Thành tiền"].apply(lambda x: f"{x:,.0f} đ")
                st.dataframe(df[["name", "quantity", "price", "Thành tiền"]], use_container_width=True)

                total = sum(item["quantity"] * item["price"] for item in st.session_state.cart)
                st.write(f"**Tổng tiền:** {total:,.0f} đ")
                payment = st.number_input("💵 Khách thanh toán", min_value=0.0, max_value=float(total), value=0.0)
                debt_amount = total - payment

            if st.button("💾 Lưu đơn hàng"):
                if customer:
                    add_customer(customer)
                    create_order(customer, st.session_state.cart, total)
                    if debt_amount > 0:
                        add_debt(customer, debt_amount, note="Nợ sau khi mua hàng")
                    st.success("✅ Đơn hàng đã được lưu")
                    st.session_state.cart = []  # clear cart
                    st.rerun()
                else:
                    st.error("❌ Vui lòng nhập tên khách hàng")

    elif menu == "📥 Đơn nhập hàng":
        st.subheader("📥 Nhập hàng")

        supplier = st.text_input("🏢 Nhà cung cấp")
        all_products = get_all_products()

        if not all_products:
            st.warning("⚠️ Chưa có sản phẩm nào.")
        else:
        # Tìm kiếm sản phẩm
            keyword = st.text_input("🔍 Tìm sản phẩm theo tên").lower()
            matched_products = [p for p in all_products if keyword in p[1].lower()]

            if not matched_products:
                st.info("🔎 Không tìm thấy sản phẩm.")
            else:
                if "purchase_cart" not in st.session_state:
                    st.session_state.purchase_cart = []

                for product in matched_products:
                    col1, col2, col3 = st.columns([4, 2, 2])
                    with col1:
                        st.write(f"**{product[1]}** - {product[2]} - Tồn kho: {product[4]}")
                    with col2:
                        qty = st.number_input(
                        f"Số lượng nhập ({product[1]})",
                        min_value=0,
                        key=f"purchase_qty_{product[0]}"
                    )
                    with col3:
                        if st.button("➕ Thêm vào giỏ", key=f"add_to_cart_{product[0]}"):
                            st.session_state.purchase_cart.append({
                                "id": product[0],
                                "name": product[1],
                                "quantity": qty
                        })
                            st.success(f"✅ Đã thêm {product[1]} vào giỏ")

            # Hiển thị giỏ hàng
            if st.session_state.purchase_cart:
                st.markdown("---")
                st.subheader("🛒 Giỏ hàng nhập")
                for item in st.session_state.purchase_cart:
                    st.write(f"{item['name']} - SL: {item['quantity']}")

                if st.button("📥 Lưu đơn nhập", key="save_purchase_button"):
                    total_quantity = sum(item["quantity"] for item in st.session_state.purchase_cart)
                    create_purchase_order(supplier, st.session_state.purchase_cart, total_quantity)
                    st.success("✅ Đã lưu đơn nhập hàng")
                    st.session_state.purchase_cart = []
                    st.rerun()
        st.markdown("---")
        st.subheader("📦 Lịch sử đơn nhập")

        orders = get_purchase_orders_with_items()
        if orders:
            df = pd.DataFrame(orders, columns=["Mã đơn", "Nhà cung cấp", "Ngày", "Mã SP", "Tên sản phẩm", "SL"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Không có đơn nhập nào.")

    # ------------------------------
    # 📋 Hóa đơn
    # ------------------------------
    elif menu == "📋 Hóa đơn":
        st.markdown("## 📋 Tra cứu hóa đơn")
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("📅 Từ ngày", value=date.today())
        with col2:
            end_date = st.date_input("📅 Đến ngày", value=date.today())
        with col3:
            customer_filter = st.text_input("👤 Tên khách hàng")

        orders = get_orders(str(start_date), str(end_date), customer_filter)
        if orders:
            df = pd.DataFrame(orders, columns=["Mã đơn", "Khách hàng", "Tổng tiền", "Ngày tạo"])
            df["Tổng tiền"] = df["Tổng tiền"].apply(lambda x: f"{x:,.0f} đ")
            st.dataframe(df, use_container_width=True)

            st.markdown("### 🧾 Chi tiết đơn")
            for order in orders:
                with st.expander(f"🧾 Đơn #{order[0]} - {order[1]} - {order[3]}"):
                    items = get_order_items(order[0])
                    item_df = pd.DataFrame(items, columns=["Mã SP", "Tên SP", "Số lượng", "Giá"])
                    item_df["Giá"] = item_df["Giá"].apply(lambda x: f"{x:,.0f} đ")
                    st.dataframe(item_df, use_container_width=True)
        else:
            st.warning("Không có hóa đơn nào.")

    # ------------------------------
    # 💳 Công nợ
    # ------------------------------
    elif menu == "💳 Công nợ":
        st.markdown("## 💳 Công nợ")
        debts = get_debts()
        if debts:
            df = pd.DataFrame(debts, columns=["ID", "Khách hàng", "Số tiền", "Ghi chú", "Ngày"])
            df["Số tiền"] = df["Số tiền"].apply(lambda x: f"{x:,.0f} đ")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("❗Không có dữ liệu công nợ.")

        st.markdown("---")
        st.subheader("➕ Ghi nhận công nợ")
        customer = st.text_input("👤 Khách hàng")
        amount = st.number_input("💵 Số tiền", min_value=0.0)
        note = st.text_input("📝 Ghi chú")
        if st.button("📥 Lưu công nợ"):
            add_debt(customer, amount, note)
            st.success("✅ Đã thêm công nợ")
            st.rerun()

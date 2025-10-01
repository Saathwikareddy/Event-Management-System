import streamlit as st
from src.services import product_service, order_service, customer_service

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Retail Inventory & Order Management",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛒 Retail Inventory & Order Management")

# ------------------- SIDEBAR NAV -------------------
menu = st.sidebar.radio(
    "📌 Navigate",
    ["Dashboard", "Products", "Orders", "Customers"]
)

# ------------------- DASHBOARD -------------------
if menu == "Dashboard":
    st.header("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_products = len(product_service.list_products())
        st.metric("Total Products", total_products)

    with col2:
        total_orders = len(order_service.list_orders())
        st.metric("Total Orders", total_orders)

    with col3:
        total_customers = len(customer_service.list_customers())
        st.metric("Total Customers", total_customers)

# ------------------- PRODUCTS -------------------
elif menu == "Products":
    st.header("📦 Manage Products")

    # Refresh button
    if st.button("🔄 Refresh Products"):
        st.experimental_rerun()

    products = product_service.list_products()

    # Show products in a table
    if products:
        st.subheader("Available Products")
        st.dataframe(products)
    else:
        st.info("No products found.")

    # Add product form
    st.subheader("➕ Add New Product")
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name")
            sku = st.text_input("SKU")
            category = st.text_input("Category")
        with col2:
            price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
            stock = st.number_input("Stock", min_value=0, step=1)

        submitted = st.form_submit_button("Add Product")
        if submitted:
            try:
                product_service.add_product(name, sku, price, int(stock), category)
                st.success(f"✅ Product '{name}' added successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Failed to add product: {e}")

# ------------------- ORDERS -------------------
elif menu == "Orders":
    st.header("📝 Manage Orders")

    orders = order_service.list_orders()
    if orders:
        st.subheader("All Orders")
        st.dataframe(orders)
    else:
        st.info("No orders available.")

    st.subheader("➕ Create New Order")
    with st.form("add_order_form"):
        customer_id = st.text_input("Customer ID")
        product_id = st.text_input("Product ID")
        quantity = st.number_input("Quantity", min_value=1, step=1)

        if st.form_submit_button("Create Order"):
            try:
                order_service.create_order(customer_id, product_id, quantity)
                st.success("✅ Order created successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Failed to create order: {e}")

# ------------------- CUSTOMERS -------------------
elif menu == "Customers":
    st.header("👤 Manage Customers")

    customers = customer_service.list_customers()
    if customers:
        st.subheader("All Customers")
        st.dataframe(customers)
    else:
        st.info("No customers found.")

    st.subheader("➕ Add New Customer")
    with st.form("add_customer_form", clear_on_submit=True):
        name = st.text_input("Customer Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")

        if st.form_submit_button("Add Customer"):
            try:
                customer_service.add_customer(name, email, phone)
                st.success(f"✅ Customer '{name}' added successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Failed to add customer: {e}")

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ------------------------------
# Initial list of services
# ------------------------------
services = [
    "បាញ់កាងមុខ", "បាញ់កាងក្រោយ", "ជួសថ្ពាល់", "បាញ់ដំបូលលើ", "បាញ់ដំបូលមុខ",
    "បាញ់ត្រគៀក", "បាញ់ទ្វា", "តោនចាប់គ្រឿង", "ជួសជុលតូចៗ", "ជួសជុលធំៗ"
]

st.title("💡 Car Repair & Spray Invoice System")

# ------------------------------
# Auto-generate Invoice ID
# ------------------------------
def generate_invoice_id():
    now = datetime.now()
    return f"INV-{now.strftime('%Y%m%d%H%M%S')}"

# ------------------------------
# Customer info input
# ------------------------------
st.header("ព័ត៌មានអតិថិជន")
customer_name = st.text_input("ឈ្មោះអតិថិជន")
phone = st.text_input("លេខទូរស័ព្ទ")
car_model = st.text_input("ម៉ូដែលឡាន")
date = st.date_input("កាលបរិច្ឆេទ", datetime.today())
invoice_id = generate_invoice_id()
st.text_input("Invoice ID", value=invoice_id, disabled=True)

# ------------------------------
# Services input (multiple services per customer)
# ------------------------------
st.header("សេវាកម្ម")
data = []
num_rows = st.number_input("ចំនួន Services", 1, 15, 3)

for i in range(num_rows):
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        service_choice = st.selectbox(
            f"Service {i+1}", 
            services + ["ផ្សេងៗ (Other)"], 
            key=f"service{i}"
        )
        if service_choice == "ផ្សេងៗ (Other)":
            service = st.text_input(
                f"Enter custom service {i+1} (សេវាកម្មបន្ថែម)", 
                key=f"custom_service{i}"
            )
            if service and service not in services:
                services.append(service)
        else:
            service = service_choice
    with col2:
        qty = st.number_input("Qty", 1, 20, 1, key=f"qty{i}")
    with col3:
        price = st.number_input("Unit Price", 0.0, 1000.0, 50.0, key=f"price{i}")
    amount = qty * price
    data.append([invoice_id, customer_name, phone, car_model, service, qty, price, amount])

# ------------------------------
# Convert to DataFrame
# ------------------------------
df = pd.DataFrame(data, columns=[
    "InvoiceID", "ឈ្មោះអតិថិជន", "លេខទូរស័ព្ទ", "ម៉ូដែលឡាន",
    "Name of Goods", "Quantity", "Unit Price", "Amount"
])

# ------------------------------
# Clean display for Excel
# ------------------------------
def format_for_excel(df):
    rows = []
    for inv_id in df["InvoiceID"].unique():
        inv_df = df[df["InvoiceID"] == inv_id].copy()
        # Copy customer info only for first row
        inv_df.iloc[1:, 1:4] = ""
        # Add total row
        total_amount = inv_df["Amount"].sum()
        total_row = pd.DataFrame({
            "InvoiceID": [inv_id],
            "ឈ្មោះអតិថិជន": ["សរុប / Total"],
            "លេខទូរស័ព្ទ": [""],
            "ម៉ូដែលឡាន": [""],
            "Name of Goods": [""],
            "Quantity": [""],
            "Unit Price": [""],
            "Amount": [total_amount]
        })
        inv_df = pd.concat([inv_df, total_row], ignore_index=True)
        rows.append(inv_df)
    return pd.concat(rows, ignore_index=True)

df_excel = format_for_excel(df)

st.write("**Preview Data (Excel-Friendly)**")
st.dataframe(df_excel)

# ------------------------------
# Save to Excel
# ------------------------------
if st.button("💾 Save to Excel"):
    filename = "invoice_data.xlsx"
    if os.path.exists(filename):
        old = pd.read_excel(filename)
        df_all = pd.concat([old, df_excel], ignore_index=True)
    else:
        df_all = df_excel
    df_all.to_excel(filename, index=False)
    st.success("Saved to Excel!")

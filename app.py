import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# --------------------------
# Database Setup
# --------------------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    note TEXT
)
""")
conn.commit()

# --------------------------
# Functions
# --------------------------
def add_expense(date, category, amount, note):
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date, category, amount, note)
    )
    conn.commit()

def get_expenses():
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    return df

def delete_expense(expense_id):
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()

# --------------------------
# UI
# --------------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💰 Expense Tracker (SQLite Version)")

# --------------------------
# Sidebar Input
# --------------------------
st.sidebar.header("Add Expense")

date = st.sidebar.date_input("Date", datetime.today())
category = st.sidebar.selectbox(
    "Category",
    ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
)
amount = st.sidebar.number_input("Amount", min_value=0.0)
note = st.sidebar.text_input("Note")

if st.sidebar.button("Add Expense"):
    if amount <= 0:
        st.sidebar.error("Amount must be > 0")
    else:
        add_expense(str(date), category, amount, note)
        st.sidebar.success("Added successfully")

# --------------------------
# Budget
# --------------------------
st.sidebar.header("Budget")
budget = st.sidebar.number_input("Monthly Budget", min_value=0.0)

# --------------------------
# Display Data
# --------------------------
df = get_expenses()

st.subheader("All Expenses")
st.dataframe(df, use_container_width=True)

# --------------------------
# Delete Expense
# --------------------------
st.subheader("Delete Expense")

if not df.empty:
    expense_id = st.number_input(
        "Enter ID to delete",
        min_value=int(df["id"].min()),
        max_value=int(df["id"].max()),
        step=1
    )
    if st.button("Delete"):
        delete_expense(expense_id)
        st.success("Deleted")

# --------------------------
# Summary
# --------------------------
if not df.empty:
    st.subheader("Summary")

    df["date"] = pd.to_datetime(df["date"])

    total_spent = df["amount"].sum()
    remaining = budget - total_spent

    col1, col2 = st.columns(2)
    col1.metric("Total Spent", f"₹{total_spent:.2f}")
    col2.metric("Remaining Budget", f"₹{remaining:.2f}")

    if budget > 0 and total_spent > budget:
        st.error("⚠️ Budget Exceeded")
    elif budget > 0:
        st.success("Within Budget")

    # --------------------------
    # Pie Chart
    # --------------------------
    st.subheader("Category-wise Spending")

    cat_data = df.groupby("category")["amount"].sum()

    fig1, ax1 = plt.subplots()
    ax1.pie(cat_data, labels=cat_data.index, autopct="%1.1f%%")
    ax1.axis("equal")
    st.pyplot(fig1)

    # --------------------------
    # Monthly Trend
    # --------------------------
    st.subheader("Monthly Trend")

    df["month"] = df["date"].dt.to_period("M")
    monthly = df.groupby("month")["amount"].sum()

    fig2, ax2 = plt.subplots()
    monthly.plot(kind="bar", ax=ax2)
    st.pyplot(fig2)

else:
    st.info("No data yet.")
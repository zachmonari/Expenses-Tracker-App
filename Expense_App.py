import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.express as px

# -----------------------------
# File setup
# -----------------------------
DATA_FILE = "expenses.json"

def load_expenses():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_expenses(expenses):
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="💰 Expense Tracker", page_icon="💵", layout="centered")

st.title("💰 Personal Expense Tracker")
st.markdown("### Track your daily expenses easily and visualize spending by category.")

# Load existing data
expenses = load_expenses()

# Convert to DataFrame
df = pd.DataFrame(expenses)

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "📋 View All", "📊 Category Summary"])

# -----------------------------
# Tab 1: Add Expense
# -----------------------------
with tab1:
    st.subheader("Add a New Expense")

    with st.form("add_expense_form", clear_on_submit=True):
        category = st.text_input("Category (e.g., Food, Transport, Bills):").capitalize()
        description = st.text_input("Description:")
        amount = st.number_input("Amount:", min_value=0.0, format="%.2f")
        date = st.date_input("Date:", datetime.now())

        submitted = st.form_submit_button("Add Expense")

        if submitted:
            if not category or not description or amount <= 0:
                st.warning("⚠️ Please fill in all fields correctly.")
            else:
                new_expense = {
                    "category": category,
                    "description": description,
                    "amount": amount,
                    "date": date.strftime("%Y-%m-%d")
                }
                expenses.append(new_expense)
                save_expenses(expenses)
                st.success(f"✅ Added {amount:.2f} under {category}")

# -----------------------------
# Tab 2: View All Expenses
# -----------------------------
with tab2:
    st.subheader("📋 All Recorded Expenses")

    if df.empty:
        st.info("No expenses recorded yet.")
    else:
        st.dataframe(df, use_container_width=True)
        total_spent = df["amount"].sum()
        st.markdown(f"### 💵 Total Spending: **${total_spent:.2f}**")

# -----------------------------
# Tab 3: Category Summary
# -----------------------------
with tab3:
    st.subheader("📊 Spending by Category")

    if df.empty:
        st.info("No data available for summary.")
    else:
        category_totals = df.groupby("category")["amount"].sum().reset_index()

        # Pie chart visualization
        fig = px.pie(category_totals, names="category", values="amount", title="Spending Breakdown")
        st.plotly_chart(fig, width='stretch')

        # Bar chart
        fig2 = px.bar(category_totals, x="category", y="amount", text="amount",
                      title="Spending per Category", color="category")
        st.plotly_chart(fig2, width='stretch')

st.markdown("---")
st.caption("© 2025 Expense Tracker™ | Developed in Python with ❤️ and Streamlit")
st.caption("@ Zach Techs ")

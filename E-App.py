import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import io
import os
from PIL import Image

#Logo
logo=Image.open("ZachTechs.jpg")
st.image(logo, width=150)

# Page configuration
st.set_page_config(
    page_title="Personal Expenses Tracker",
    page_icon="💰",
    layout="wide"
)

# Initialize session state for data persistence
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount', 'Type'])


def add_expense(date, category, description, amount, expense_type):
    """Add a new expense/income to the dataframe"""
    new_entry = {
        'Date': date,
        'Category': category,
        'Description': description,
        'Amount': amount,
        'Type': expense_type
    }

    # Convert to DataFrame and concatenate
    new_df = pd.DataFrame([new_entry])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_df], ignore_index=True)

def delete_expense(index):
    """Delete an expense by index"""
    st.session_state.expenses = st.session_state.expenses.drop(index).reset_index(drop=True)


def get_summary():
    """Calculate summary statistics"""
    if st.session_state.expenses.empty:
        return 0, 0, 0

    expenses = st.session_state.expenses[st.session_state.expenses['Type'] == 'Expense']
    income = st.session_state.expenses[st.session_state.expenses['Type'] == 'Income']

    total_expenses = expenses['Amount'].sum() if not expenses.empty else 0
    total_income = income['Amount'].sum() if not income.empty else 0
    balance = total_income - total_expenses

    return total_income, total_expenses, balance


def plot_expenses_by_category():
    """Create a pie chart of expenses by category"""
    if st.session_state.expenses.empty:
        return None

    expenses_df = st.session_state.expenses[st.session_state.expenses['Type'] == 'Expense']

    if expenses_df.empty:
        return None

    category_totals = expenses_df.groupby('Category')['Amount'].sum()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(category_totals.values, labels=category_totals.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Expenses by Category')
    return fig


def plot_monthly_trend():
    """Create a line chart of monthly expenses and income"""
    if st.session_state.expenses.empty:
        return None

    # Convert date and extract year-month
    df = st.session_state.expenses.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year-Month'] = df['Date'].dt.to_period('M').astype(str)

    monthly_data = df.groupby(['Year-Month', 'Type'])['Amount'].sum().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 6))

    if 'Expense' in monthly_data.columns:
        ax.plot(monthly_data.index, monthly_data['Expense'], marker='o', label='Expenses', color='red')
    if 'Income' in monthly_data.columns:
        ax.plot(monthly_data.index, monthly_data['Income'], marker='o', label='Income', color='green')

    ax.set_title('Monthly Income vs Expenses')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    return fig

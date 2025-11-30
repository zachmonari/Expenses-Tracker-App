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
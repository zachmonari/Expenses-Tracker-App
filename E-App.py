import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
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
    ax.set_ylabel('Amount (KSH)')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    return fig


def main():
    st.title("💰 Personal Expense Tracker")
    st.markdown("Track your income and expenses effortlessly!")

    # Sidebar for adding new entries
    with st.sidebar:
        st.header("Add New Transaction")

        with st.form("add_transaction"):
            date = st.date_input("Date", datetime.date.today())
            expense_type = st.radio("Type", ["Expense", "Income"])

            categories = {
                "Expense": ["Food & Dining", "Transportation", "Entertainment", "Shopping",
                            "Bills & Utilities", "Healthcare", "Education", "Other"],
                "Income": ["Salary", "Freelance", "Investment", "Gift", "Other"]
            }

            category = st.selectbox("Category", categories[expense_type])
            description = st.text_input("Description")
            amount = st.number_input("Amount (KSH)", min_value=0.0, step=0.01)

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                if amount > 0 and description:
                    add_expense(date, category, description, amount, expense_type)
                    st.success(f"✅ {expense_type} added successfully!")
                else:
                    st.error("❌ Please enter a valid amount and description")

    # Main content area
    col1, col2, col3 = st.columns(3)

    total_income, total_expenses, balance = get_summary()

    with col1:
        st.metric("Total Income", f"KSH. {total_income:,.2f}")
    with col2:
        st.metric("Total Expenses", f"KSH. {total_expenses:,.2f}")
    with col3:
        balance_color = "normal" if balance >= 0 else "inverse"
        st.metric("Balance", f"KSH. {balance:,.2f}", delta=None, delta_color=balance_color)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Expense Distribution")
        pie_chart = plot_expenses_by_category()
        if pie_chart:
            st.pyplot(pie_chart)
        else:
            st.info("No expense data to display")

    with col2:
        st.subheader("Monthly Trends")
        trend_chart = plot_monthly_trend()
        if trend_chart:
            st.pyplot(trend_chart)
        else:
            st.info("No data to display trends")

    # Data table and management
    st.subheader("Transaction History")

    if not st.session_state.expenses.empty:
        # Convert date to string for display
        display_df = st.session_state.expenses.copy()
        display_df['Date'] = display_df['Date'].astype(str)

        # Add delete buttons
        display_df['Delete'] = False
        edited_df = st.data_editor(
            display_df,
            column_config={
                "Delete": st.column_config.CheckboxColumn(
                    "Delete?",
                    help="Check to delete transaction",
                    default=False
                )
            },
            hide_index=True,
            width="stretch"
        )

        # Process deletions
        if edited_df['Delete'].any():
            indices_to_delete = edited_df[edited_df['Delete'] == True].index
            for idx in indices_to_delete:
                delete_expense(idx)
            st.rerun()

        # Export options
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 Export to CSV"):
                csv = st.session_state.expenses.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"expenses_{datetime.date.today()}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("🗑️ Clear All Data"):
                if st.checkbox("I'm sure I want to delete all data"):
                    st.session_state.expenses = pd.DataFrame(
                        columns=['Date', 'Category', 'Description', 'Amount', 'Type'])
                    st.rerun()

    else:
        st.info("No transactions yet. Add some using the sidebar!")

    # Sample data for testing
    with st.expander("💡 Need sample data?"):
        if st.button("Load Sample Data"):
            sample_data = [
                {'Date': datetime.date(2024, 1, 15), 'Category': 'Salary', 'Description': 'Monthly Salary',
                 'Amount': 3000, 'Type': 'Income'},
                {'Date': datetime.date(2024, 1, 16), 'Category': 'Food & Dining', 'Description': 'Groceries',
                 'Amount': 150, 'Type': 'Expense'},
                {'Date': datetime.date(2024, 1, 17), 'Category': 'Transportation', 'Description': 'Gas', 'Amount': 60,
                 'Type': 'Expense'},
                {'Date': datetime.date(2024, 1, 18), 'Category': 'Entertainment', 'Description': 'Movie', 'Amount': 35,
                 'Type': 'Expense'},
                {'Date': datetime.date(2024, 1, 20), 'Category': 'Freelance', 'Description': 'Web Design',
                 'Amount': 500, 'Type': 'Income'},
            ]
            for data in sample_data:
                add_expense(data['Date'], data['Category'], data['Description'], data['Amount'], data['Type'])
            st.success("Sample data loaded! Scroll up to see the dashboard.")
            st.rerun()


if __name__ == "__main__":
    main()
st.markdown("---")
st.caption("© 2025 Expenses Tracker™ ")
st.caption("@ Zach Techs ")
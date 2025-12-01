import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from contextlib import contextmanager
import os

# Page configuration
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Database configuration
DB_FILE = "expenses.db"
INITIAL_CATEGORIES = {
    "Expense": ["Food & Dining", "Transportation", "Entertainment", "Shopping",
                "Bills & Utilities", "Healthcare", "Education", "Other"],
    "Income": ["Salary", "Freelance", "Investment", "Gift", "Other"]
}


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create categories table for user customization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                color TEXT,
                icon TEXT
            )
        ''')

        # Create budgets table for future extension
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                monthly_limit REAL NOT NULL,
                year_month TEXT NOT NULL,
                UNIQUE(category, year_month)
            )
        ''')

        # Create user settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL
            )
        ''')

        # Insert default categories if not exists
        for trans_type, categories in INITIAL_CATEGORIES.items():
            for category in categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, type) 
                    VALUES (?, ?)
                ''', (category, trans_type))

        # Set default currency
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('currency', 'KSH')
        ''')

        conn.commit()


def add_transaction(date, category, description, amount, trans_type):
    """Add a new transaction to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (date, category, description, amount, type)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, category, description, amount, trans_type))
        conn.commit()
        return cursor.lastrowid


def get_all_transactions():
    """Get all transactions from database"""
    with get_db_connection() as conn:
        query = '''
            SELECT id, date, category, description, amount, type, created_at
            FROM transactions
            ORDER BY date DESC, created_at DESC
        '''
        df = pd.read_sql_query(query, conn)

        # Convert date columns to datetime
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['created_at'] = pd.to_datetime(df['created_at'])

        return df


def delete_transaction(transaction_id):
    """Delete a transaction by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        return cursor.rowcount > 0


def update_transaction(transaction_id, date, category, description, amount, trans_type):
    """Update an existing transaction"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions 
            SET date = ?, category = ?, description = ?, amount = ?, type = ?
            WHERE id = ?
        ''', (date, category, description, amount, trans_type, transaction_id))
        conn.commit()
        return cursor.rowcount > 0


def get_categories(trans_type=None):
    """Get categories from database"""
    with get_db_connection() as conn:
        if trans_type:
            query = "SELECT name FROM categories WHERE type = ? ORDER BY name"
            categories = pd.read_sql_query(query, conn, params=(trans_type,))
        else:
            query = "SELECT name, type FROM categories ORDER BY type, name"
            categories = pd.read_sql_query(query, conn)
        return categories


def add_category(name, trans_type, color=None, icon=None):
    """Add a new category"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO categories (name, type, color, icon)
                VALUES (?, ?, ?, ?)
            ''', (name, trans_type, color, icon))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Category already exists


def delete_category(name):
    """Delete a category"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categories WHERE name = ?', (name,))
        conn.commit()
        return cursor.rowcount > 0


def get_summary():
    """Calculate summary statistics from database"""
    with get_db_connection() as conn:
        # Get total income
        income_query = "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'Income'"
        income_result = conn.execute(income_query).fetchone()
        total_income = income_result['total']

        # Get total expenses
        expense_query = "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'Expense'"
        expense_result = conn.execute(expense_query).fetchone()
        total_expenses = expense_result['total']

        balance = total_income - total_expenses

        return float(total_income), float(total_expenses), float(balance)


def get_category_summary():
    """Get summary by category"""
    with get_db_connection() as conn:
        query = '''
            SELECT 
                category,
                type,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM transactions
            GROUP BY category, type
            ORDER BY type, total_amount DESC
        '''
        return pd.read_sql_query(query, conn)


def get_monthly_summary():
    """Get monthly summary"""
    with get_db_connection() as conn:
        query = '''
            SELECT 
                utctime('%Y-%m', date) as month,
                type,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM transactions
            GROUP BY month, type
            ORDER BY month DESC
        '''
        return pd.read_sql_query(query, conn)


def export_to_csv():
    """Export all transactions to CSV"""
    df = get_all_transactions()
    if df.empty:
        return None

    # Format for export
    export_df = df.copy()
    export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
    export_df['created_at'] = export_df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return export_df.to_csv(index=False)


def plot_expenses_by_category():
    """Create a pie chart of expenses by category"""
    category_summary = get_category_summary()

    if category_summary.empty:
        return None

    expenses_df = category_summary[category_summary['type'] == 'Expense']

    if expenses_df.empty or expenses_df['total_amount'].sum() == 0:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = plt.cm.Set3(np.linspace(0, 1, len(expenses_df)))

    wedges, texts, autotexts = ax.pie(
        expenses_df['total_amount'],
        labels=expenses_df['category'],
        autopct=lambda p: f'{p:.1f}%\n(Ksh. {(p / 100) * expenses_df["total_amount"].sum():.0f})',
        startangle=90,
        colors=colors,
        pctdistance=0.85
    )

    # Draw a circle in the center to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)

    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    ax.set_title('Expenses by Category', fontweight='bold', pad=20)
    return fig


def plot_monthly_trend():
    """Create a line chart of monthly expenses and income"""
    monthly_summary = get_monthly_summary()

    if monthly_summary.empty:
        return None

    # Pivot the data
    pivot_df = monthly_summary.pivot(index='month', columns='type', values='total_amount').fillna(0)

    fig, ax = plt.subplots(figsize=(10, 6))

    if 'Expense' in pivot_df.columns and pivot_df['Expense'].sum() > 0:
        ax.plot(pivot_df.index, pivot_df['Expense'], marker='o', label='Expenses',
                color='#FF6B6B', linewidth=2, markersize=8)

    if 'Income' in pivot_df.columns and pivot_df['Income'].sum() > 0:
        ax.plot(pivot_df.index, pivot_df['Income'], marker='s', label='Income',
                color='#51CF66', linewidth=2, markersize=8)

    ax.set_title('Monthly Income vs Expenses', fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount (Ksh)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

    # Add value labels on points
    for col in ['Expense', 'Income']:
        if col in pivot_df.columns:
            for i, (month, value) in enumerate(zip(pivot_df.index, pivot_df[col])):
                if value > 0:
                    ax.annotate(f'Ksh{value:,.0f}',
                                xy=(i, value),
                                xytext=(0, 10 if col == 'Expense' else -15),
                                textcoords="offset points",
                                ha='center',
                                fontsize=8,
                                color='#FF6B6B' if col == 'Expense' else '#51CF66',
                                fontweight='bold')

    plt.tight_layout()
    return fig


def add_sample_data():
    """Add sample data for demonstration"""
    sample_data = [
        (datetime.date(2024, 1, 15), 'Salary', 'Monthly Salary', 3000, 'Income'),
        (datetime.date(2024, 1, 16), 'Food & Dining', 'Groceries', 150, 'Expense'),
        (datetime.date(2024, 1, 17), 'Transportation', 'Gas', 60, 'Expense'),
        (datetime.date(2024, 1, 18), 'Entertainment', 'Movie', 35, 'Expense'),
        (datetime.date(2024, 1, 20), 'Freelance', 'Web Design', 500, 'Income'),
        (datetime.date(2024, 2, 1), 'Bills & Utilities', 'Electricity', 80, 'Expense'),
        (datetime.date(2024, 2, 5), 'Salary', 'Monthly Salary', 3000, 'Income'),
        (datetime.date(2024, 2, 10), 'Food & Dining', 'Restaurant', 75, 'Expense'),
        (datetime.date(2024, 2, 15), 'Shopping', 'Clothes', 120, 'Expense'),
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO transactions (date, category, description, amount, type)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()


def main():
    # Initialize database
    init_database()

    st.title("💰 Personal Expense Tracker ")
    st.markdown("Track your Transactions effortlessly!")

    # Sidebar for adding new entries
    with st.sidebar:
        st.header("➕ Add New Transaction")

        with st.form("add_transaction", clear_on_submit=True):
            date = st.date_input("Date", datetime.date.today())
            trans_type = st.radio("Type", ["Expense", "Income"], horizontal=True)

            # Get categories from database
            categories_df = get_categories(trans_type)
            categories = categories_df['name'].tolist() if not categories_df.empty else []

            category = st.selectbox("Category", categories)
            description = st.text_input("Description")
            amount = st.number_input("Amount (Ksh)", min_value=0.0, step=0.01, format="%.2f")

            submitted = st.form_submit_button("💾 Save Transaction", width="stretch")

            if submitted:
                if amount > 0 and description.strip():
                    transaction_id = add_transaction(date, category, description.strip(), amount, trans_type)
                    st.success(f"✅ Transaction #{transaction_id} saved successfully!")
                else:
                    st.error("❌ Please enter a valid amount and description")

        st.divider()

        # Category Management
        st.header("🗂️ Category Management")
        with st.expander("Manage Categories"):
            tab1, tab2 = st.tabs(["Add Category", "Delete Category"])

            with tab1:
                with st.form("add_category_form"):
                    new_category_name = st.text_input("Category Name")
                    new_category_type = st.selectbox("Type", ["Expense", "Income"])
                    col1, col2 = st.columns(2)
                    with col1:
                        new_category_color = st.color_picker("Color", "#4CAF50")
                    with col2:
                        new_category_icon = st.selectbox("Icon", ["💰", "🛒", "🍔", "🚗", "🎬", "🏠", "💼", "🎁"])

                    if st.form_submit_button("Add Category"):
                        if new_category_name.strip():
                            if add_category(new_category_name.strip(), new_category_type,
                                            new_category_color, new_category_icon):
                                st.success(f"✅ Category '{new_category_name}' added!")
                                st.rerun()
                            else:
                                st.error("❌ Category already exists!")

            with tab2:
                all_categories = get_categories()
                if not all_categories.empty:
                    category_to_delete = st.selectbox(
                        "Select category to delete",
                        all_categories['name'].tolist()
                    )
                    if st.button("🗑️ Delete Category", type="secondary"):
                        if delete_category(category_to_delete):
                            st.warning(f"Category '{category_to_delete}' deleted!")
                            st.rerun()
                else:
                    st.info("No categories to delete")

    # Main content area
    col1, col2, col3 = st.columns(3)

    total_income, total_expenses, balance = get_summary()

    with col1:
        st.metric("💰 Total Income", f"Ksh. {total_income:,.2f}", delta=None)
    with col2:
        st.metric("💸 Total Expenses", f"Ksh. {total_expenses:,.2f}", delta=None)
    with col3:
        balance_color = "normal" if balance >= 0 else "off"
        balance_icon = "📈" if balance >= 0 else "📉"
        st.metric(f"{balance_icon} Balance", f"Ksh. {balance:,.2f}", delta=None, delta_color=balance_color)

    # Charts
    if not get_all_transactions().empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Expense Distribution")
            pie_chart = plot_expenses_by_category()
            if pie_chart:
                st.pyplot(pie_chart)
            else:
                st.info("No expense data to display")

        with col2:
            st.subheader("📈 Monthly Trends")
            trend_chart = plot_monthly_trend()
            if trend_chart:
                st.pyplot(trend_chart)
            else:
                st.info("No data to display trends")

    # Transaction History with Edit/Delete
    st.subheader("📋 Transaction History")

    transactions_df = get_all_transactions()

    if not transactions_df.empty:
        # Format for display
        display_df = transactions_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"Ksh. {x:,.2f}")
        display_df = display_df[['id', 'date', 'type', 'category', 'description', 'amount']]

        # Display with edit/delete options
        for _, row in display_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 2, 2, 3, 2, 2])
                with col1:
                    st.text(f"#{row['id']}")
                with col2:
                    st.text(row['date'])
                with col3:
                    type_color = "🟢" if row['type'] == 'Income' else "🔴"
                    st.text(f"{type_color} {row['type']}")
                with col4:
                    st.text(row['category'])
                with col5:
                    st.text(row['description'][:30] + ("..." if len(row['description']) > 30 else ""))
                with col6:
                    amount_color = "green" if row['type'] == 'Income' else "red"
                    st.markdown(f"<span style='color:{amount_color}; font-weight:bold;'>{row['amount']}</span>",
                                unsafe_allow_html=True)
                with col7:
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("✏️", key=f"edit_{row['id']}", help="Edit"):
                            st.session_state[f"edit_{row['id']}"] = True
                    with col_del:
                        if st.button("🗑️", key=f"del_{row['id']}", help="Delete"):
                            if delete_transaction(row['id']):
                                st.success(f"Transaction #{row['id']} deleted!")
                                st.rerun()

        # Export options
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = export_to_csv()
            if csv_data:
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv_data,
                    file_name=f"expenses_{datetime.date.today()}.csv",
                    mime="text/csv",
                    width="stretch"

                )

        with col2:
            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
                st.warning("⚠️ This will delete ALL transactions!")
                confirm = st.checkbox("I understand this action cannot be undone")
                if confirm and st.button("Confirm Delete All", type="primary"):
                    with get_db_connection() as conn:
                        conn.execute("DELETE FROM transactions")
                        conn.commit()
                    st.error("All data deleted!")
                    st.rerun()

        with col3:
            db_size = os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0
            st.info(f"Database: {db_size / 1024:.1f} KB")

    else:
        st.info("📭 No transactions yet. Add some using the sidebar!")

    # Footer with database info and sample data
    with st.expander("⚙️ Database Tools & Info"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sample Data")
            st.write("Need some data to test with?")
            if st.button("Load Sample Data"):
                add_sample_data()
                st.success("Sample data loaded! Refresh to see it.")
                st.rerun()

        with col2:
            st.subheader("Database Info")
            if os.path.exists(DB_FILE):
                db_stats = {
                    "File Size": f"{os.path.getsize(DB_FILE) / 1024:.1f} KB",
                    "Transactions": len(transactions_df),
                    "Categories": len(get_categories())
                }
                for key, value in db_stats.items():
                    st.text(f"{key}: {value}")
            else:
                st.warning("Database file not found!")


if __name__ == "__main__":
    main()
st.markdown("---")
st.caption("© 2025 Expenses Tracker™ ")
st.caption("@ Zach Techs ")
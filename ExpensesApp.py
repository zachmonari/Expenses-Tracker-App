import json
from datetime import datetime

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
# Core functions
# -----------------------------
def add_expense(expenses):
    print("\n📝 Add a New Expense")
    category = input("Enter category (e.g., food, transport, bills): ").strip().capitalize()
    description = input("Enter description: ").strip()

    while True:
        try:
            amount = float(input("Enter amount: "))
            break
        except ValueError:
            print("⚠️ Please enter a valid number.")

    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    expense = {
        "category": category,
        "description": description,
        "amount": amount,
        "date": date
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"✅ Expense added: {amount} in {category}")


def view_expenses(expenses):
    print("\n📋 All Expenses:")
    if not expenses:
        print("No expenses recorded yet.")
        return

    for i, exp in enumerate(expenses, 1):
        print(f"{i}. {exp['date']} - {exp['category']}: {exp['description']} (${exp['amount']:.2f})")


def total_per_category(expenses):
    print("\n📊 Total Spending per Category:")
    if not expenses:
        print("No expenses recorded yet.")
        return

    totals = {}
    for exp in expenses:
        category = exp["category"]
        totals[category] = totals.get(category, 0) + exp["amount"]

    for cat, total in totals.items():
        print(f"{cat}: ${total:.2f}")


# -----------------------------
# Edit & Delete Functions
# -----------------------------
def edit_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return

    try:
        idx = int(input("\nEnter the number of the expense to edit: ")) - 1
        if idx < 0 or idx >= len(expenses):
            print("⚠️ Invalid selection.")
            return
    except ValueError:
        print("⚠️ Please enter a valid number.")
        return

    exp = expenses[idx]
    print(f"\nEditing: {exp['category']} - {exp['description']} (${exp['amount']}) on {exp['date']}")

    new_category = input(f"New category [{exp['category']}]: ").strip().capitalize() or exp["category"]
    new_description = input(f"New description [{exp['description']}]: ").strip() or exp["description"]

    try:
        new_amount = input(f"New amount [{exp['amount']}]: ").strip()
        new_amount = float(new_amount) if new_amount else exp["amount"]
    except ValueError:
        print("⚠️ Invalid amount. Keeping old value.")
        new_amount = exp["amount"]

    new_date = input(f"New date [{exp['date']}]: ").strip() or exp["date"]

    expenses[idx] = {
        "category": new_category,
        "description": new_description,
        "amount": new_amount,
        "date": new_date
    }
    save_expenses(expenses)
    print("✅ Expense updated successfully!")


def delete_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return

    try:
        idx = int(input("\nEnter the number of the expense to delete: ")) - 1
        if idx < 0 or idx >= len(expenses):
            print("⚠️ Invalid selection.")
            return
    except ValueError:
        print("⚠️ Please enter a valid number.")
        return

    deleted = expenses.pop(idx)
    save_expenses(expenses)
    print(f"🗑️ Deleted: {deleted['description']} ({deleted['category']}) - ${deleted['amount']:.2f}")


# -----------------------------
# Main Program Loop
# -----------------------------
def main():
    expenses = load_expenses()

    while True:
        print("\n=== 💰 Expense Tracker ===")
        print("1️⃣  Add Expense")
        print("2️⃣  View All Expenses")
        print("3️⃣  View Total per Category")
        print("4️⃣  Edit an Expense")
        print("5️⃣  Delete an Expense")
        print("0️⃣  Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            total_per_category(expenses)
        elif choice == "4":
            edit_expense(expenses)
        elif choice == "5":
            delete_expense(expenses)
        elif choice == "0":
            print("👋 Goodbye! Your expenses have been saved.")
            break
        else:
            print("⚠️ Invalid choice. Try again.")


if __name__ == "__main__":
    main()

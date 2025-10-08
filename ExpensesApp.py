import json
from datetime import datetime

# -----------------------------
# File setup
# -----------------------------
DATA_FILE = "expenses.json"


# Load existing expenses or start with an empty list
def load_expenses():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Save expenses to file
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
# Main Program Loop
# -----------------------------
def main():
    expenses = load_expenses()

    while True:
        print("\n=== 💰 Expense Tracker ===")
        print("1️⃣  Add Expense")
        print("2️⃣  View All Expenses")
        print("3️⃣  View Total per Category")
        print("0️⃣  Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            total_per_category(expenses)
        elif choice == "0":
            print("👋 Goodbye! Your expenses have been saved.")
            break
        else:
            print("⚠️ Invalid choice. Try again.")


if __name__ == "__main__":
    main()

from models.account import Account, AccountGroup
from models.user import User
from models.transaction import Transaction

users = {}

def preload_users():
    u1 = User("Alice", "alice@example.com", "password123")

    # 🧾 Add dummy transactions
    u1.transactions.append(Transaction(1000, "Salary", "income", "Monthly pay", date_str("2024-04-01")))
    u1.transactions.append(Transaction(200, "Groceries", "expense", "Walmart", date_str("2024-04-01")))
    u1.transactions.append(Transaction(50, "Transport", "expense", "Gas", date_str("2024-04-02")))
    u1.transactions.append(Transaction(300, "Freelance", "income", "Side gig", date_str("2024-04-05")))
    u1.transactions.append(Transaction(120, "Eating Out", "expense", "Dinner", date_str("2024-04-05")))
    u1.transactions.append(Transaction(80, "Subscriptions", "expense", "Netflix", date_str("2024-03-28")))

    users[u1.id] = u1

    group = u1.add_group("Chase Bank")
    group.add_account(Account("Checking", "checking", 1000))
    group.add_account(Account("Savings", "savings", 3000))

    group2 = u1.add_group("Wells Fargo")
    group2.add_account(Account("Credit Card", "credit", -500))


def date_str(date_string):
    from datetime import datetime
    return datetime.strptime(date_string, "%Y-%m-%d")

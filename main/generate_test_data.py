import random
from datetime import datetime, timedelta
from models.models import db, User, Transaction, Account, AccountGroup
from app import app

# -------------------
# CONFIGURATION
# -------------------
USER_EMAIL = "alice@example.com"
NUM_TRANSACTIONS = 300
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime.today()

BANK_NAMES = ["Chase", "Bank of America", "Wells Fargo"]
ACCOUNT_TYPES = ["Checking", "Savings"]
INCOME_CATEGORIES = ["Salary", "Allowance", "Bonus", "Interest earned", "Other"]
EXPENSE_CATEGORIES = ["Food", "Groceries", "Rent", "Utilities", "Gas", "Travel", "Gift", "Shopping"]
NOTES = ["Lunch", "Paycheck", "Gas refill", "Netflix", "Rent", "Bonus", "Dinner", "Holiday"]

def random_date():
    return START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))

# -------------------
# MAIN LOGIC
# -------------------
with app.app_context():
    user = User.query.filter_by(email=USER_EMAIL).first()
    if not user:
        print("User not found.")
        exit()

    # Create Account Groups (Banks)
    if not user.account_groups:
        for bank in BANK_NAMES:
            group = AccountGroup(name=bank, user_id=user.id)
            db.session.add(group)
        db.session.commit()

    # Create Accounts under each group
    for group in user.account_groups:
        if not group.accounts:
            for acct_type in ACCOUNT_TYPES:
                acct = Account(name=f"{acct_type} Account", balance=1000.0, group_id=group.id)
                db.session.add(acct)
    db.session.commit()

    # Flatten all user accounts for access
    all_accounts = [acct for g in user.account_groups for acct in g.accounts]

    # Generate Transactions
    for _ in range(NUM_TRANSACTIONS):
        t_type = random.choice(["income", "expense", "transfer"])
        date = random_date()
        amount = round(random.uniform(10, 1000), 2)
        note = random.choice(NOTES)

        if t_type == "transfer":
            if len(all_accounts) >= 2:
                from_acct, to_acct = random.sample(all_accounts, 2)
                t = Transaction(
                    user_id=user.id,
                    account_id=from_acct.id,
                    type="transfer",
                    category="Transfer",
                    amount=amount,
                    note=f"Transfer to {to_acct.name}",
                    date=date,
                    from_account_id=from_acct.id,
                    to_account_id=to_acct.id
                )
                db.session.add(t)
                continue  # Skip rest of the loop for transfer
            else:
                continue  # Not enough accounts for transfer

        # For income or expense
        account = random.choice(all_accounts)
        category = random.choice(INCOME_CATEGORIES if t_type == "income" else EXPENSE_CATEGORIES)
        t = Transaction(
            user_id=user.id,
            account_id=account.id,
            type=t_type,
            category=category,
            amount=amount,
            note=note,
            date=date
        )
        db.session.add(t)

    db.session.commit()
    print(f"✅ {NUM_TRANSACTIONS} transactions created for {user.name}.")

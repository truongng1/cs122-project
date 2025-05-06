# WalletO - Personal Finance Tracker

## Group Members
- Eric Nguyen
- Jonathan Huang

## Project Description
WalletO is a web-based personal finance tracker that allows users to manage transactions across multiple accounts. Users can record income, expenses, and transfers, view monthly statistics, and export their data. The app supports grouping of accounts and provides a clean interface with a galaxy-themed background.

## Dependencies
- Flask==2.3.2
- Flask_SQLAlchemy==3.0.5
- pandas==2.2.2
- openpyxl==3.1.2
- Werkzeug==2.3.7
- Jinja2==3.1.3

See `requirements.txt` for installation.

## Setup and Execution Instructions

1. **Clone the project**:
   ```bash
   git clone https://github.com/yourusername/walleto.git
   cd walleto
   ```

2. **Set up a virtual environment (optional but recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Visit the application**:
   Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## File Structure Overview

```
main/
├── app.py                  # Main application script
├── generate_test_data.py
├── models/
│   └── models.py           # SQLAlchemy models for User, Account, Group, Transaction
├── routes/
│   ├── dashboard_routes.py # Blueprint for dashboard-related routes
│   ├── transaction_routes.py # Blueprint for transaction logic
│   ├── dashboard_routes.py
│   └── auth_routes.py
├── templates/              # HTML templates (Jinja2)
├── static/                 # Static files (background videos
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Known Bugs or Limitations
- SQLite may raise "database is locked" errors under concurrent write conditions.
- Background video can increase page load time.
- No user email verification implemented.
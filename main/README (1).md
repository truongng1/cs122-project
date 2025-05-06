# WalletO - Personal Finance Tracker

## Group Members
- Eric Nguyen
- Jonathan Huang

## Project Description
WalletO is a web-based personal finance tracker that enables users to manage transactions across multiple accounts. Users can record income, expenses, and transfers, view monthly statistics, and export their data. The application supports grouping of accounts and offers a clean interface with a galaxy-themed background.

## Dependencies
- Flask==2.3.2
- Flask_SQLAlchemy==3.0.5
- pandas==2.2.2
- openpyxl==3.1.2
- Werkzeug==2.3.7
- Jinja2==3.1.3

Refer to `requirements.txt` for installation.

## Setup and Execution Instructions

### 1. Clone the Project
```bash
git clone https://github.com/truongng1/cs122-project.git
cd cs122-project/main/
```

### 2. Set Up a Virtual Environment (Recommended)

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (Command Prompt)
```cmd
py -m venv venv
venv\Scripts\activate
```

#### Windows (PowerShell)
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Application
Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 6. Default Login Credentials
Use the following credentials to log in with the preloaded user:
- **Email**: alice@example.com
- **Password**: password123

## File Structure Overview
```
main/
├── app.py                  # Main application script
├── generate_test_data.py   # Script to generate test data
├── models/
│   └── models.py           # SQLAlchemy models for User, Account, Group, Transaction
├── routes/
│   ├── auth_routes.py      # Blueprint for authentication routes
│   ├── dashboard_routes.py # Blueprint for dashboard-related routes
│   └── transaction_routes.py # Blueprint for transaction logic
├── templates/              # HTML templates (Jinja2)
├── static/                 # Static files (e.g., background videos)
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Known Bugs or Limitations
- SQLite may raise "database is locked" errors under concurrent write conditions.
- Background video can increase page load time.
- No user email verification implemented.

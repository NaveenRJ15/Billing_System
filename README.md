# Billing System

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Start server: `uvicorn app.main:app --reload`
3. Run sample data: `python sample_data.py`
4. Visit http://127.0.0.1:8000

## Features
- Product billing with tax calculation
- Denomination-based balance calculation
- Invoice email (async)
- Purchase history
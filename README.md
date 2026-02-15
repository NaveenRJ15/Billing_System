# Billing System

A FastAPI-based billing system that handles product purchases, tax calculation, and change management using denominations.

## Features

- **Product Management**: Add products with pricing and tax rates
- **Tax Calculation**: Automatic per-product tax calculation that scales with quantity
- **Invoice Generation**: Create detailed invoices with itemized purchases
- **Denomination-Based Change**: Calculate and dispense change using available denominations
- **Email Notifications**: Send invoice receipts via email (async)
- **Purchase History**: Track all transactions
- **Inventory Management**: Real-time stock updates

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Run sample data (first time only):**
   ```bash
   python sample_data.py
   ```

4. **Access the application:**
   Open your browser and visit: `http://127.0.0.1:8000`

## Project Structure

```
Billing_System/
├── app/
│   ├── main.py           # FastAPI application & routes
│   ├── models.py         # Database models
│   ├── database.py       # Database configuration
│   └── services.py       # Business logic (optional)
├── templates/
│   ├── index.html        # Purchase form
│   └── bill.html         # Invoice receipt
├── sample_data.py        # Initialize sample data
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Usage

### Making a Purchase

1. Select products and quantities from the form
2. Enter customer email
3. Enter paid amount
4. System calculates:
   - Product subtotal
   - Per-product tax (scales with quantity)
   - Total amount
   - Change using available denominations
5. Invoice is generated and sent to customer email

### Tax Calculation Example

**Pen @ ₹10 with 5% tax:**
- 1 unit: ₹10 + ₹0.50 (tax) = ₹10.50
- 5 units: ₹50 + ₹2.50 (tax) = ₹52.50
- 10 units: ₹100 + ₹5.00 (tax) = ₹105.00

### Denominations

Available denominations (from `sample_data.py`):
- ₹2000 (10 notes)
- ₹500 (20 notes)
- ₹100 (50 notes)
- ₹50 (75 notes)
- ₹20 (100 notes)
- ₹10 (150 notes)
- ₹5 (200 notes)
- ₹1 (500 notes)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page with billing form |
| POST | `/purchase` | Process purchase and generate invoice |

## Database Models

### Product
- `product_id`: Unique identifier
- `name`: Product name
- `price`: Unit price
- `stock`: Available quantity
- `tax_percent`: Tax percentage

### Denomination
- `value`: Denomination value (₹2000, ₹500, etc.)
- `available_count`: Number of notes available

### Invoice
- `id`: Invoice number
- `email`: Customer email
- `total_amount`: Total with tax
- `paid_amount`: Amount received
- `balance`: Change amount
- `items`: List of purchased items
- `balance_denoms`: Change breakdown

## Troubleshooting

**Issue**: "Insufficient denominations available to give exact change"
- **Solution**: Run `python sample_data.py` again to reset denominations or update counts in database

**Issue**: "Insufficient amount paid"
- **Solution**: Ensure paid amount is greater than or equal to total amount

**Issue**: "Insufficient stock"
- **Solution**: Reduce quantity or restock products in database

## Configuration

To modify sample data, edit `sample_data.py`:
- Change product prices, tax rates, or stock
- Update denomination values or counts
- Add new products or denominations

Then run: `python sample_data.py`
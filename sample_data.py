from app.database import SessionLocal
from app.models import Product, Denomination

db = SessionLocal()

products = [
    {"product_id": "P001", "name": "Pen", "price": 10, "stock": 100, "tax_percent": 5},
    {"product_id": "P002", "name": "Notebook", "price": 50, "stock": 50, "tax_percent": 12},
    {"product_id": "P003", "name": "Pencil", "price": 5, "stock": 200, "tax_percent": 0},
    {"product_id": "P004", "name": "Eraser", "price": 2, "stock": 150, "tax_percent": 5},
]

denoms = [
    {"value": 2000, "available_count": 5},
    {"value": 500, "available_count": 10},
    {"value": 100, "available_count": 20},
    {"value": 50, "available_count": 30},
    {"value": 20, "available_count": 50},
    {"value": 10, "available_count": 100},
    {"value": 5, "available_count": 100},
    {"value": 1, "available_count": 100},
]

for p in products:
    if not db.query(Product).filter_by(product_id=p["product_id"]).first():
        db.add(Product(**p))

for d in denoms:
    denom = db.query(Denomination).filter_by(value=d["value"]).first()
    if denom:
        denom.available_count = d["available_count"]
    else:
        db.add(Denomination(**d))

db.commit()
db.close()
print("Sample data seeded successfully!")
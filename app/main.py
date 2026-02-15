from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .database import SessionLocal, engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_balance_denominations(balance: float, db: Session):
    """Calculate denomination breakdown for balance and update available count"""
    denoms = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
    balance_denoms = []
    remaining = int(balance)
    
    for denom in denoms:
        if remaining >= denom.value and denom.available_count > 0:
            count = min(remaining // denom.value, denom.available_count)
            if count > 0:
                balance_denoms.append({"value": denom.value, "count": count})
                denom.available_count -= count
                db.add(denom)
                remaining -= count * denom.value
    
    # Check if exact balance can be given
    if remaining > 0:
        return None  # Cannot give exact balance
    
    return balance_denoms

def send_email(email: str, invoice_id: int, db: Session):
    """Send invoice email"""
    try:
        invoice = db.query(models.Invoice).filter_by(id=invoice_id).first()
        if not invoice:
            return
        
        subject = "Your Invoice"
        body = f"""
        <h2>Invoice #{invoice.id}</h2>
        <p>Total Amount: {invoice.total_amount}</p>
        <p>Paid Amount: {invoice.paid_amount}</p>
        <p>Balance: {invoice.balance}</p>
        <h3>Items:</h3>
        <ul>
        """
        for item in invoice.items:
            body += f"<li>{item.product_id}: {item.quantity} x {item.price/item.quantity} = {item.price} (Tax: {item.tax})</li>"
        body += "</ul>"
        
        print(f"Sending invoice email to {email}")
        # For production, configure SMTP settings
        # msg = MIMEMultipart()
        # msg['From'] = 'your-email@example.com'
        # msg['To'] = email
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'html'))
    except Exception as e:
        print(f"Error sending email: {e}")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    denominations = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": products,
        "denominations": denominations
    })

@app.post("/purchase", response_class=HTMLResponse)
def purchase(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    product_id: List[str] = Form(default=[]),
    quantity: List[int] = Form(default=[]),
    paid_amount: float = Form(...),
    db: Session = Depends(get_db)
):
    items = []
    total = 0
    
    if not product_id or not quantity:
        products = db.query(models.Product).all()
        denominations = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Please add at least one product",
            "products": products,
            "denominations": denominations
        })

    for pid, qty in zip(product_id, quantity):
        if not pid or qty <= 0:
            continue
            
        product = db.query(models.Product).filter_by(product_id=pid).first()
        if not product:
            continue
        if product.stock < qty:
            products = db.query(models.Product).all()
            denominations = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": f"Insufficient stock for {product.name}",
                "products": products,
                "denominations": denominations
            })

        price = product.price * qty
        tax = price * (product.tax_percent / 100)
        total += price + tax

        product.stock -= qty
        db.add(product)

        items.append(
            models.InvoiceItem(
                product_id=pid,
                quantity=qty,
                price=price,
                tax=tax
            )
        )

    balance = paid_amount - total
    if balance < 0:
        products = db.query(models.Product).all()
        denominations = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Insufficient amount paid",
            "products": products,
            "denominations": denominations
        })

    balance_denoms = calculate_balance_denominations(balance, db)
    
    if balance_denoms is None:
        db.rollback()  # Rollback denomination changes
        products = db.query(models.Product).all()
        denominations = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Insufficient denominations available to give exact change",
            "products": products,
            "denominations": denominations
        })
    
    invoice = models.Invoice(
        email=email,
        total_amount=total,
        paid_amount=paid_amount,
        balance=balance,
        items=items
    )

    for bd in balance_denoms:
        invoice.balance_denoms.append(
            models.BalanceDenomination(
                denomination_value=bd["value"],
                count=bd["count"]
            )
        )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    background_tasks.add_task(send_email, email, invoice.id, SessionLocal())

    return templates.TemplateResponse(
        "bill.html",
        {"request": request, "invoice": invoice}
    )

@app.get("/purchases", response_class=HTMLResponse)
def purchases(request: Request, db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()
    return templates.TemplateResponse(
        "purchases.html",
        {"request": request, "invoices": invoices}
    )

@app.get("/purchase/{invoice_id}", response_class=HTMLResponse)
def purchase_detail(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter_by(id=invoice_id).first()
    if not invoice:
        invoices = db.query(models.Invoice).all()
        return templates.TemplateResponse("purchases.html", {
            "request": request,
            "invoices": invoices,
            "error": "Invoice not found"
        })
    return templates.TemplateResponse(
        "bill.html",
        {"request": request, "invoice": invoice}
    )
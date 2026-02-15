from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    tax_percent = Column(Float)
    
    invoices = relationship("InvoiceItem", back_populates="product")

class Denomination(Base):
    __tablename__ = "denominations"
    
    id = Column(Integer, primary_key=True)
    value = Column(Integer, unique=True)
    available_count = Column(Integer)

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    total_amount = Column(Float)
    paid_amount = Column(Float)
    balance = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    balance_denoms = relationship("BalanceDenomination", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    product_id = Column(String, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    price = Column(Float)
    tax = Column(Float)
    
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoices")

class BalanceDenomination(Base):
    __tablename__ = "balance_denominations"
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    denomination_value = Column(Integer)
    count = Column(Integer)
    
    invoice = relationship("Invoice", back_populates="balance_denoms")
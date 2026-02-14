from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException
from database import SessionLocal, engine
import database_models
from models import Product
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

try:
    database_models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database connection failed: {e}")


@app.get("/")

def greet():
    return "Welcome to AT Innovations"

products=[
    Product(id=1, name="Laptop", description="A high-performance laptop", price=999.99, stock=10),
    Product(id=2, name="Smartphone", description="A latest model smartphone", price=499.99, stock=20),
    Product(id=3, name="Headphones", description="Noise-cancelling headphones", price=199.99, stock=15),
    Product(id=4, name="Smartwatch", description="A smartwatch with various features", price=299.99, stock=5)
]
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = SessionLocal()
    count = db.query(database_models.Product).count()
    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
    db.close()
init_db()


@app.get("/products", response_model=List[Product])
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products

@app.get("/products/{product_id}", response_model=Product)
def find_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.post("/products", response_model=Product)
def add_product(new_product: Product, db: Session = Depends(get_db)):
        db_product = database_models.Product(**new_product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
     

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = updated_product.model_dump()
    for key, value in update_data.items():
        if key != "id" and value is not None:
            setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted successfully"}


from app.db.session import SessionLocal
from app.models.product import Product
from app.services.vector_service import generate_embedding

db = SessionLocal()

# Create a dummy product
title = "Minimalist 10% Vitamin C Serum for Glowing Skin"
vector = generate_embedding(title)

p = Product(
    title=title,
    brand="Minimalist",
    url="https://example.com/vitc",
    price_current=699,
    embedding=vector # <--- We are saving the math!
)

db.add(p)
db.commit()
print("✅ Product Inserted!")
exit()
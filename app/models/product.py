
#We set the vector size to 384. This is not a random number. 
# It is the exact output dimension of the all-MiniLM-L6-v2 model, which is the industry standard for fast, free, CPU-based embeddings (perfect for your free-tier setup).


import uuid
from sqlalchemy import Column, String, Numeric, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector  # <--- The magic import
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, unique=True, index=True, nullable=False)
    
    # Metadata
    brand = Column(String, index=True)
    title = Column(String, nullable=False)
    image_url = Column(String)
    
    # Price Tracking
    price_current = Column(Numeric(10, 2))
    
    # The "Intelligence" Column
    # 384 dimensions matches the 'all-MiniLM-L6-v2' AI model
    embedding = Column(Vector(384))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.title}>"
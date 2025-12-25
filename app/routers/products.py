from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.services.vector_service import generate_embedding

router = APIRouter()

@router.get("/search")
def search_products(q: str, db: Session = Depends(get_db)):
    # 1. Convert the user's text query into a mathematical vector
    query_vector = generate_embedding(q)
    
    # 2. The Magic SQL
    # The operator '<=>' calculates Cosine Distance (Similarity) in Postgres.
    # We order by distance ASC (closest match first).
    sql = text("""
        SELECT id, title, price_current, brand, url, 
               (embedding <=> :vector) as distance
        FROM products
        ORDER BY distance ASC
        LIMIT 5;
    """)
    
    # 3. Execute the query
    # We must cast the list to a string format that pgvector understands
    results = db.execute(sql, {"vector": str(query_vector)}).fetchall() #we do this because postgresql + pgvector expect a string, not an array
    
    # 4. Format the output
    response = []
    for row in results:
        response.append({
            "title": row.title,
            "brand": row.brand,
            "price": row.price_current,
            "match_score": round(1 - row.distance, 2) # Convert distance to % match
        })
        
    return response
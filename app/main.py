from fastapi import FastAPI
from app.routers import auth,products

app = FastAPI(title="Skincare Intelligence API")

# Include the Auth Router
app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "System is running"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth,products

app = FastAPI(title="Skincare Intelligence API")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow the frontend
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],
)

# Include the Auth Router
app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "System is running"}
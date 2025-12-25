import requests
import time
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert
from app.db.session import SessionLocal
from app.models.product import Product
from app.services.vector_service import generate_embedding

# The Targets
TARGETS = [
    # Minimalist is very developer friendly
    {"brand": "Minimalist", "base_url": "https://beminimalist.co"},
    
    # Dr. Sheth's uses standard Shopify
    {"brand": "Dr. Sheth's", "base_url": "https://www.drsheths.com"},
    
    # Dot & Key is also standard Shopify
    {"brand": "Dot & Key", "base_url": "https://www.dotandkey.com"} 
]

def clean_html(html_text: str) -> str:
    """
    Shopify returns descriptions full of HTML tags.
    We need plain text for the AI to understand it.
    """
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def scrape_shopify(brand: str, base_url: str):
    print(f"🔵 Starting Scrape: {brand}...")
    page = 1
    db = SessionLocal()
    
    # Masquerade as a browser to avoid basic 403 blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        # The Hidden API Endpoint
        endpoint = f"{base_url}/products.json?page={page}&limit=250"
        
        try:
            r = requests.get(endpoint,headers=headers, timeout=15) #does not return Json or text but a HTTP reponse wrapper
            #response object has a status code and a body which is JSON incase of shopify
           # If the brand hides their API (like Derma Co), we skip it gracefully
            if r.status_code == 403 or r.status_code == 404:
                print(f"   ❌ Endpoint blocked or not found: {endpoint}")
                break
                
            if r.status_code != 200:
                print(f"   ⚠️ Status {r.status_code}, skipping page.")
                break
            
            data = r.json()  #data is a dictionary
            #Network sends bytes → requests decodes to string → .json() converts string → Python objects
            products = data.get("products", []) #syntax -> dict.get(key, default)
            
            if not products:
                print("   ✅ Finished (End of list)")
                break
            
            print(f"   📄 Page {page}: Processing {len(products)} products...")
            
            for p in products:
                # 1. Parse Basic Data
                title = p.get("title")
                handle = p.get("handle")
                url = f"{base_url}/products/{handle}"
                
                # Get Price (from first variant)
                variants = p.get("variants", [])
                price = variants[0].get("price") if variants else 0
                
                # Get Description (Ingredients often hidden here)
                raw_html = p.get("body_html", "")
                clean_desc = clean_html(raw_html)
                
                # 2. Check for Duplicates (Don't re-embed if not needed)
                # In a real system, we might check last_updated timestamps.
                # For this MVP, we just overwrite.
                
                # 3. Generate Vector (The CPU Heavy part)
                # We combine Title + Description for better search matches
                text_to_embed = f"{title} {clean_desc[:1000]}"  #1000 characters limit for description text
                embedding = generate_embedding(text_to_embed)
                
                # 4. Upsert into DB (Postgres specific)
                stmt = insert(Product).values(
                    title=title,
                    brand=brand,
                    url=url,
                    price_current=float(price),
                    embedding=embedding,
                    image_url=p.get("images")[0].get("src") if p.get("images") else None
                )
                
                # If URL exists, just update the price
                #If this INSERT causes a conflict, UPDATE the existing row instead.
                stmt = stmt.on_conflict_do_update(
                    index_elements=['url'], #conflict if another row already has the same url
                    set_=dict(price_current=stmt.excluded.price_current) #exclude means the row which was excluded during insert because of conflict
                )
                
                db.execute(stmt)
            
            db.commit() # Commit after every page
            page += 1
            time.sleep(1) # pauses execution for one second
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            break
            
    db.close()
#Run this code only when this file is executed directly —NOT when it’s imported as a module
if __name__ == "__main__":
    for t in TARGETS:
        scrape_shopify(t["brand"], t["base_url"])



#Because your scraper imports app.*, you must run it as a module from the project root (python -m scraper.main) so Python can resolve those imports correctly.
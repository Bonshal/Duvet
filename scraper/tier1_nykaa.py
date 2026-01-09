import time
from playwright.sync_api import sync_playwright
from sqlalchemy.dialects.postgresql import insert
from app.db.session import SessionLocal
from app.models.product import Product
from app.services.vector_service import generate_embedding

# Category URLs
START_URLS = [
    "https://www.nykaa.com/skin/serums/c/8393",
    "https://www.nykaa.com/skin/moisturizers/c/8392"
]

def scrape_nykaa():
    print("🟣 Starting Tier 1 Scrape: Nykaa (Stealth Mode)...")
    
    with sync_playwright() as p:
        # 1. Launch Browser with HTTP/2 DISABLED
        # This fixes the 'ERR_HTTP2_PROTOCOL_ERROR'
        browser = p.chromium.launch(
            headless=False,  # Set to False so you can see it working!
            args=[
                '--disable-http2', 
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        
        # 2. Configure the "Fingerprint"
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768},
            ignore_https_errors=True,
            java_script_enabled=True
        )

        # 3. Patch the 'navigator.webdriver' property
        # This stops the site from knowing it's being controlled by code
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()
        db = SessionLocal()

        for url in START_URLS:
            print(f"   🔎 Visiting: {url}")
            try:
                # Increased timeout to 60 seconds
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                # 4. Human-like Scrolling
                print("      Scrolling to load images...")
                for _ in range(5): 
                    page.mouse.wheel(0, 5000)
                    time.sleep(3) # Wait for network requests
                
                # 5. Extract Data
                # Note: Nykaa class names change. If this finds 0 products, 
                # we need to inspect the site and check these classes:
                # Card: div.product-wrapper OR div.css-d5z3ro
                # Title: div.css-xrzmfa
                # Link: a.css-qlopj4
                
                # Broad selector to catch the cards
                product_cards = page.query_selector_all('div.product-wrapper')
                
                if not product_cards:
                    # Fallback for different layout
                    product_cards = page.query_selector_all('div.css-d5z3ro')

                print(f"      Found {len(product_cards)} products.")

                for card in product_cards:
                    try:
                        # Extract Title (Try multiple selectors if one fails)
                        title_el = card.query_selector('div.css-xrzmfa')
                        if not title_el:
                            title_el = card.query_selector('.product-listing_product-title')
                        if not title_el: continue
                        
                        title = title_el.inner_text()

                        # Extract Link
                        link_el = card.query_selector('a')
                        if not link_el: continue
                        href = link_el.get_attribute('href')
                        link = "https://www.nykaa.com" + href if href.startswith('/') else href
                        
                        # Extract Price
                        price_el = card.query_selector('span.css-111i9a8')
                        if not price_el:
                            price_el = card.query_selector('.product-listing_price')
                        
                        price_text = "0"
                        if price_el:
                            price_text = price_el.inner_text().replace('₹', '').replace(',', '').split('MRP')[0]

                        # 6. Save to DB
                        embedding = generate_embedding(title)
                        
                        stmt = insert(Product).values(
                            title=title,
                            brand="Nykaa Aggregated",
                            url=link,
                            price_current=float(price_text) if price_text.strip() else 0,
                            embedding=embedding
                        )
                        stmt = stmt.on_conflict_do_update(
                            index_elements=['url'],
                            set_=dict(price_current=stmt.excluded.price_current)
                        )
                        db.execute(stmt)

                    except Exception as e:
                        continue 

                db.commit()
                print("      ✅ Batch saved.")

            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        browser.close()
        db.close()

if __name__ == "__main__":
    scrape_nykaa()
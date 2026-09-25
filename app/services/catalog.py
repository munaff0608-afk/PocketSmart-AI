from urllib.parse import quote

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k=",
    "Flipkart": "https://www.flipkart.com/search?q=",
    "IKEA": "https://www.ikea.com/in/en/search/?q=",
    "Swiggy": "https://www.swiggy.com/search?query=",
    "Zomato": "https://www.zomato.com/search?q=",
    "OYO": "https://www.oyorooms.com/search?location=",
}

def platform_link(platform: str, query: str) -> str:
    base = PLATFORMS.get(platform, PLATFORMS["Amazon"])
    return base + quote(query)

def build_mock_catalog(category: str, budget: float) -> list[dict]:
    # Demo-safe simulated sourcing, as permitted by the project document.
    if category == "home":
        return [
            {"name": "Minimal LED Ceiling Light", "platform": "IKEA", "price": 1499, "query": "LED ceiling light"},
            {"name": "Modern Study/Side Table", "platform": "Amazon", "price": 2499, "query": "modern side table"},
            {"name": "Decorative Wall Art Set", "platform": "Flipkart", "price": 1199, "query": "wall art set"},
            {"name": "Comfort Accent Chair", "platform": "IKEA", "price": 6999, "query": "accent chair"},
            {"name": "Ceiling Fan 1200mm", "platform": "Amazon", "price": 3299, "query": "1200mm ceiling fan"},
        ]
    if category == "party":
        return [
            {"name": "Party Catering Search", "platform": "Swiggy", "price": 0, "query": "party catering"},
            {"name": "Restaurant & Catering Search", "platform": "Zomato", "price": 0, "query": "party catering"},
            {"name": "Event Decoration Search", "platform": "Amazon", "price": 2499, "query": "birthday decoration"},
            {"name": "Event Stay Search", "platform": "OYO", "price": 0, "query": "event stay"},
        ]
    return [
        {"name": "Elegant Gold-Tone Necklace", "platform": "Amazon", "price": 1899, "query": "elegant necklace"},
        {"name": "Minimal Drop Earrings", "platform": "Flipkart", "price": 899, "query": "drop earrings"},
        {"name": "Classic Bracelet", "platform": "Amazon", "price": 1299, "query": "classic bracelet"},
        {"name": "Statement Earrings", "platform": "Flipkart", "price": 1599, "query": "statement earrings"},
    ]

def enrich_links(items: list[dict]) -> list[dict]:
    result = []
    for item in items:
        item = dict(item)
        item["url"] = platform_link(item["platform"], item["query"])
        result.append(item)
    return result

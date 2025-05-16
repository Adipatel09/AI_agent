"""
Product catalog for the Pocket AI e-commerce agent.
This module contains the product database used for recommendations and searches.
"""

# Product database - directly converted from JavaScript version
products = [
    # Clothing - T-shirts
    {"id": 1, "name": "Sports T-Shirt (Breathable)", "category": "clothing", "type": "t-shirt", 
     "tags": ["sports", "running", "gym", "breathable"], "price": 29.99, "image": "sport-tshirt-1.jpg"},
    {"id": 2, "name": "Athletic Performance T-Shirt", "category": "clothing", "type": "t-shirt", 
     "tags": ["sports", "athletics", "performance"], "price": 34.99, "image": "sport-tshirt-2.jpg"},
    {"id": 3, "name": "Moisture-Wicking Running Shirt", "category": "clothing", "type": "t-shirt", 
     "tags": ["sports", "running", "moisture-wicking"], "price": 32.99, "image": "sport-tshirt-3.jpg"},
    {"id": 4, "name": "Casual Cotton T-Shirt", "category": "clothing", "type": "t-shirt", 
     "tags": ["casual", "cotton", "everyday"], "price": 19.99, "image": "casual-tshirt-1.jpg"},
    {"id": 5, "name": "Dress Shirt (Formal)", "category": "clothing", "type": "shirt", 
     "tags": ["formal", "business", "dress"], "price": 59.99, "image": "dress-shirt-1.jpg"},
    
    # Electronics
    {"id": 6, "name": "Smart Watch (Fitness Tracking)", "category": "electronics", "type": "watch", 
     "tags": ["fitness", "tracking", "smart", "wearable"], "price": 199.99, "image": "smartwatch-1.jpg"},
    {"id": 7, "name": "Wireless Earbuds", "category": "electronics", "type": "audio", 
     "tags": ["wireless", "audio", "earbuds", "music"], "price": 129.99, "image": "earbuds-1.jpg"},
    {"id": 8, "name": "Laptop Backpack", "category": "accessories", "type": "bag", 
     "tags": ["laptop", "backpack", "travel", "storage"], "price": 79.99, "image": "backpack-1.jpg"},
    {"id": 9, "name": "Running Shoes", "category": "footwear", "type": "shoes", 
     "tags": ["running", "sports", "athletic", "footwear"], "price": 89.99, "image": "running-shoes-1.jpg"},
    {"id": 10, "name": "Yoga Mat", "category": "fitness", "type": "equipment", 
     "tags": ["yoga", "fitness", "exercise", "mat"], "price": 45.99, "image": "yoga-mat-1.jpg"},
    
    # Additional Electronics
    {"id": 11, "name": "4K Smart TV (55-inch)", "category": "electronics", "type": "television", 
     "tags": ["4k", "smart", "tv", "entertainment"], "price": 499.99, "image": "smart-tv.jpg"},
    {"id": 12, "name": "Bluetooth Speaker", "category": "electronics", "type": "audio", 
     "tags": ["bluetooth", "speaker", "wireless", "music"], "price": 89.99, "image": "bluetooth-speaker.jpg"},
    {"id": 13, "name": "Gaming Laptop", "category": "electronics", "type": "computer", 
     "tags": ["gaming", "laptop", "high-performance", "computer"], "price": 1299.99, "image": "gaming-laptop.jpg"},
    {"id": 14, "name": "Digital Camera (Mirrorless)", "category": "electronics", "type": "camera", 
     "tags": ["camera", "digital", "photography", "mirrorless"], "price": 799.99, "image": "digital-camera.jpg"},
    {"id": 15, "name": "Tablet with Stylus", "category": "electronics", "type": "tablet", 
     "tags": ["tablet", "stylus", "digital", "drawing"], "price": 349.99, "image": "tablet.jpg"},
    
    # Home and Kitchen
    {"id": 16, "name": "Coffee Maker", "category": "home", "type": "kitchen", 
     "tags": ["coffee", "kitchen", "appliance", "brewing"], "price": 119.99, "image": "coffee-maker.jpg"},
    {"id": 17, "name": "Air Fryer", "category": "home", "type": "kitchen", 
     "tags": ["cooking", "air fryer", "kitchen", "appliance"], "price": 89.99, "image": "air-fryer.jpg"},
    {"id": 18, "name": "Robot Vacuum Cleaner", "category": "home", "type": "cleaning", 
     "tags": ["vacuum", "robot", "cleaning", "smart"], "price": 249.99, "image": "robot-vacuum.jpg"},
    {"id": 19, "name": "Bed Sheets Set (Queen)", "category": "home", "type": "bedding", 
     "tags": ["sheets", "bedding", "cotton", "queen"], "price": 59.99, "image": "bed-sheets.jpg"},
    {"id": 20, "name": "Smart Light Bulbs (4-Pack)", "category": "home", "type": "lighting", 
     "tags": ["smart", "lighting", "bulbs", "wifi"], "price": 49.99, "image": "smart-bulbs.jpg"},
    
    # More Clothing
    {"id": 21, "name": "Denim Jeans", "category": "clothing", "type": "pants", 
     "tags": ["jeans", "denim", "casual", "everyday"], "price": 59.99, "image": "jeans.jpg"},
    {"id": 22, "name": "Winter Jacket", "category": "clothing", "type": "outerwear", 
     "tags": ["winter", "jacket", "warm", "waterproof"], "price": 129.99, "image": "winter-jacket.jpg"},
    {"id": 23, "name": "Summer Dress", "category": "clothing", "type": "dress", 
     "tags": ["summer", "dress", "casual", "floral"], "price": 49.99, "image": "summer-dress.jpg"},
    {"id": 24, "name": "Formal Suit", "category": "clothing", "type": "formal", 
     "tags": ["suit", "formal", "business", "professional"], "price": 199.99, "image": "formal-suit.jpg"},
    {"id": 25, "name": "Workout Leggings", "category": "clothing", "type": "activewear", 
     "tags": ["leggings", "workout", "gym", "stretch"], "price": 39.99, "image": "leggings.jpg"},
    
    # Additional Footwear
    {"id": 26, "name": "Casual Sneakers", "category": "footwear", "type": "sneakers", 
     "tags": ["casual", "sneakers", "comfortable", "everyday"], "price": 69.99, "image": "casual-sneakers.jpg"},
    {"id": 27, "name": "Formal Leather Shoes", "category": "footwear", "type": "formal", 
     "tags": ["formal", "leather", "business", "shoes"], "price": 119.99, "image": "leather-shoes.jpg"},
    {"id": 28, "name": "Hiking Boots", "category": "footwear", "type": "boots", 
     "tags": ["hiking", "boots", "outdoor", "waterproof"], "price": 149.99, "image": "hiking-boots.jpg"},
    {"id": 29, "name": "Sandals", "category": "footwear", "type": "sandals", 
     "tags": ["summer", "sandals", "beach", "casual"], "price": 34.99, "image": "sandals.jpg"},
    {"id": 30, "name": "Indoor Slippers", "category": "footwear", "type": "slippers", 
     "tags": ["indoor", "slippers", "comfortable", "home"], "price": 24.99, "image": "slippers.jpg"},
    
    # Books and Media
    {"id": 31, "name": "Bestselling Novel", "category": "books", "type": "fiction", 
     "tags": ["novel", "fiction", "bestseller", "reading"], "price": 18.99, "image": "novel.jpg"},
    {"id": 32, "name": "Cookbook", "category": "books", "type": "non-fiction", 
     "tags": ["cooking", "recipes", "food", "chef"], "price": 29.99, "image": "cookbook.jpg"},
    {"id": 33, "name": "Programming Reference", "category": "books", "type": "education", 
     "tags": ["programming", "education", "reference", "coding"], "price": 39.99, "image": "programming-book.jpg"},
    {"id": 34, "name": "Historical Biography", "category": "books", "type": "non-fiction", 
     "tags": ["history", "biography", "non-fiction", "educational"], "price": 27.99, "image": "biography.jpg"},
    {"id": 35, "name": "Science Fiction Collection", "category": "books", "type": "fiction", 
     "tags": ["sci-fi", "collection", "fiction", "fantasy"], "price": 45.99, "image": "sci-fi-books.jpg"},
    
    # Sports and Fitness
    {"id": 36, "name": "Adjustable Dumbbells Set", "category": "fitness", "type": "weights", 
     "tags": ["dumbbells", "weights", "adjustable", "home gym"], "price": 179.99, "image": "dumbbells.jpg"},
    {"id": 37, "name": "Exercise Bike", "category": "fitness", "type": "cardio", 
     "tags": ["bike", "exercise", "cardio", "stationary"], "price": 349.99, "image": "exercise-bike.jpg"},
    {"id": 38, "name": "Tennis Racket", "category": "sports", "type": "tennis", 
     "tags": ["tennis", "racket", "sports", "outdoor"], "price": 89.99, "image": "tennis-racket.jpg"},
    {"id": 39, "name": "Basketball", "category": "sports", "type": "basketball", 
     "tags": ["basketball", "sports", "indoor", "outdoor"], "price": 29.99, "image": "basketball.jpg"},
    {"id": 40, "name": "Fitness Tracker Band", "category": "fitness", "type": "wearable", 
     "tags": ["fitness", "tracker", "band", "health"], "price": 59.99, "image": "fitness-band.jpg"},
    
    # Beauty and Personal Care
    {"id": 41, "name": "Facial Cleanser", "category": "beauty", "type": "skincare", 
     "tags": ["facial", "cleanser", "skincare", "face"], "price": 24.99, "image": "facial-cleanser.jpg"},
    {"id": 42, "name": "Hair Dryer", "category": "beauty", "type": "haircare", 
     "tags": ["hair", "dryer", "styling", "blowout"], "price": 49.99, "image": "hair-dryer.jpg"},
    {"id": 43, "name": "Electric Razor", "category": "personal-care", "type": "shaving", 
     "tags": ["razor", "electric", "shaving", "grooming"], "price": 79.99, "image": "electric-razor.jpg"},
    {"id": 44, "name": "Makeup Set", "category": "beauty", "type": "makeup", 
     "tags": ["makeup", "set", "cosmetics", "beauty"], "price": 59.99, "image": "makeup-set.jpg"},
    {"id": 45, "name": "Perfume", "category": "beauty", "type": "fragrance", 
     "tags": ["perfume", "fragrance", "scent", "luxury"], "price": 89.99, "image": "perfume.jpg"},
    
    # Toys and Games
    {"id": 46, "name": "Board Game Set", "category": "toys", "type": "games", 
     "tags": ["board game", "family", "fun", "strategy"], "price": 34.99, "image": "board-game.jpg"},
    {"id": 47, "name": "Video Game Console", "category": "toys", "type": "gaming", 
     "tags": ["console", "video game", "gaming", "entertainment"], "price": 399.99, "image": "game-console.jpg"},
    {"id": 48, "name": "Remote Control Car", "category": "toys", "type": "rc", 
     "tags": ["remote control", "car", "toy", "racing"], "price": 59.99, "image": "rc-car.jpg"},
    {"id": 49, "name": "Building Blocks Set", "category": "toys", "type": "building", 
     "tags": ["blocks", "building", "creative", "kids"], "price": 39.99, "image": "building-blocks.jpg"},
    {"id": 50, "name": "Plush Teddy Bear", "category": "toys", "type": "plush", 
     "tags": ["teddy bear", "plush", "soft", "kids"], "price": 19.99, "image": "teddy-bear.jpg"}
]


def get_product_by_id(product_id):
    """Get a product by its ID."""
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def get_products_by_category(category):
    """Get all products in a specific category."""
    return [product for product in products if product["category"] == category]


def get_products_by_search(query):
    """Search for products matching a query string."""
    query = query.lower()
    matching_products = []
    
    for product in products:
        # Check if query appears in product name, category, or type
        if (query in product["name"].lower() or 
            query in product["category"].lower() or 
            query in product["type"].lower()):
            matching_products.append(product)
            continue
            
        # Check if query appears in any tags
        if any(query in tag.lower() for tag in product["tags"]):
            matching_products.append(product)
            
    return matching_products


def get_product_summary():
    """Get a summary of all products for AI prompts."""
    return "\n".join([
        f"ID {p['id']}: {p['name']} (${p['price']}) - Category: {p['category']}, "
        f"Type: {p['type']}, Tags: [{', '.join(p['tags'])}]" 
        for p in products
    ])


def get_random_products(count=3):
    """Get a random selection of products."""
    import random
    
    # Organize products by category
    products_by_category = {}
    for product in products:
        category = product["category"]
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)
    
    # Get unique categories
    categories = list(products_by_category.keys())
    
    # Initialize result list
    result = []
    
    # Try to get one product from each category
    shuffled_categories = list(categories)
    random.shuffle(shuffled_categories)
    
    # Take up to 'count' categories
    categories_to_use = shuffled_categories[:count]
    
    # Get one random product from each selected category
    for category in categories_to_use:
        category_products = products_by_category[category]
        random_product = random.choice(category_products)
        result.append(random_product)
    
    # If we still need more products, get random ones
    if len(result) < count:
        remaining = count - len(result)
        already_selected_ids = [p["id"] for p in result]
        
        # Select from remaining products not already in the result
        remaining_products = [p for p in products if p["id"] not in already_selected_ids]
        shuffled_remaining = random.sample(remaining_products, 
                                           min(remaining, len(remaining_products)))
        
        # Add remaining products
        result.extend(shuffled_remaining)
    
    return result 
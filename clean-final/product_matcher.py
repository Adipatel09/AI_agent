#!/usr/bin/env python3
"""
Product Matcher - A script to analyze product images and provide detailed product recommendations
with explanations about how each product relates to the image description.
"""

import os
import sys
import json
import base64
import requests
import subprocess
import logging
from typing import List, Dict, Any, Optional

# Make sure the current directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add the backend directory to the path so we can import from it
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import products from backend/products.py
try:
    from backend.products import products, get_product_by_id, get_product_summary, get_random_products
except ImportError:
    # Fallback import if the first attempt fails
    sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
    from products import products, get_product_by_id, get_product_summary, get_random_products

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("product_matcher")

# Helper function to get product features from tags
def get_product_features(product):
    """Extract features from product tags and other attributes."""
    features = []
    
    # Add type as a feature
    features.append(f"{product['type'].capitalize()}")
    
    # Add category-specific features
    if product['category'] == 'electronics':
        features.append("Modern technology")
        if 'smart' in product['tags']:
            features.append("Smart features")
        if 'wireless' in product['tags']:
            features.append("Wireless capability")
    
    elif product['category'] == 'clothing':
        if 'casual' in product['tags']:
            features.append("Casual style")
        if 'formal' in product['tags']:
            features.append("Formal style")
        if 'breathable' in product['tags']:
            features.append("Breathable fabric")
    
    elif product['category'] == 'books':
        if 'fiction' in product['tags']:
            features.append("Fiction content")
        if 'non-fiction' in product['tags']:
            features.append("Non-fiction content")
        if 'education' in product['tags']:
            features.append("Educational material")
    
    # Add general features from tags
    for tag in product['tags']:
        if tag not in features and tag not in ['casual', 'formal', 'smart', 'wireless']:
            features.append(tag.capitalize())
    
    return features[:4]  

# Helper function to get product colors
def get_product_colors(product):
    """Extract colors from product tags and name."""
    colors = []
    common_colors = ["black", "white", "red", "blue", "green", "yellow", "purple", "pink", 
                    "orange", "brown", "gray", "silver", "gold"]
    
    # Check tags for colors
    for tag in product['tags']:
        if tag.lower() in common_colors:
            colors.append(tag.capitalize())
    
    # Check name for colors
    for color in common_colors:
        if color in product['name'].lower() and color.capitalize() not in colors:
            colors.append(color.capitalize())
    
    # Default color if none found
    if not colors:
        if product['category'] == 'electronics':
            colors = ["Black", "Silver"]
        elif product['category'] == 'books':
            colors = ["Multi-colored"]
        else:
            colors = ["Various"]
    
    return colors

# Helper function to get product use cases
def get_product_use_cases(product):
    """Extract use cases from product tags and category."""
    use_cases = []
    
    # Add category-specific use cases
    if product['category'] == 'books':
        use_cases.extend(["Reading", "Learning", "Entertainment"])
        if 'education' in product['type'] or 'education' in product['tags']:
            use_cases.append("Study")
        if 'fiction' in product['type'] or 'fiction' in product['tags']:
            use_cases.append("Leisure reading")
    
    elif product['category'] == 'electronics':
        use_cases.append("Technology use")
        if 'entertainment' in product['tags']:
            use_cases.append("Entertainment")
    
    elif product['category'] == 'clothing':
        use_cases.append("Everyday wear")
        if 'formal' in product['tags']:
            use_cases.append("Professional settings")
        if 'casual' in product['tags']:
            use_cases.append("Casual outings")
    
    # Add use cases from tags
    for tag in product['tags']:
        potential_use = f"{tag.capitalize()} activities"
        if potential_use not in use_cases and tag not in ['casual', 'formal']:
            use_cases.append(potential_use)
    
    return use_cases[:4]  # Limit to 4 use cases

def get_enhanced_product_summary() -> str:
    """Generate a detailed summary of all products in the catalog with enhanced attributes."""
    summary_parts = []
    
    for product in products:
        # Extract additional attributes
        features = get_product_features(product)
        colors = get_product_colors(product)
        use_cases = get_product_use_cases(product)
        
        features_str = ", ".join(features)
        colors_str = ", ".join(colors)
        use_cases_str = ", ".join(use_cases)
        tags_str = ", ".join(product["tags"])
        
        summary = (
            f"Product ID: {product['id']} - {product['name']} (${product['price']:.2f})\n"
            f"Category: {product['category']}\n"
            f"Type: {product['type']}\n"
            f"Description: {product['name']} - {product['category']} {product['type']} - {tags_str}\n"
            f"Features: {features_str}\n"
            f"Available Colors: {colors_str}\n"
            f"Use Cases: {use_cases_str}\n"
        )
        summary_parts.append(summary)
    
    return "\n\n".join(summary_parts)

def analyze_image(image_path: str) -> Optional[str]:
    """
    Analyze an image using Ollama's vision model with multiple fallback methods.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Image description or None if analysis fails
    """
    logger.info(f"Analyzing image: {image_path}")
    
    # Verify the image exists
    if not os.path.exists(image_path):
        logger.error(f"Image not found: {image_path}")
        return None
    
    # Create a detailed analysis prompt
    analysis_prompt = """Analyze this product image in detail and provide a comprehensive description of:
1) What type of product or item is shown
2) What category it belongs to (clothing, electronics, accessories, books, etc.)
3) Its apparent color(s), material(s), and texture(s)
4) Any distinctive features, patterns, or design elements
5) What the product might be used for
6) Any visible brand identifiers or logos
7) The apparent size, shape, and form factor

Be specific and detailed in your analysis. Focus only on what you can actually see in the image."""
    
    # Method 1: Try Ollama CLI with -i flag (most reliable for image input)
    try:
        logger.info("Trying image analysis with Ollama CLI...")
        import shlex
        escaped_prompt = shlex.quote(analysis_prompt)
        escaped_path = shlex.quote(image_path)
        
        cmd = f'ollama run llava -i {escaped_path} {escaped_prompt}'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout.strip() and "I cannot see any images" not in result.stdout:
            logger.info("CLI image analysis succeeded!")
            return result.stdout.strip()
    except Exception as e:
        logger.warning(f"CLI image analysis failed: {str(e)}")
    
    # Method 2: Try with Ollama API using base64 encoding
    try:
        logger.info("Trying image analysis with Ollama API...")
        # Read and encode the image
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llava",
                "prompt": analysis_prompt,
                "images": [img_base64],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            analysis = response.json().get("response", "")
            if analysis and "I cannot see any images" not in analysis:
                logger.info("API image analysis succeeded!")
                return analysis
    except Exception as e:
        logger.warning(f"API image analysis failed: {str(e)}")
    
    # Method 3: Try with direct backend integration if available
    try:
        logger.info("Trying image analysis with backend integration...")
        # Check if we can import the backend module
        try:
            from backend.ai_utils import ImageAnalyzer
            
            # Use the ImageAnalyzer directly
            import asyncio
            analysis = asyncio.run(ImageAnalyzer.analyze_product_image(image_path))
            
            if analysis and "I cannot see any images" not in analysis:
                logger.info("Backend integration image analysis succeeded!")
                return analysis
        except ImportError:
            logger.warning("Backend integration not available")
    except Exception as e:
        logger.warning(f"Backend integration image analysis failed: {str(e)}")
    
    # Method 4: Fallback to a generic description
    logger.warning("All image analysis methods failed, using fallback description.")
    return """This appears to be a product image, but I couldn't analyze it in detail. 
The image might contain an item that could be in one of our popular categories like electronics, 
clothing, home goods, or accessories."""

def get_product_recommendations(image_description: str) -> Optional[str]:
    """
    Generate detailed product recommendation based on image description.
    
    Args:
        image_description: Description of the image
        
    Returns:
        Detailed product recommendation with explanation
    """
    logger.info("Generating product recommendation...")
    
    # Extract key terms and categories from the image description
    description_lower = image_description.lower()
    
    # Identify key categories in the description
    key_categories = []
    category_keywords = {
        "books": ["book", "novel", "reading", "literature", "textbook", "cookbook", "fiction", "non-fiction"],
        "electronics": ["smartphone", "phone", "laptop", "computer", "tablet", "electronic", "device", "gadget", "camera"],
        "home": ["kitchen", "home", "house", "furniture", "appliance", "decor"],
        "clothing": ["shirt", "pants", "dress", "jacket", "clothing", "wear", "fashion"],
        "fitness": ["fitness", "exercise", "workout", "gym", "training"],
        "accessories": ["accessory", "accessories", "bag", "watch", "jewelry"],
        "footwear": ["shoes", "sneakers", "boots", "footwear", "sandals"],
        "beauty": ["beauty", "skincare", "makeup", "cosmetics"],
        "toys": ["toy", "game", "gaming", "play"],
        "sports": ["sports", "athletic", "outdoor"]
    }
    
    # Check for category keywords in the description
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in description_lower:
                key_categories.append(category)
                break
    
    # Remove duplicates
    key_categories = list(set(key_categories))
    logger.info(f"Detected categories: {key_categories}")
    
    # Define a scoring function to rank products by relevance to the description
    def score_product(product):
        score = 0
        product_category = product["category"]
        
        # Prioritize products in the detected categories
        if product_category in key_categories:
            score += 20
        
        # Special handling for books
        if "book" in description_lower and product_category == "books":
            score += 30
            
            # Check for specific book types
            if "cookbook" in description_lower and "cookbook" in product["name"].lower():
                score += 20
            if "programming" in description_lower and "programming" in product["name"].lower():
                score += 20
            if "fiction" in description_lower and "fiction" in product["type"]:
                score += 15
            if "non-fiction" in description_lower and "non-fiction" in product["type"]:
                score += 15
        
        # Check product name in description
        product_name_lower = product["name"].lower()
        if product_name_lower in description_lower:
            score += 15
        else:
            # Check individual words in product name
            for word in product_name_lower.split():
                if len(word) > 3 and word in description_lower:
                    score += 3
            
        # Check product category in description
        if product_category.lower() in description_lower:
            score += 10
            
        # Check product type
        if product["type"].lower() in description_lower:
            score += 8
                
        # Check tags
        for tag in product["tags"]:
            if tag.lower() in description_lower:
                score += 5
            elif len(tag) > 3:
                # Check individual words in multi-word tags
                for word in tag.lower().split():
                    if len(word) > 3 and word in description_lower:
                        score += 1
        
        # Check colors
        common_colors = ["black", "white", "red", "blue", "green", "yellow", "purple", "pink", 
                        "orange", "brown", "gray", "silver", "gold"]
        for color in common_colors:
            if color in description_lower and (color in product_name_lower or 
                                              any(color in tag.lower() for tag in product["tags"])):
                score += 3
                
        # Brand name bonuses
        brands = ["canon", "nikon", "sony", "apple", "samsung", "google"]
        for brand in brands:
            if brand in description_lower and brand in product_name_lower:
                score += 10
                        
        return score
    
    # Score all products and rank them
    scored_products = [(product, score_product(product)) for product in products]
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # Log scores for debugging
    logger.info("Product scores:")
    for product, score in scored_products[:3]:
        logger.info(f"{product['name']}: {score}")
    
    # Take only the best matching product
    best_product = scored_products[0][0]
    
    # If the best score is very low, try to find a better match
    if scored_products[0][1] < 5:
        logger.warning("No good match found, selecting best category match")
        
        # If we detected categories, prioritize those
        if key_categories:
            for category in key_categories:
                matching_products = [p for p in products if p["category"] == category]
                if matching_products:
                    best_product = matching_products[0]
                    break
    
    # Generate detailed explanation for the best product
    product = best_product
    
    # Find matching elements between product and description
    matches = []
    product_category = product["category"]
    
    # Check category match
    if product_category.lower() in description_lower:
        matches.append(f"Category match: {product_category}")
    elif product_category in key_categories:
        matches.append(f"Category match: {product_category} (detected from keywords)")
        
    # Check for brand matches
    brands = ["canon", "nikon", "sony", "apple", "samsung", "google"]
    for brand in brands:
        if brand in description_lower and brand in product["name"].lower():
            matches.append(f"Brand match: {brand.title()}")
    
    # Check color matches
    common_colors = ["black", "white", "red", "blue", "green", "yellow", "purple", "pink", 
                    "orange", "brown", "gray", "silver", "gold"]
    color_matches = []
    for color in common_colors:
        if color in description_lower and (color in product["name"].lower() or 
                                           any(color in tag.lower() for tag in product["tags"])):
            color_matches.append(color.capitalize())
            
    if color_matches:
        matches.append(f"Color match: {', '.join(color_matches)}")
        
    # Check tag matches
    tag_matches = []
    for tag in product["tags"]:
        if tag.lower() in description_lower:
            tag_matches.append(tag)
    
    if tag_matches:
        matches.append(f"Feature matches: {', '.join(tag_matches)}")
    
    # Get enhanced product attributes
    features = get_product_features(product)
    colors = get_product_colors(product)
    use_cases = get_product_use_cases(product)
    
    # Create a detailed recommendation
    recommendation = f"""## Best Match: {product['name']} (${product['price']:.2f})

Product ID: {product['id']}

### Why This Product Matches:
This {product_category.capitalize()} product aligns with the image description because:
"""
    
    # Add matching elements or a generic explanation if no specific matches
    if matches:
        for match in matches:
            recommendation += f"- {match}\n"
    else:
        recommendation += f"- It belongs to the {product_category} category which could fit the item shown\n"
        recommendation += f"- It has features like {', '.join(features[:2])}\n"
        recommendation += f"- It's available in colors including {', '.join(colors)}\n"
    
    # Add product details
    recommendation += f"""
### Product Details:
- {product['name']} - {product_category.capitalize()} {product['type']}
- Key features: {', '.join(features)}
- Available colors: {', '.join(colors)}
- Ideal for: {', '.join(use_cases)}
- Tags: {', '.join(product['tags'])}

### How It Relates to the Image:
"""
    
    # Create a contextual explanation based on the product and image description
    if "book" in description_lower and product_category == "books":
        if "collection" in product["name"].lower() or "set" in product["name"].lower():
            recommendation += "The image shows a stack of books, and this product is a collection of books that would be similar to what's shown in the image.\n"
        else:
            recommendation += f"The image shows books, and this {product['type']} book would be a valuable addition to the collection shown.\n"
            
        if "fiction" in product["type"] and "fiction" in description_lower:
            recommendation += "The books in the image appear to be fiction titles, which is exactly what this product offers.\n"
        elif "non-fiction" in product["type"] and "non-fiction" in description_lower:
            recommendation += "The books in the image appear to be non-fiction titles, which is exactly what this product offers.\n"
        
    elif "camera" in description_lower and product_category == "electronics" and "camera" in product["type"]:
        recommendation += "The image shows a camera, and this product is a camera with similar features to what's shown in the image.\n"
    elif "electronics" in description_lower and product_category == "electronics":
        recommendation += "The image shows an electronic device, and this product provides modern technology features to meet similar needs.\n"
    elif "clothing" in description_lower and product_category == "clothing":
        recommendation += "The image shows a clothing item, and this product offers comfortable, stylish options that match that category.\n"
    elif "home" in description_lower and product_category == "home":
        recommendation += "The image shows a home item, and this product would complement such household needs.\n"
    elif any(color in description_lower for color in colors):
        matching_colors = [color for color in colors if color.lower() in description_lower]
        recommendation += f"The image shows an item with similar coloring ({', '.join(matching_colors)}), matching this product's aesthetic.\n"
    else:
        # Generic explanation connecting image to product
        recommendation += f"Based on what's shown in the image, this {product_category} product would complement the item's use case and provide additional value.\n"
    
    # Clean up any standalone # characters that might appear in the text
    recommendation = recommendation.replace('\n#\n', '\n\n')
    recommendation = recommendation.replace('\n# \n', '\n\n')
    recommendation = recommendation.replace('\n#', '\n')
    recommendation = recommendation.replace(' # ', ' ')
    # Additional cleanup for standalone # characters
    recommendation = recommendation.replace('#\n', '\n')
    recommendation = recommendation.replace('# ', ' ')
    recommendation = recommendation.replace(' #', ' ')
    recommendation = recommendation.replace('#', '')
    
    return recommendation

def main():
    """Main function to analyze an image and provide product recommendations."""
    # Handle command-line arguments
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use default test image
        image_path = "test_image.jpg"
        if not os.path.exists(image_path):
            logger.error(f"No image specified and default {image_path} not found.")
            print(f"Usage: python {os.path.basename(__file__)} [path_to_image]")
            return 1
    
    print("\n" + "="*80)
    print(" Pocket AI - PRODUCT IMAGE ANALYZER ".center(80, "="))
    print("="*80 + "\n")
    
    # Step 1: Analyze the image
    print("📸 ANALYZING IMAGE...\n")
    image_description = analyze_image(image_path)
    
    if not image_description:
        logger.error("Failed to analyze image.")
        print("❌ Error: Could not analyze the image. Please try with a different image.")
        return 1
    
    print("✅ IMAGE ANALYSIS COMPLETE\n")
    print("📝 IMAGE DESCRIPTION:")
    print("-" * 80)
    print(image_description)
    print("-" * 80 + "\n")
    
    # Step 2: Generate product recommendations
    print("🔍 FINDING MATCHING PRODUCTS...\n")
    recommendations = get_product_recommendations(image_description)
    
    if not recommendations:
        logger.error("Failed to generate product recommendations.")
        print("❌ Error: Could not generate product recommendations.")
        return 1
    
    print("✅ PRODUCT MATCHES FOUND\n")
    print("🛍️ RECOMMENDED PRODUCTS:")
    print("-" * 80)
    print(recommendations)
    print("-" * 80 + "\n")
    
    print("=" * 80)
    print(" ANALYSIS COMPLETE ".center(80, "="))
    print("=" * 80 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
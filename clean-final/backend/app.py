"""
Main application for the Pocket AI e-commerce agent.
This module defines the FastAPI routes and application.
"""

import os
import logging
import re
import traceback
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import uvicorn
import sys

# Add parent directory to path to import product_matcher
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from product_matcher import analyze_image, get_product_recommendations
except ImportError as e:
    logging.error(f"Failed to import product_matcher: {e}")
    # Define fallback functions
    async def analyze_image(image_path):
        return "I can see a product image, but I'm unable to analyze it in detail at the moment."
        
    async def get_product_recommendations(image_description):
        return "Based on what I can see, I would recommend checking our electronics or clothing categories."

# Import our custom modules
from products import products, get_product_by_id, get_product_summary, get_random_products
from session import get_session, add_message_to_session, get_session_messages
from ai_utils import (
    RecommendationGenerator, 
    ImageAnalyzer, 
    ChatAssistant
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="Pocket AI E-commerce Agent")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)


# Define request models
class ChatRequest(BaseModel):
    sessionId: Optional[str] = None
    message: str


class RecommendRequest(BaseModel):
    sessionId: Optional[str] = None
    query: str


# Define response models
class ChatResponse(BaseModel):
    sessionId: str
    reply: str


class RecommendResponse(BaseModel):
    sessionId: str
    recommendationText: str
    products: List[Dict[str, Any]]
    error: Optional[str] = None


class ImageSearchResponse(BaseModel):
    sessionId: str
    imageDescription: str
    matchExplanation: str
    products: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    timestamp: str


# Helper function to cleanup uploaded files
def remove_file(file_path: str):
    """Remove an uploaded file after processing."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.error(f"Error removing file {file_path}: {str(e)}")


# Helper function to extract product IDs from AI recommendation text
def extract_product_ids_from_recommendation(recommendation_text: str) -> List[int]:
    """
    Extract product IDs from recommendation text.
    
    Args:
        recommendation_text: The AI-generated recommendation text
        
    Returns:
        A list of product IDs mentioned in the text
    """
    mentioned_ids = []
    valid_product_ids = [p["id"] for p in products]
    
    # Pattern 1: "Product ID: X" format
    id_pattern = re.compile(r"product\s+id:\s*(\d+)", re.IGNORECASE)
    for match in id_pattern.finditer(recommendation_text):
        try:
            product_id = int(match.group(1))
            if product_id in valid_product_ids and product_id not in mentioned_ids:
                mentioned_ids.append(product_id)
        except (ValueError, IndexError):
            continue
    
    # If we don't have 3 products yet, try extracting from exact product names
    if len(mentioned_ids) < 3:
        for product in products:
            if product["id"] in mentioned_ids:
                continue
                
            # Check for exact product name matches
            if product["name"] in recommendation_text:
                mentioned_ids.append(product["id"])
                if len(mentioned_ids) >= 3:
                    break
    
    # If we still don't have at least one product, return random products
    if not mentioned_ids:
        logger.warning("No product IDs found in recommendation, using random products")
        mentioned_ids = get_random_products(3)
    
    # Verify all IDs actually exist in the catalog
    verified_ids = [pid for pid in mentioned_ids if pid in valid_product_ids]
    
    # Log any discrepancies
    if len(verified_ids) < len(mentioned_ids):
        logger.warning(f"Removed {len(mentioned_ids) - len(verified_ids)} invalid product IDs from recommendations")
    
    return verified_ids[:3]  # Limit to 3 products


# API Routes
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API is running."""
    from datetime import datetime
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for general conversation with the AI assistant."""
    try:
        # Get or create session
        session_id, session = get_session(request.sessionId)
        
        # Add user message to history
        add_message_to_session(session_id, "user", request.message)
        
        # Get messages for context
        messages = get_session_messages(session_id)
        
        # Get AI response
        bot_reply = await ChatAssistant.get_chat_response(messages)
        
        # Add bot response to history
        add_message_to_session(session_id, "assistant", bot_reply)
        
        return {
            "sessionId": session_id,
            "reply": bot_reply
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        logger.error(traceback.format_exc())
        # Return a friendly error message
        return {
            "sessionId": request.sessionId or "error-session",
            "reply": "I'm sorry, I'm having trouble responding right now. Please try again in a moment."
        }


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """Product recommendation endpoint based on text queries."""
    try:
        logger.info(f"\n=== PRODUCT RECOMMENDATION REQUEST ===")
        logger.info(f"Query: {request.query}")
        
        # Get or create session
        session_id, _ = get_session(request.sessionId)
        
        # Get product summary for the AI prompt
        product_summary = get_product_summary()
        
        # Get AI recommendations
        logger.info("Calling Ollama API for recommendations...")
        recommendation_text = await RecommendationGenerator.get_product_recommendations(
            request.query, product_summary
        )
        logger.info("Received recommendation text from Ollama")
        
        # Log the recommendation text for debugging
        logger.info("\nAI RECOMMENDATION TEXT:")
        logger.info("------------------------")
        logger.info(recommendation_text)
        logger.info("------------------------\n")
        
        # Extract product IDs from the recommendation
        mentioned_ids = extract_product_ids_from_recommendation(recommendation_text)
        logger.info(f"Extracted product IDs: {mentioned_ids}")
        
        # Get the full product details for recommended items
        recommended_products = [get_product_by_id(product_id) for product_id in mentioned_ids 
                                if get_product_by_id(product_id) is not None]
        
        # Extract relevance scores from recommendation text
        relevance_scores = {}
        score_pattern = re.compile(r"Relevance Score:\s*(\d+)/100.*?Product ID:\s*(\d+)", re.DOTALL)
        for match in score_pattern.finditer(recommendation_text):
            score = int(match.group(1))
            product_id = int(match.group(2))
            relevance_scores[product_id] = score
            
        # Filter products by relevance score (minimum 70)
        min_relevance_score = 70
        filtered_products = []
        for product in recommended_products:
            product_id = product['id']
            if product_id in relevance_scores:
                score = relevance_scores[product_id]
                logger.info(f"Product {product['name']} (ID: {product_id}) has relevance score: {score}")
                if score >= min_relevance_score:
                    filtered_products.append(product)
                else:
                    logger.info(f"Filtering out product {product['name']} due to low relevance score: {score}")
            else:
                # If no score found, include the product (backward compatibility)
                filtered_products.append(product)
                
        recommended_products = filtered_products
        
        logger.info(f"Found {len(recommended_products)} relevant products: {[p['name'] for p in recommended_products]}")
        
        # If no products found, return error message
        if not recommended_products:
            logger.warning("No highly relevant product matches found!")
            return {
                "sessionId": session_id,
                "recommendationText": recommendation_text,
                "products": [],
                "error": "No highly relevant product matches found for your query. Please try a different search term."
            }
        
        logger.info(f"Sending response with {len(recommended_products)} products")
        logger.info("=== END OF REQUEST ===\n")
        
        return {
            "sessionId": session_id,
            "recommendationText": recommendation_text,
            "products": recommended_products
        }
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation service error: {str(e)}")


@app.post("/api/image-search", response_model=ImageSearchResponse)
async def image_search(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    sessionId: Optional[str] = Form(None)
):
    """Image search endpoint to find products based on uploaded images."""
    logger.info(f"=== IMAGE SEARCH REQUEST ===")
    logger.info(f"Received image: {image.filename}")
    
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file uploaded")
        
        # Get or create session
        session_id, _ = get_session(sessionId)
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create a unique filename to avoid conflicts
        from datetime import datetime
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_ext = os.path.splitext(image.filename)[1]
        safe_filename = f"{timestamp}_{unique_id}{file_ext}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Save the uploaded file
        logger.info(f"Saving image to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Schedule file cleanup
        background_tasks.add_task(remove_file, file_path)
        
        # Try to use vision model for image analysis
        use_vision_model = True
        try:
            # Analyze the image
            logger.info("Analyzing image with Ollama vision model...")
            image_description = await ImageAnalyzer.analyze_product_image(file_path)
            logger.info("Image analysis successful")
        except Exception as e:
            logger.warning(f"Vision model error: {str(e)}")
            use_vision_model = False
            image_description = "Image analysis is currently limited. We've selected some products based on popular categories."
        
        # Get product summary for the AI prompt
        product_summary = get_product_summary()
        
        # Create prompt for matching products based on image description
        if use_vision_model:
            logger.info("Using vision model results for product matching")
            match_prompt = [
                {
                    "role": "system",
                    "content": "You are Pocket AI, a product matching specialist for an e-commerce platform. Your task is to find products in our catalog that match what's shown in a user's image."
                },
                {
                    "role": "user",
                    "content": f"""Based on this description of an image: "{image_description}"

Here are the available products in our catalog:
{product_summary}

Find exactly 3 products from our catalog that best match what's shown in the image. For each product:
1. Clearly state the product ID number (e.g., "Product ID: 7")
2. Explain specifically why this product matches the image
3. Highlight the features that are similar to what's in the image

Format your response to clearly highlight the product IDs so they can be easily extracted. Be accurate and precise in your matching."""
                }
            ]
        else:
            # Fallback when vision model isn't available
            logger.info("Using fallback for product recommendations (vision model failed)")
            match_prompt = [
                {
                    "role": "system",
                    "content": "You are Pocket AI, a product recommendation specialist for an e-commerce platform."
                },
                {
                    "role": "user",
                    "content": f"""A user has uploaded an image, but we can't analyze it directly. Let's recommend some diverse products that might be useful.

Here are the available products in our catalog:
{product_summary}

Please recommend 3 diverse products from different categories that a typical shopper might be interested in. For each product:
1. Clearly state the product ID number (e.g., "Product ID: 7")
2. Explain why this product would appeal to shoppers
3. Mention its key features and benefits

Format your response to clearly highlight the product IDs so they can be easily extracted."""
                }
            ]
        
        # Get AI-generated product matches
        logger.info("Getting product matches from Ollama...")
        match_explanation = await ChatAssistant.get_chat_response(match_prompt)
        
        # Extract product IDs from the match explanation
        mentioned_ids = extract_product_ids_from_recommendation(match_explanation)
        logger.info(f"Extracted product IDs: {mentioned_ids}")
        
        # Get the full product details for matched items
        matched_products = [get_product_by_id(product_id) for product_id in mentioned_ids 
                           if get_product_by_id(product_id) is not None]
        
        # If no products found, use random products
        if not matched_products:
            logger.warning("No products matched, using random products instead")
            matched_products = get_random_products(3)
        
        logger.info(f"Returning {len(matched_products)} products")
        logger.info("=== END OF IMAGE SEARCH REQUEST ===")
        
        return {
            "sessionId": session_id,
            "imageDescription": image_description,
            "matchExplanation": match_explanation,
            "products": matched_products
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image search error: {str(e)}")


@app.post("/api/product-match", response_model=ImageSearchResponse)
async def product_match(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    sessionId: Optional[str] = Form(None)
):
    """Product matcher endpoint using the dedicated product_matcher.py functionality."""
    logger.info(f"=== PRODUCT MATCHER REQUEST ===")
    logger.info(f"Received image: {image.filename}")
    
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file uploaded")
        
        # Get or create session
        session_id, _ = get_session(sessionId)
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create a unique filename to avoid conflicts
        from datetime import datetime
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_ext = os.path.splitext(image.filename)[1]
        safe_filename = f"{timestamp}_{unique_id}{file_ext}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Save the uploaded file
        logger.info(f"Saving image to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Schedule file cleanup
        background_tasks.add_task(remove_file, file_path)
        
        try:
            # Use product_matcher.py to analyze the image
            logger.info("Analyzing image with product_matcher...")
            image_description = analyze_image(file_path)
            
            if not image_description:
                logger.warning("Product matcher image analysis returned None, using fallback")
                image_description = "Image analysis is currently limited. We've selected a product based on popular categories."
            else:
                logger.info("Image analysis successful")
                logger.info(f"Image description: {image_description[:100]}...")
                
            # Use product_matcher.py to get product recommendations
            logger.info("Getting best product match from product_matcher...")
            match_explanation = get_product_recommendations(image_description)
            
            if not match_explanation:
                logger.warning("Product matching returned None, using fallback")
                match_explanation = "We couldn't find a specific product match. Here's a popular item you might be interested in."
                matched_products = [get_random_products(1)[0]]
            else:
                logger.info(f"Match explanation received: {len(match_explanation)} chars")
                
                # Extract product IDs from the match explanation
                mentioned_ids = extract_product_ids_from_recommendation(match_explanation)
                logger.info(f"Extracted product IDs: {mentioned_ids}")
                
                # Get the full product details for matched items
                if mentioned_ids:
                    # Get the first matched product
                    matched_product = get_product_by_id(mentioned_ids[0])
                    matched_products = [matched_product] if matched_product else []
                else:
                    matched_products = []
                
                # If no product found, use a random product
                if not matched_products:
                    logger.warning("No product matched, using random product instead")
                    matched_products = [get_random_products(1)[0]]
        except Exception as analysis_error:
            # Fallback to using the built-in image analysis if product_matcher fails
            logger.error(f"Error using product_matcher: {str(analysis_error)}")
            logger.info("Falling back to built-in image analysis...")
            
            # Use the built-in image analyzer instead
            image_description = await ImageAnalyzer.analyze_product_image(file_path)
            
            # Get product summary for the AI prompt
            product_summary = get_product_summary()
            
            # Create prompt for matching products based on image description
            match_prompt = [
                {
                    "role": "system",
                    "content": "You are Pocket AI, a product matching specialist for an e-commerce platform. Your task is to find the best product in our catalog that matches what's shown in a user's image."
                },
                {
                    "role": "user",
                    "content": f"""Based on this description of an image: "{image_description}"

Here are the available products in our catalog:
{product_summary}

Find the single best product from our catalog that matches what's shown in the image:
1. Clearly state the product ID number (e.g., "Product ID: 7")
2. Explain specifically why this product matches the image
3. Highlight the features that are similar to what's in the image

Format your response to clearly highlight the product ID so it can be easily extracted. Be accurate and precise in your matching."""
                }
            ]
            
            # Get AI-generated product match
            match_explanation = await ChatAssistant.get_chat_response(match_prompt)
            
            # Extract product IDs from the match explanation
            mentioned_ids = extract_product_ids_from_recommendation(match_explanation)
            
            # Get the full product details for matched item
            if mentioned_ids:
                matched_product = get_product_by_id(mentioned_ids[0])
                matched_products = [matched_product] if matched_product else []
            else:
                matched_products = []
            
            # If no product found, use a random product
            if not matched_products:
                matched_products = [get_random_products(1)[0]]
        
        logger.info(f"Returning {len(matched_products)} product")
        logger.info("=== END OF PRODUCT MATCHER REQUEST ===")
        
        return {
            "sessionId": session_id,
            "imageDescription": image_description,
            "matchExplanation": match_explanation,
            "products": matched_products
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product matcher error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Product matcher error: {str(e)}")


if __name__ == "__main__":
    # Run the server
    port = int(os.environ.get("PORT", 4000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 
"""
Frontend application for the Pocket AI e-commerce agent.
This module provides a web UI using FastAPI and Jinja2 templates.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="Pocket AI Frontend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the current directory
current_dir = Path(__file__).parent
static_dir = current_dir / "static"
templates_dir = current_dir / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:4000/api")

# API client
client = httpx.AsyncClient(timeout=30.0)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request}
    )


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: Optional[str] = None):
    """Render the chat page."""
    return templates.TemplateResponse(
        "chat.html", 
        {"request": request, "session_id": session_id or ""}
    )


@app.post("/send-message")
async def send_message(request: Request, session_id: str = Form(""), message: str = Form(...)):
    """Send a message to the AI assistant and get a response."""
    try:
        response = await client.post(
            f"{BACKEND_API_URL}/chat",
            json={"sessionId": session_id if session_id else None, "message": message}
        )
        
        if response.status_code != 200:
            return {"success": False, "error": f"API Error: {response.status_code}"}
            
        result = response.json()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/recommend", response_class=HTMLResponse)
async def recommend_page(request: Request, session_id: Optional[str] = None):
    """Render the product recommendation page."""
    return templates.TemplateResponse(
        "recommend.html", 
        {"request": request, "session_id": session_id or ""}
    )


@app.post("/get-recommendations")
async def get_recommendations(request: Request, session_id: str = Form(""), query: str = Form(...)):
    """Get product recommendations based on a query."""
    try:
        response = await client.post(
            f"{BACKEND_API_URL}/recommend",
            json={"sessionId": session_id if session_id else None, "query": query}
        )
        
        if response.status_code != 200:
            return {"success": False, "error": f"API Error: {response.status_code}"}
            
        result = response.json()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/product-matcher", response_class=HTMLResponse)
async def product_matcher_page(request: Request, session_id: Optional[str] = None):
    """Render the product matcher page."""
    return templates.TemplateResponse(
        "product_matcher.html", 
        {"request": request, "session_id": session_id or ""}
    )


@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """Render the products catalog page."""
    try:
        # Import the products module from backend
        sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        import sys
        sys.path.append(sys_path)
        from backend.products import products
        
        # Organize products by category
        products_by_category = {}
        for product in products:
            category = product["category"]
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product)
        
        # Sort categories alphabetically
        sorted_categories = sorted(products_by_category.keys())
        
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "products_by_category": products_by_category,
                "categories": sorted_categories
            }
        )
    except Exception as e:
        logger.error(f"Products page error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return HTMLResponse(
            content=f"<h1>Error loading products</h1><p>{str(e)}</p>",
            status_code=500
        )


@app.post("/match-product")
async def match_product(
    request: Request, 
    image: UploadFile = File(...),
    session_id: str = Form("")
):
    """Upload an image and get product matches using the product_matcher functionality."""
    try:
        # Check file type
        content_type = image.content_type
        if not content_type or not content_type.startswith('image/'):
            return {"success": False, "error": "Please upload a valid image file."}
        
        # Check file size (limit to 5MB)
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        file_contents = b''
        
        # Read file in chunks to check size and store content
        while chunk := await image.read(chunk_size):
            file_size += len(chunk)
            file_contents += chunk
            if file_size > 5 * 1024 * 1024:  # 5MB limit
                return {"success": False, "error": "Image file is too large (max 5MB)."}
        
        # Reset file position
        await image.seek(0)
        
        # Prepare the form data
        form_data = {"sessionId": session_id if session_id else None}
        files = {"image": (image.filename, file_contents, image.content_type)}
        
        # Send request to backend
        logger.info(f"Sending image to backend for product matching: {image.filename}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{BACKEND_API_URL}/product-match",
                    data=form_data,
                    files=files
                )
                
                if response.status_code != 200:
                    error_detail = "Unknown error"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_detail = error_data["detail"]
                    except:
                        pass
                    logger.error(f"Backend API error: {response.status_code} - {error_detail}")
                    return {"success": False, "error": f"API Error ({response.status_code}): {error_detail}"}
                    
                result = response.json()
                logger.info(f"Received product match results with {len(result.get('products', []))} products")
                return {"success": True, "data": result}
            except httpx.TimeoutException:
                logger.error("Request to backend timed out")
                return {"success": False, "error": "The request timed out. Image analysis may take longer than expected."}
    except Exception as e:
        logger.error(f"Product matcher error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": f"Error processing image: {str(e)}"}


if __name__ == "__main__":
    # Run the server
    port = int(os.environ.get("FRONTEND_PORT", 3000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 
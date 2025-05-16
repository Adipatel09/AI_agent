"""
AI utilities for the Pocket AI e-commerce agent.
This module handles interactions with the Ollama API.
"""

import os
import requests
import subprocess
import logging
import shlex
import json
import base64
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ollama API configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")


async def call_ollama(messages: List[Dict[str, str]], model: str = OLLAMA_MODEL) -> str:
    """
    Call the Ollama API for text completion.
    
    Args:
        messages: A list of message objects in the format [{"role": "user", "content": "Hello"}]
        model: The Ollama model to use (default: llama3.2)
        
    Returns:
        The generated text response from the model
    """
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get response from Ollama: {response.status_code}")
            
        result = response.json()
        return result["message"]["content"]
    except Exception as e:
        logger.error(f"Ollama API error: {str(e)}")
        # Fallback to basic generate API if chat API fails
        try:
            # Get the last user message
            last_user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    last_user_message = message["content"]
                    break
            
            if last_user_message:
                response = requests.post(
                    f"{OLLAMA_API_URL}/generate",
                    json={
                        "model": model,
                        "prompt": last_user_message,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "I'm sorry, I couldn't process your request at the moment.")
        except Exception as e2:
            logger.error(f"Fallback API error: {str(e2)}")
            
        return "I'm sorry, I'm having trouble connecting to my AI services right now. Please try again later."


async def analyze_image_with_ollama(image_path: str, prompt: str) -> str:
    """
    Analyze an image using Ollama's vision model.
    
    Args:
        image_path: Path to the image file
        prompt: The text prompt to guide the image analysis
        
    Returns:
        The text analysis of the image
    """
    # Try three different methods to analyze the image, falling back if previous ones fail
    
    # Method 1: Use subprocess to call Ollama CLI directly
    try:
        # Properly escape the command arguments for security
        model = OLLAMA_VISION_MODEL
        escaped_prompt = shlex.quote(prompt)
        escaped_path = shlex.quote(image_path)
        
        command = f'ollama run {model} -i {escaped_path} {escaped_prompt}'
        logger.info(f"Executing method 1: {command}")
        
        # Run the command and capture output
        result = subprocess.check_output(
            command, 
            shell=True, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=30  # Add timeout to prevent hanging
        )
        
        return result.strip()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Method 1 failed with error: {e.output}")
        # Fall back to method 2
    except subprocess.TimeoutExpired:
        logger.warning("Method 1 timed out")
        # Fall back to method 2
    except Exception as e:
        logger.warning(f"Method 1 failed with error: {str(e)}")
        # Fall back to method 2
    
    # Method 2: Try calling ollama CLI with arguments as list (no shell)
    try:
        logger.info("Trying method 2: subprocess with args list")
        result = subprocess.check_output(
            ["ollama", "run", OLLAMA_VISION_MODEL, "-i", image_path, prompt],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=30
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Method 2 failed with error: {e.output}")
        # Fall back to method 3
    except subprocess.TimeoutExpired:
        logger.warning("Method 2 timed out")
        # Fall back to method 3
    except Exception as e:
        logger.warning(f"Method 2 failed with error: {str(e)}")
        # Fall back to method 3
    
    # Method 3: Use Ollama's API directly with an image
    try:
        logger.info("Trying method 3: Ollama REST API with base64 image")
        
        # Read the image file and encode it as base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Prepare the API request
        response = requests.post(
            f"{OLLAMA_API_URL}/generate",
            json={
                "model": OLLAMA_VISION_MODEL,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Method 3 API error: {response.status_code} - {response.text}")
            raise Exception(f"Failed with status code: {response.status_code}")
        
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        logger.error(f"All methods failed. Final error: {str(e)}")
        return "I'm unable to analyze this image at the moment. Please try again later or use a different image."


class RecommendationGenerator:
    """Class to generate product recommendations using the Ollama AI model."""
    
    @staticmethod
    async def get_product_recommendations(query: str, product_summary: str) -> str:
        """
        Generate product recommendations based on a user query.
        
        Args:
            query: User's product query
            product_summary: Summary of available products
            
        Returns:
            AI-generated product recommendations
        """
        # Create recommendation prompt
        recommendation_prompt = [
            {
                "role": "system", 
                "content": """You are Pocket AI, a product recommendation specialist for an e-commerce platform. Your task is to accurately match user requests to relevant products from our catalog and provide detailed, persuasive recommendations.

CRITICAL RULES:
1. You MUST ONLY recommend products that are in our catalog
2. You MUST use the EXACT product names from the catalog WITHOUT ANY CHANGES
3. DO NOT invent products or modify product names in any way
4. DO NOT paraphrase or abbreviate product names
5. When listing a product name, it must match the catalog EXACTLY character-for-character
6. NEVER suggest products that aren't in the catalog, even as alternatives
7. ONLY recommend products that are HIGHLY RELEVANT to the user's query - do not suggest loosely related products
8. If you can't find at least 2 highly relevant products, it's better to recommend just 1 perfect match than multiple mediocre matches
9. NEVER use phrases like "I couldn't find a product named X" - only recommend actual products
10. For each product, assign a relevance score from 1-100 based on how well it matches the query (include this in your reasoning)"""
            },
            {
                "role": "user",
                "content": f"""I'm looking for: "{query}".

Here is our EXACT product catalog with IDs, names, and details:
{product_summary}

Based on my request, recommend ONLY products that are HIGHLY RELEVANT to what I'm looking for. ONLY recommend products that EXACTLY match names in the catalog above.

For each recommendation, structure your response like this:

## [EXACT PRODUCT NAME] ($PRICE)

### Perfect Match Because:
- [Relevance Score: X/100] - Explain why you assigned this score
- [First reason this product matches my query]
- [Second reason this product matches my query]
- [Third reason this product matches my query]

Product ID: [PRODUCT_ID]"""
            }
        ]
        
        try:
            response = await call_ollama(recommendation_prompt)
            
            # Verify that the response contains at least one product ID
            if "Product ID:" not in response:
                logger.warning("Recommendation doesn't contain product IDs. Adding fallback message.")
                response += "\n\nI've highlighted the Product IDs above so you can easily reference these items."
                
            return response
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            # Return a fallback response
            return """I'm sorry, but I couldn't generate product recommendations at this time. Here are some popular products from our catalog instead:

## Wireless Bluetooth Headphones ($89.99)
- Quality sound with noise cancellation
- Long battery life
- Comfortable fit for all-day wear
Product ID: 1

## Smart Home Assistant ($149.99)
- Voice-controlled smart home hub
- Plays music, answers questions, controls smart devices
- Compact design fits anywhere
Product ID: 5"""


class ImageAnalyzer:
    """Class to analyze product images using Ollama's vision model."""
    
    @staticmethod
    async def analyze_product_image(image_path: str) -> str:
        """
        Analyze a product image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detailed description of the product in the image
        """
        # Create analysis prompt
        analysis_prompt = """Analyze this product image in detail and provide a comprehensive description of:
1) What type of product or item is shown
2) What category it belongs to (clothing, electronics, accessories, books, etc.)
3) Its apparent color(s), material(s), and texture(s)
4) Any distinctive features, patterns, or design elements
5) What the product might be used for
6) Any visible brand identifiers or logos
7) The apparent size, shape, and form factor

Be specific and detailed in your analysis. Focus only on what you can actually see in the image."""
        
        try:
            # Call image analysis function
            description = await analyze_image_with_ollama(image_path, analysis_prompt)
            
            # Check if the result is empty or contains error messages
            if not description or "cannot analyze" in description.lower() or "cannot see" in description.lower():
                logger.warning("Image analysis failed or returned unusable result")
                return "I see a product image, but can't analyze the details completely. It appears to be a consumer product that might be in categories like electronics, clothing, or home goods."
                
            return description
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return "I see a product image, but I'm having trouble analyzing it in detail right now. It appears to be a consumer product, though I can't identify specific features."


class ChatAssistant:
    """Class to handle chat interactions."""
    
    @staticmethod
    async def get_chat_response(messages: List[Dict[str, str]]) -> str:
        """
        Generate a chat response based on conversation history.
        
        Args:
            messages: List of chat messages with roles and content
            
        Returns:
            AI-generated response to the user's message
        """
        # Add system prompt to messages
        system_message = {
            "role": "system",
            "content": """You are Pocket AI, a helpful and friendly e-commerce shopping assistant. You help users find products, answer questions about products, and provide information about shopping on our platform.

Important guidelines:
1. Be friendly, conversational, and helpful
2. If users ask for product recommendations, encourage them to use the dedicated recommendation feature
3. If users mention images or ask about product images, inform them about the image search feature
4. Keep responses concise and to-the-point
5. Focus on helping the user accomplish their shopping goals
6. If a user's message is unclear, politely ask for clarification
7. You are an e-commerce assistant for Pocket AI, a fictional company that sells various products"""
        }
        
        # Insert system message at the beginning
        full_messages = [system_message] + messages
        
        try:
            response = await call_ollama(full_messages)
            
            # Basic sanity check
            if not response or len(response) < 10:
                logger.warning("Chat response was too short or empty, using fallback")
                return "I'm here to help with your shopping needs! How can I assist you today?"
                
            return response
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my services right now. Please try again in a moment!" 
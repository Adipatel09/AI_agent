# Pocket AI: E-Commerce Agent

An AI-powered shopping assistant that helps users find products through natural language conversation, text-based recommendations, and image-based product search.

## Table of Contents
- [Pocket AI: E-Commerce Agent](#pocket-ai-e-commerce-agent)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
    - [Key Components](#key-components)
    - [Data Flow](#data-flow)
  - [Features](#features)
    - [General Conversation](#general-conversation)
    - [Text-Based Product Recommendation](#text-based-product-recommendation)
    - [Image-Based Product Search](#image-based-product-search)
  - [Product Recommendation System](#product-recommendation-system)
    - [Recommendation Architecture](#recommendation-architecture)
    - [Scoring Algorithm](#scoring-algorithm)
    - [Category Detection](#category-detection)
    - [Match Explanation Generation](#match-explanation-generation)
  - [Technical Decisions](#technical-decisions)
    - [Language and Framework Selection](#language-and-framework-selection)
    - [AI Model Selection](#ai-model-selection)
    - [Deployment Architecture](#deployment-architecture)
    - [Error Handling and Resilience](#error-handling-and-resilience)
  - [Installation \& Setup](#installation--setup)
    - [Prerequisites](#prerequisites)
    - [Setup Steps](#setup-steps)
    - [Running the Application](#running-the-application)
  - [Usage](#usage)
    - [Example Interactions](#example-interactions)
  - [API Documentation](#api-documentation)
    - [Key Endpoints](#key-endpoints)
  - [Future Improvements](#future-improvements)

## Overview

Pocket AI is an AI-powered shopping assistant inspired by Amazon's Rufus. It's designed to help users discover products through natural language interactions, make personalized recommendations based on textual descriptions, and identify products from images. The application combines modern AI capabilities with a user-friendly interface to create a seamless shopping experience.

## Architecture

The system follows a client-server architecture with clear separation of concerns:

```
┌────────────────┐     ┌────────────────┐     ┌─────────────────┐
│    Frontend    │◄───►│    Backend     │◄───►│   AI Services   │
│ (User Interface)│     │ (API Server)   │     │  (Ollama Models) │
└────────────────┘     └────────────────┘     └─────────────────┘
```

### Key Components

1. **Frontend**:
   - Web interface built with HTML, CSS, JavaScript, and Jinja2 templates
   - Responsive design for desktop and mobile devices
   - Form handling for text input and image uploads

2. **Backend**:
   - FastAPI server for REST API endpoints
   - Product database (in-memory with JSON)
   - Request processing and response formatting

3. **AI Services**:
   - Local Ollama models for inference:
     - LLaMA 3.2 for text-based interactions
     - LLaVA for image analysis
   - Custom matching algorithms for product recommendations

4. **Utilities**:
   - Startup scripts for environment configuration
   - Error handling and logging
   - Image processing utilities

### Data Flow

The system processes user interactions in the following sequence:

1. **User Input**: 
   - Text query via chat interface
   - Image upload via file selector

2. **API Processing**:
   - Frontend sends request to appropriate endpoint (`/api/chat`, `/api/recommend`, `/api/image-search`)
   - Backend validates and preprocesses input
   - For image uploads, files are saved temporarily in the `uploads` directory

3. **AI Analysis**:
   - Chat messages routed to LLaMA 3.2 via the ChatAssistant class
   - Images processed by LLaVA through multiple fallback methods:
     - Ollama CLI with direct image flag
     - Ollama API with base64 encoding
     - Backend integration with ImageAnalyzer
     - Generic fallback for error cases
   - Structured output extracted from AI responses

4. **Product Matching**:
   - Processed data matched against product catalog using custom scoring algorithm
   - Categories detected from keywords in the query or image description
   - Products ranked by relevance score
   - Best match selected (for image search) or top matches (for text recommendations)

5. **Response Generation**:
   - Detailed explanation of why products match the query
   - Results formatted with product details including ID, price, features, etc.
   - Response returned to frontend via JSON

6. **Display**:
   - Frontend renders recommendations in a user-friendly format
   - Interactive elements allow further exploration of products

## Features

### General Conversation

The agent can engage in natural, contextual conversations with users about products, shopping preferences, and general inquiries.

**Technical Implementation:**
- Uses LLaMA 3.2 model via Ollama for natural language processing
- Implements context management to maintain conversation history
- Customized prompt engineering to ensure helpful, relevant responses
- Fallback mechanisms for handling ambiguous queries

**Design Decisions:**
- Chose local Ollama models over cloud APIs for privacy and reduced latency
- Implemented a throttling mechanism to prevent API overload
- Structured prompts to guide the AI toward commerce-specific responses
- Added guardrails to prevent hallucinations and inappropriate content

### Text-Based Product Recommendation

Users can describe what they're looking for, and the agent recommends relevant products from the catalog.

**Technical Implementation:**
- Text embedding and semantic search for product matching
- Custom scoring algorithm that considers:
  - Category relevance
  - Keyword matching
  - Feature alignment
  - Brand recognition
- Multi-step recommendation pipeline:
  1. Natural language understanding of user request
  2. Feature extraction from request
  3. Product database search and ranking
  4. Response generation with rationale

**Design Decisions:**
- Developed a custom scoring system rather than using pure vector search for better explainability
- Weighted category and specific feature matches higher than general term matches
- Added randomization factor to avoid recommending the same products repeatedly
- Implemented detailed explanation generation to help users understand why products were recommended

### Image-Based Product Search

Users can upload images of products, and the agent identifies them and finds similar items in the catalog.

**Technical Implementation:**
- Uses LLaVA vision model for image analysis
- Multi-stage processing pipeline:
  1. Image analysis to extract detailed description
  2. Feature extraction from description
  3. Category detection and classification
  4. Product matching based on extracted features
- Multiple fallback methods for image processing:
  - Ollama CLI approach (primary)
  - Ollama API with base64 encoding (secondary)
  - Backend integration (tertiary)
  - Generic fallback (if all else fails)

**Design Decisions:**
- Chose LLaVA for its strong performance in detailed visual analysis
- Implemented multiple analysis methods to ensure reliable performance across environments
- Added detailed logging for troubleshooting
- Optimized image handling to work with various formats and sizes
- Created comprehensive product attribute extraction for better matching

## Product Recommendation System

### Recommendation Architecture

The recommendation system follows a hybrid approach that combines several techniques:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input    │────►│  AI Processing  │────►│ Feature Extraction │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         │                                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Presentation   │◄────│  Explanation    │◄────│  Product Matching │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Input Analysis**:
   - For text queries, LLaMA 3.2 extracts key features (product type, attributes, use case)
   - For images, LLaVA generates detailed descriptions covering visual aspects

2. **Category Identification**:
   - Input processed through keyword matching against predefined category keywords
   - Multiple categories can be identified in a single query
   - Categories weighted by relevance and specificity

3. **Product Database Interaction**:
   - In-memory JSON product database with structured attributes
   - Products organized by category, type, and features
   - Each product includes detailed metadata (price, colors, tags, etc.)

4. **Enhanced Product Attributes**:
   - Dynamic attribute extraction from product data
   - Features derived from product tags and type
   - Color information extracted from name and tags
   - Use cases inferred from category and type

### Scoring Algorithm

The scoring algorithm ranks products based on relevance to the user's query. Key aspects of the scoring system:

- **Weighted Attributes**: Different match types have different score weights
- **Hierarchical Scoring**: Category matches are weighted higher than specific attributes
- **Contextual Boosts**: Special handling for specific categories like books
- **Semantic Matching**: Partial word matching for broader coverage
- **Brand Recognition**: Higher weights for brand-name matches

### Category Detection

The system uses a keyword-based approach to detect product categories, exactly as implemented in the codebase:

```python
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
```

Benefits of this approach:
- **Transparency**: Clear mapping between keywords and categories
- **Extensibility**: Easy to add new categories or keywords
- **Efficiency**: Fast computation without complex embeddings
- **Robustness**: Works well even with limited training data

### Match Explanation Generation

After finding matching products, the system generates natural language explanations for why each product matches the user's query:

1. **Identify Match Points**:
   ```python
   # Find matching elements between product and description
   matches = []
   
   # Check category match
   if product_category.lower() in description_lower:
       matches.append(f"Category match: {product_category}")
   elif product_category in key_categories:
       matches.append(f"Category match: {product_category} (detected from keywords)")
   ```

2. **Context-Specific Explanations**:
   ```python
   # Create a contextual explanation based on the product and image description
   if "book" in description_lower and product_category == "books":
       if "collection" in product["name"].lower() or "set" in product["name"].lower():
           recommendation += "The image shows a stack of books, and this product is a collection of books..."
       else:
           recommendation += f"The image shows books, and this {product['type']} book would be a valuable addition..."
   ```

3. **Match Highlights**:
   ```python
   # Add matching elements or a generic explanation if no specific matches
   if matches:
       for match in matches:
           recommendation += f"- {match}\n"
   else:
       recommendation += f"- It belongs to the {product_category} category which could fit the item shown\n"
       recommendation += f"- It has features like {', '.join(features[:2])}\n"
       recommendation += f"- It's available in colors including {', '.join(colors)}\n"
   ```

4. **Formatting**:
   ```python
   # Create a detailed recommendation
   recommendation = f"""## Best Match: {product['name']} (${product['price']:.2f})

   Product ID: {product['id']}

   ### Why This Product Matches:
   This {product_category.capitalize()} product aligns with the image description because:
   """
   ```

## Technical Decisions

### Language 

- **Python**: Chosen for its extensive AI/ML libraries, readability, and rapid development capabilities

### AI Model Selection

- **LLaMA 3.2**: Selected for general text processing due to:
  - Strong reasoning capabilities
  - Good context handling
  - Efficient performance on local hardware
  - Open-source nature

- **LLaVA**: Chosen for image analysis because:
  - Specifically designed for vision-language tasks
  - Efficient local inference
  - Good performance on product recognition
  - Ability to generate detailed descriptions

### Deployment Architecture

- **Local-first approach**: All AI inference runs locally using Ollama
  - Advantages: Privacy, no usage costs, works offline
  - Disadvantages: Requires more powerful hardware, longer startup time

- **Modular design**: Components are loosely coupled for easier maintenance and updates

### Error Handling and Resilience

- Extensive error handling with appropriate user feedback
- Multiple fallback approaches for critical functionality
- Comprehensive logging system for debugging
- Graceful degradation when optimal services unavailable

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/download) for local AI models
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Adipatel09/AI_agent.git
   cd clean-final
   ```

2. **Create and activate a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Ollama is installed and running**
   - Download Ollama from [ollama.ai/download](https://ollama.ai/download)
   - Start Ollama service

5. **Install required models**
   ```bash
   ollama pull llama3.2
   ollama pull llava
   ```

### Running the Application

**Quick Start:**
```bash
./clean_start.sh
```

**Manual Start:**
```bash
python start.py
```

The application will:
1. Check if Ollama is running and required models are available
2. Start the backend server (default port: 4000)
3. Start the frontend server (default port: 3000)
4. Provide URLs to access the application

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Use the chat interface to:
   - Ask general questions
   - Request product recommendations by describing what you want
   - Upload an image to find matching products

### Example Interactions

- **General conversation:** "What kind of products do you offer?"
- **Text-based recommendation:** "I need a comfortable t-shirt for jogging"
- **Image-based search:** Upload an image of a smartphone to find similar products

## API Documentation

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send a message to the AI assistant |
| `/api/recommend` | POST | Get product recommendations based on text |
| `/api/image-search` | POST | Upload an image for product matching |
| `/api/products` | GET | Get the complete product catalog |
| `/api/product/{id}` | GET | Get details for a specific product |
| `/api/health` | GET | Check if the API is running |

For detailed API documentation, visit `http://localhost:4000/docs` when the server is running.

## Future Improvements

- **Enhanced Product Catalog**: Expand with more detailed product information
- **Multi-modal Queries**: Allow text and image in the same query
- **User Profiles**: Personalized recommendations based on user history
- **Performance Optimization**: Caching and query optimization
- **Mobile App**: Native mobile applications for iOS and Android
- **Multi-language Support**: Extend capabilities to multiple languages 
#!/usr/bin/env python3
"""
Startup script for the Pocket AI E-commerce Agent.
This script checks if Ollama is installed and running,
then starts the FastAPI backend server and frontend.
"""

import os
import sys
import subprocess
import time
import requests
import logging
import signal
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("startup")

# Configuration
OLLAMA_PORT = 11434
API_PORT = 4000
FRONTEND_PORT = 3000
REQUIRED_MODELS = ["llama3.2", "llava"]
PROCESSES = []

def check_command_exists(command):
    """Check if a command exists on the system."""
    try:
        subprocess.run(
            ["which", command], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_ollama_running():
    """Check if Ollama is running."""
    try:
        response = requests.get(f"http://localhost:{OLLAMA_PORT}/api/tags")
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_model_exists(model):
    """Check if a model exists in Ollama."""
    try:
        response = requests.get(f"http://localhost:{OLLAMA_PORT}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(m.get("name") == model for m in models)
        return False
    except requests.RequestException:
        return False

def verify_llava_works():
    """Specifically verify that the llava model can process images."""
    try:
        logger.info("Performing detailed check of llava model...")
        
        # First check if the model exists
        if not check_model_exists("llava"):
            logger.warning("llava model not found")
            return False
            
        # Create a simple test prompt
        test_prompt = "What is this?"
        
        # Try using the API with a small base64 encoded test image
        # This is a 1x1 pixel transparent PNG
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        
        try:
            response = requests.post(
                f"http://localhost:{OLLAMA_PORT}/api/generate",
                json={
                    "model": "llava",
                    "prompt": test_prompt,
                    "images": [test_image],
                    "stream": False
                },
                timeout=15
            )
            
            if response.status_code != 200:
                logger.warning(f"llava model API test failed with status code {response.status_code}")
                return False
                
            # Check if we got a reasonable response
            result = response.json()
            if not result.get("response"):
                logger.warning("llava model didn't return a response")
                return False
                
            logger.info("llava model can process images")
            return True
        except Exception as e:
            logger.warning(f"llava model API test failed: {str(e)}")
            return False
    except Exception as e:
        logger.warning(f"llava verification failed: {str(e)}")
        return False

def verify_model_works(model):
    """Verify that a model works by running a simple prompt."""
    try:
        logger.info(f"Verifying model {model}...")
        
        if model == "llava":
            # For llava, we need a more thorough check
            return verify_llava_works()
        else:
            # For text models, we can just run a simple prompt
            response = requests.post(
                f"http://localhost:{OLLAMA_PORT}/api/generate",
                json={
                    "model": model,
                    "prompt": "Say hello",
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Model {model} verification failed with status code {response.status_code}")
                return False
                
            logger.info(f"Model {model} verification successful")
            return True
    except Exception as e:
        logger.warning(f"Model {model} verification failed: {str(e)}")
        return False

def pull_model(model):
    """Pull a model using Ollama."""
    logger.info(f"Pulling model {model}...")
    try:
        subprocess.run(
            ["ollama", "pull", model],
            check=True
        )
        
        # Verify the model works after pulling
        if verify_model_works(model):
            logger.info(f"Model {model} pulled and verified successfully")
            return True
        else:
            logger.warning(f"Model {model} was pulled but verification failed")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to pull model {model}: {e}")
        return False

def check_port_available(port):
    """Check if a port is available."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("localhost", port))
        s.close()
        return True
    except socket.error:
        return False

def find_available_port(start_port, max_tries=10):
    """Find an available port starting from start_port."""
    for port_offset in range(max_tries):
        port = start_port + port_offset
        if check_port_available(port):
            return port
    return None

def start_backend():
    """Start the FastAPI backend."""
    logger.info("Starting FastAPI backend...")
    
    # Find an available port
    port = find_available_port(API_PORT)
    if not port:
        logger.error(f"Could not find an available port for the backend (tried {API_PORT}-{API_PORT+9})")
        return False
    
    if port != API_PORT:
        logger.warning(f"Port {API_PORT} is in use, using port {port} instead")
    
    # Start the backend in a subprocess
    backend_path = Path(__file__).parent / "backend"
    backend_process = subprocess.Popen(
        ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
        cwd=backend_path,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    PROCESSES.append(backend_process)
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Check if server is running
    try:
        response = requests.get(f"http://localhost:{port}/api/health")
        if response.status_code == 200:
            logger.info(f"Backend started successfully on port {port}")
            # Set environment variable for frontend to use
            os.environ["BACKEND_API_URL"] = f"http://localhost:{port}/api"
            return True
        else:
            logger.warning(f"Backend may not have started correctly. Status code: {response.status_code}")
            return False
    except requests.RequestException:
        logger.warning("Could not connect to backend. It may not have started correctly.")
        return False

def start_frontend():
    """Start the Frontend server."""
    logger.info("Starting frontend server...")
    
    # Find an available port
    port = find_available_port(FRONTEND_PORT)
    if not port:
        logger.error(f"Could not find an available port for the frontend (tried {FRONTEND_PORT}-{FRONTEND_PORT+9})")
        return False
    
    if port != FRONTEND_PORT:
        logger.warning(f"Port {FRONTEND_PORT} is in use, using port {port} instead")
    
    # Set environment variable for the frontend port
    os.environ["FRONTEND_PORT"] = str(port)
    
    # Start the frontend in a subprocess
    frontend_path = Path(__file__).parent / "frontend"
    frontend_process = subprocess.Popen(
        ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
        cwd=frontend_path,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    PROCESSES.append(frontend_process)
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Check if server is running
    try:
        response = requests.get(f"http://localhost:{port}/")
        if response.status_code == 200:
            logger.info(f"Frontend started successfully on port {port}")
            return True
        else:
            logger.warning(f"Frontend may not have started correctly. Status code: {response.status_code}")
            return False
    except requests.RequestException:
        logger.warning("Could not connect to frontend. It may not have started correctly.")
        return False

def cleanup(signum=None, frame=None):
    """Clean up processes on exit."""
    logger.info("Shutting down...")
    
    for process in PROCESSES:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
    
    logger.info("All processes terminated")
    sys.exit(0)

def main():
    """Main entry point for the startup script."""
    logger.info("Starting Pocket AI E-commerce Agent...")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Check if Ollama is installed
    if not check_command_exists("ollama"):
        logger.error("Ollama is not installed. Please install it first: https://ollama.ai/download")
        return False
    
    # Check if Ollama is running
    if not check_ollama_running():
        logger.warning("Ollama is not running. Attempting to start it...")
        try:
            ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            PROCESSES.append(ollama_process)
            
            # Give Ollama some time to start
            time.sleep(5)
            
            if not check_ollama_running():
                logger.error("Failed to start Ollama. Please start it manually.")
                return False
        except Exception as e:
            logger.error(f"Error starting Ollama: {e}")
            return False
    
    # Check and pull required models
    all_models_ready = True
    for model in REQUIRED_MODELS:
        if not check_model_exists(model):
            logger.info(f"Model {model} not found. Downloading...")
            if not pull_model(model):
                logger.warning(f"Failed to download {model}. Some features may not work correctly.")
                all_models_ready = False
        else:
            # Verify the model works even if it exists
            logger.info(f"Model {model} exists. Verifying...")
            if not verify_model_works(model):
                logger.warning(f"Model {model} verification failed. Attempting to re-pull...")
                if not pull_model(model):
                    logger.warning(f"Failed to re-pull {model}. Some features may not work correctly.")
                    all_models_ready = False
    
    if not all_models_ready:
        logger.warning("Some models are not working correctly. Certain features may be limited.")
        
        # If llava is not working, warn specifically about image features
        if "llava" in REQUIRED_MODELS and not verify_model_works("llava"):
            logger.warning("The llava model is not working correctly. Image analysis features will be limited.")
    
    # Start the backend server
    if not start_backend():
        logger.error("Failed to start backend server")
        return False
    
    # Start the frontend server
    if not start_frontend():
        logger.error("Failed to start frontend server")
        return False
    
    # Get the frontend port from environment
    frontend_port = os.environ.get("FRONTEND_PORT", FRONTEND_PORT)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Pocket AI E-commerce Agent is now running!")
    logger.info(f"- Frontend: http://localhost:{frontend_port}")
    logger.info(f"- Backend API: {os.environ.get('BACKEND_API_URL', f'http://localhost:{API_PORT}/api')}")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop all servers.")
    
    try:
        # Keep the script running to maintain the subprocesses
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
    
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1) 
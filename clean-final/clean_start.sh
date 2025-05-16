#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print header
echo -e "\n${BOLD}${PURPLE}=======================================${NC}"
echo -e "${BOLD}${PURPLE}     POCKET AI E-COMMERCE AGENT     ${NC}"
echo -e "${BOLD}${PURPLE}=======================================${NC}\n"

# Check if script is run with sudo (which we don't want)
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please don't run this script with sudo or as root.${NC}"
    exit 1
fi

# Function to kill process using a specific port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Killing process $pid using port $port...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
    else
        echo -e "${YELLOW}No process found using port $port${NC}"
    fi
}

# Debug function to echo messages with a timestamp
debug() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${BLUE}DEBUG: $1${NC}"
}

# Check for port conflicts and clean up if needed
echo -e "${BLUE}Checking for port conflicts...${NC}"
kill_port 3000  # Frontend
kill_port 4000  # Backend
echo -e "${GREEN}Port check complete.${NC}"

# Check for Ollama installation
echo -e "\n${BLUE}Checking Ollama installation...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Ollama is not installed.${NC}"
    echo -e "${YELLOW}Please install Ollama from https://ollama.ai/download${NC}"
    echo -e "${YELLOW}After installing Ollama, run this script again.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Ollama is installed.${NC}"
fi

# Check if Ollama is running
echo -e "\n${BLUE}Checking if Ollama service is running...${NC}"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${YELLOW}Ollama service is not running. Attempting to start it...${NC}"
    
    # Different start methods based on platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open -a Ollama
    else
        # Linux and others
        ollama serve &
    fi
    
    echo -e "${YELLOW}Waiting for Ollama to start...${NC}"
    # Wait for up to 20 seconds for Ollama to start
    for i in {1..20}; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            echo -e "${GREEN}✓ Ollama service started successfully.${NC}"
            break
        fi
        sleep 1
        echo -n "."
        if [ $i -eq 20 ]; then
            echo -e "\n${RED}Failed to start Ollama service.${NC}"
            echo -e "${YELLOW}Please start Ollama manually and run this script again.${NC}"
            exit 1
        fi
    done
else
    echo -e "${GREEN}✓ Ollama service is already running.${NC}"
fi

# Check for required models
check_model() {
    local model=$1
    echo -e "\n${BLUE}Checking for $model model...${NC}"
    if curl -s http://localhost:11434/api/tags | grep -q "\"$model\""; then
        echo -e "${GREEN}✓ $model model is already downloaded.${NC}"
        return 0
    else
        echo -e "${YELLOW}$model model is not found. Pulling now...${NC}"
        ollama pull $model
        
        # Verify pull was successful
        if curl -s http://localhost:11434/api/tags | grep -q "\"$model\""; then
            echo -e "${GREEN}✓ $model model downloaded successfully.${NC}"
            return 0
        else
            echo -e "${RED}Failed to download $model model.${NC}"
            return 1
        fi
    fi
}

# Check required models
check_model "llama3.2" || echo -e "${YELLOW}Warning: llama3.2 model not available. Chat functionality may be limited.${NC}"
check_model "llava" || echo -e "${RED}Warning: llava model not available. Image analysis will not work!${NC}"

# Find the Python command
echo -e "\n${BLUE}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check Python version for compatibility
    PY_VERSION=$(python --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo $PY_VERSION | cut -d. -f1)
    MINOR=$(echo $PY_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python 3.8 or higher is required.${NC}"
        echo -e "${YELLOW}Found Python $PY_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo -e "${YELLOW}Please install Python 3.8 or higher: https://www.python.org/downloads/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Using $PYTHON_CMD ($(${PYTHON_CMD} --version 2>&1))${NC}"

# Navigate to the script directory
cd "$(dirname "$0")"
debug "Current directory: $(pwd)"

# Set up virtual environment
echo -e "\n${BLUE}Setting up virtual environment...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating new virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        echo -e "${YELLOW}Trying to continue without virtual environment...${NC}"
        VENV_ACTIVE=false
    else
        VENV_ACTIVE=true
    fi
else
    echo -e "${GREEN}✓ Using existing virtual environment.${NC}"
    VENV_ACTIVE=true
fi

# Activate virtual environment if it exists
if [ "$VENV_ACTIVE" = true ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to activate virtual environment.${NC}"
        echo -e "${YELLOW}Trying to continue without virtual environment...${NC}"
        VENV_ACTIVE=false
    else
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    fi
fi

# Install dependencies
echo -e "\n${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Standard installation failed. Trying simplified installation...${NC}"
    
    # Try installing without version constraints
    pip install fastapi uvicorn python-multipart requests python-dotenv jinja2 httpx
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies.${NC}"
        echo -e "${YELLOW}Please try installing them manually:${NC}"
        echo -e "${YELLOW}pip install -r requirements.txt${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Dependencies installed successfully.${NC}"

# Show starting information
echo -e "\n${PURPLE}${BOLD}=======================================${NC}"
echo -e "${GREEN}${BOLD}STARTING POCKET AI E-COMMERCE AGENT${NC}"
echo -e "${PURPLE}${BOLD}=======================================${NC}\n"

echo -e "${BLUE}The application will start with:${NC}"
echo -e "${YELLOW}• Backend API: http://localhost:4000/api${NC}"
echo -e "${YELLOW}• Frontend:    http://localhost:3000${NC}"
echo -e "${YELLOW}• Ollama API:  http://localhost:11434/api${NC}\n"

echo -e "${BLUE}Press Ctrl+C to stop the application at any time.${NC}\n"

# Check if we're in the right directory
debug "Looking for start files in: $(pwd)"
debug "Available files: $(ls -la | grep -E 'start.py|run.py')"

# Start the application
if [ -f "start.py" ]; then
    debug "Found start.py, using it to start the application"
    $PYTHON_CMD start.py
elif [ -f "run.py" ]; then
    debug "Found run.py, using it to start the application"
    $PYTHON_CMD run.py
else
    echo -e "${RED}Error: Could not find start.py or run.py in $(pwd).${NC}"
    exit 1
fi

# If the script exits, show a completion message
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Application exited successfully.${NC}"
else
    echo -e "\n${RED}The application exited with an error.${NC}"
    exit 1
fi

# Deactivate virtual environment if it was activated
if [ "$VENV_ACTIVE" = true ]; then
    deactivate
fi 
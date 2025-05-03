#!/bin/bash
# TaskWeaver Deployment and Launch Script

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}TaskWeaver Deployment and Launch Script${NC}"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip is not installed. Please install pip and try again.${NC}"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git and try again.${NC}"
    exit 1
fi

# Pull the latest changes
echo -e "${YELLOW}Pulling the latest changes from the repository...${NC}"
git pull

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating a virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate the virtual environment
echo -e "${YELLOW}Activating the virtual environment...${NC}"
source venv/bin/activate

# Install or upgrade dependencies
echo -e "${YELLOW}Installing or upgrading dependencies...${NC}"
pip install -e ".[dev]"

# Check if the installation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies. Please check the error message above.${NC}"
    exit 1
fi

# Set up environment variables
echo -e "${YELLOW}Setting up environment variables...${NC}"

# Check if .env file exists
if [ -f ".env" ]; then
    echo -e "${GREEN}Found .env file. Loading environment variables...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}No .env file found. Creating a new one...${NC}"
    
    # Prompt for API keys
    read -p "Enter your OpenAI API key (leave blank to skip): " OPENAI_API_KEY
    read -p "Enter your Codegen API key (leave blank to skip): " CODEGEN_API_KEY
    read -p "Enter your Codegen organization ID (leave blank to skip): " CODEGEN_ORG_ID
    read -p "Enter your GitHub token (leave blank to skip): " GITHUB_TOKEN
    read -p "Enter your ngrok token (leave blank to skip): " NGROK_TOKEN
    
    # Create .env file
    echo "# TaskWeaver Environment Variables" > .env
    [ ! -z "$OPENAI_API_KEY" ] && echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env
    [ ! -z "$CODEGEN_API_KEY" ] && echo "CODEGEN_API_KEY=$CODEGEN_API_KEY" >> .env
    [ ! -z "$CODEGEN_ORG_ID" ] && echo "CODEGEN_ORG_ID=$CODEGEN_ORG_ID" >> .env
    [ ! -z "$GITHUB_TOKEN" ] && echo "GITHUB_TOKEN=$GITHUB_TOKEN" >> .env
    [ ! -z "$NGROK_TOKEN" ] && echo "NGROK_TOKEN=$NGROK_TOKEN" >> .env
    
    # Export environment variables
    [ ! -z "$OPENAI_API_KEY" ] && export OPENAI_API_KEY
    [ ! -z "$CODEGEN_API_KEY" ] && export CODEGEN_API_KEY
    [ ! -z "$CODEGEN_ORG_ID" ] && export CODEGEN_ORG_ID
    [ ! -z "$GITHUB_TOKEN" ] && export GITHUB_TOKEN
    [ ! -z "$NGROK_TOKEN" ] && export NGROK_TOKEN
fi

# Launch TaskWeaver
echo -e "${GREEN}Launching TaskWeaver...${NC}"
echo "========================================"

# Prompt for launch mode
echo "Select a launch mode:"
echo "1. Web UI (default)"
echo "2. Desktop GUI"
echo "3. CLI"
read -p "Enter your choice (1-3): " LAUNCH_MODE

# Set default port
PORT=8000

# Prompt for port
read -p "Enter port number (default: 8000): " PORT_INPUT
if [ ! -z "$PORT_INPUT" ]; then
    PORT=$PORT_INPUT
fi

# Launch based on selected mode
case $LAUNCH_MODE in
    2)
        echo -e "${GREEN}Launching Desktop GUI...${NC}"
        python main.py --gui
        ;;
    3)
        echo -e "${GREEN}Launching CLI...${NC}"
        read -p "Enter project directory: " PROJECT_DIR
        if [ -z "$PROJECT_DIR" ]; then
            echo -e "${RED}Error: Project directory is required for CLI mode.${NC}"
            exit 1
        fi
        python main.py --cli --project "$PROJECT_DIR" --interactive
        ;;
    *)
        echo -e "${GREEN}Launching Web UI on port $PORT...${NC}"
        python main.py --web --port $PORT
        ;;
esac

# Deactivate the virtual environment when done
deactivate


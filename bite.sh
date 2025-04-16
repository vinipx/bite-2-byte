#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print a header
print_header() {
    echo -e "${BLUE}==============================================${NC}"
    echo -e "${BLUE} Bite-2-Byte: Web Scraper for AI Training Data ${NC}"
    echo -e "${BLUE}==============================================${NC}"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header

# Check if Python is installed
if ! command -v python &> /dev/null; then
    print_error "Python is not installed. Please install Python first."
    exit 1
fi

# Detect OS
OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == "Darwin" ]]; then
    echo "macOS detected. Using pip for installation."
    # macOS installation using pip
    pip install -r requirements.txt
elif [[ "$OS_TYPE" == "MINGW"* ]] || [[ "$OS_TYPE" == "MSYS"* ]] || [[ "$OS_TYPE" == "CYGWIN"* ]]; then
    echo "Windows detected. Checking for pip..."
    if command -v pip &> /dev/null; then
        echo "pip found. Using pip for installation."
        pip install -r requirements.txt
    else
        echo "pip not found. Please install Python and pip, or use an alternative method like Chocolatey."
        echo "Visit https://chocolatey.org/install for Chocolatey installation instructions."
        echo "After installing Chocolatey, you can run: choco install python"
        exit 1
    fi
else
    echo "Unsupported OS detected. Please install dependencies manually."
    exit 1
fi

# Check if the main.py file exists
if [ ! -f "main.py" ]; then
    print_error "main.py not found. Please ensure you're in the correct directory."
    exit 1
fi

# Ask for URL if not provided as an argument
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Enter the base URL to start crawling from:${NC}"
    read -p "(e.g., https://example.com): " url
else
    url="$1"
fi

# Ask for data format
echo -e "${YELLOW}Select a data format for AI training:${NC}"
echo -e "  ${BLUE}1.${NC} JSONL (default)"
echo -e "  ${BLUE}2.${NC} CSV"
echo -e "  ${BLUE}3.${NC} TXT"
read -p "Enter choice (1-3, press Enter for default): " format_choice

case $format_choice in
    2)
        format="csv"
        ;;
    3)
        format="txt"
        ;;
    *)
        format="jsonl"
        ;;
esac

# Run the application
echo -e "${YELLOW}Starting the web scraper...${NC}"
print_warning "URL: $url"
print_warning "Data will be saved in $format format"
python main.py --url "$url" --format "$format"

if [ $? -eq 0 ]; then
    echo -e "${BLUE}==============================================${NC}"
    print_success "Web scraping completed successfully!"
    print_success "Check 'training_data.$format' for the extracted Q&A data."
else
    echo -e "${BLUE}==============================================${NC}"
    print_error "An error occurred during web scraping."
    print_error "Please check the output above for details."
fi

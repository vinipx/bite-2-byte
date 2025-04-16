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
    echo -e "${BLUE} Web Scraper for AI Training Data ${NC}"
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

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    print_error "pip is not installed. Please install pip to manage Python packages."
    exit 1
fi

# Check for required Python libraries
print_warning "Checking for required Python libraries..."
required_libs=("requests" "beautifulsoup4")
missing_libs=()
for lib in "${required_libs[@]}"; do
    if ! pip show "$lib" &> /dev/null; then
        missing_libs+=("$lib")
    fi
done

if [ ${#missing_libs[@]} -ne 0 ]; then
    print_error "Missing required libraries: ${missing_libs[*]}"
    print_warning "Attempting to install missing libraries..."
    for lib in "${missing_libs[@]}"; do
        pip install "$lib"
        if [ $? -eq 0 ]; then
            print_success "Installed $lib successfully."
        else
            print_error "Failed to install $lib. Please install it manually."
            exit 1
        fi
    done
fi
print_success "All required libraries are installed."

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

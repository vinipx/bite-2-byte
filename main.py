import argparse
import sys
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from collections import deque
import re


def is_valid_url(url):
    """ Check if the URL is valid. """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_user_input():
    """ Get base URL and preferred data format from user. """
    parser = argparse.ArgumentParser(description='Web scraper for Q&A and knowledge base data extraction for AI training.')
    parser.add_argument('--url', type=str, help='Base URL to start crawling from')
    parser.add_argument('--format', type=str, choices=['jsonl', 'csv', 'txt'], default='jsonl',
                        help='Preferred data format for model training (default: jsonl)')
    args = parser.parse_args()
    
    if not args.url:
        args.url = input("Please enter the base URL to start crawling from: ")
    return args.url, args.format

def crawl_website(base_url):
    """ Crawl the website starting from the base URL and return a list of URLs to scrape. """
    urls_to_visit = deque([base_url])
    visited_urls = set()
    links = []

    while urls_to_visit:
        url = urls_to_visit.popleft()
        if url in visited_urls:
            continue

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                visited_urls.add(url)
                links.append(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                for anchor in soup.find_all('a'):
                    href = anchor.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if is_valid_url(full_url) and urlparse(full_url).netloc == urlparse(base_url).netloc:
                            if full_url not in visited_urls:
                                urls_to_visit.append(full_url)
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")

        if len(links) >= 100:  # Limit to 100 pages for now
            break

    return links

def extract_qa_content(urls):
    """ Extract Questions and Answers content from the list of URLs. """
    qa_data = []
    question_pattern = re.compile(r'(what|how|why|when|where|who|is|are|do|does|can|could|should|would)\b', re.IGNORECASE)
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])
                current_question = None
                for element in text_elements:
                    text = element.get_text().strip()
                    if question_pattern.search(text) and text.endswith('?'):
                        current_question = text
                    elif current_question and len(text) > 20:  # Assuming answer is longer than 20 chars
                        qa_data.append({'question': current_question, 'answer': text, 'source': url})
                        current_question = None
        except requests.RequestException as e:
            print(f"Error processing {url}: {e}")
    return qa_data

def format_data(qa_data, output_format):
    """ Format the extracted data into the specified format for AI training. """
    if output_format == 'jsonl':
        with open('training_data.jsonl', 'w') as f:
            for item in qa_data:
                json.dump(item, f)
                f.write('\n')
    elif output_format == 'csv':
        import csv
        with open('training_data.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['question', 'answer', 'source'])
            writer.writeheader()
            for item in qa_data:
                writer.writerow(item)
    elif output_format == 'txt':
        with open('training_data.txt', 'w', encoding='utf-8') as f:
            for item in qa_data:
                f.write(f"Q: {item['question']}\nA: {item['answer']}\nSource: {item['source']}\n\n")

def validate_data_for_llm(qa_data):
    """ Validate if the extracted data is suitable for LLM training. """
    if not qa_data:
        return False, "No data extracted for training."

    suitable_count = 0
    issues = []
    for i, item in enumerate(qa_data):
        question = item.get('question', '')
        answer = item.get('answer', '')
        
        if len(question) < 10:
            issues.append(f"Item {i+1}: Question too short - {question}")
        elif len(answer) < 20:
            issues.append(f"Item {i+1}: Answer too short - {answer}")
        elif not question.endswith('?'):
            issues.append(f"Item {i+1}: Question does not end with a question mark - {question}")
        else:
            suitable_count += 1

    suitability_ratio = suitable_count / len(qa_data) if qa_data else 0
    if suitability_ratio < 0.7:
        return False, f"Only {suitability_ratio*100:.1f}% of data is suitable for training. Issues: {'; '.join(issues[:5])}"
    return True, f"{suitability_ratio*100:.1f}% of data is suitable for LLM training."

def main():
    base_url, data_format = get_user_input()
    if not is_valid_url(base_url):
        print("Invalid URL provided. Please ensure it includes the scheme (http:// or https://) and a valid domain.")
        sys.exit(1)

    print(f"Starting crawl from {base_url}")
    urls = crawl_website(base_url)
    print(f"Found {len(urls)} pages to scrape.")
    qa_data = extract_qa_content(urls)
    print(f"Extracted {len(qa_data)} Q&A pairs.")
    
    is_suitable, validation_message = validate_data_for_llm(qa_data)
    print("Validation Result:", validation_message)
    if not is_suitable:
        print("Warning: The extracted data may not be suitable for LLM training. Consider refining the source or extraction criteria.")
    
    format_data(qa_data, data_format)
    print(f"Data has been formatted and saved as 'training_data.{data_format}'")

if __name__ == "__main__":
    main()

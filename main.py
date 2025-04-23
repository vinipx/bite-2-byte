import argparse
import html
import json
import re
from collections import deque
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import requests
from bs4 import BeautifulSoup


def clean_text(text):
    """ Clean text by removing HTML tags, handling newlines and Unicode symbols. """
    if not text:
        return ""

    # Remove HTML tags if any are left
    text = re.sub(r'<[^>]+>', ' ', text)

    # Replace newlines, tabs, and multiple spaces with a single space
    text = re.sub(r'[\n\t\r]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize Unicode characters
    text = text.strip()

    return text


def is_valid_url(url):
    """ Check if the URL is valid. """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_user_input():
    """ Get base URL and preferred data format from user. """
    parser = argparse.ArgumentParser(
        description='Web scraper for Q&A and knowledge base data extraction for AI training.')
    parser.add_argument('--url', type=str, help='Base URL to start crawling from')
    parser.add_argument('--format', type=str, choices=['jsonl', 'csv', 'txt'], default='jsonl',
                        help='Preferred data format for model training (default: jsonl)')
    parser.add_argument('--max-pages', type=int, default=None,
                        help='Maximum number of pages to crawl (optional, will auto-detect if not specified)')
    args = parser.parse_args()

    if not args.url:
        args.url = input("Please enter the base URL to start crawling from: ")
    return args.url, args.format, args.max_pages


def discover_all_pages(base_url, max_discovery=200):
    """
    Discover all available pages by following pagination links.
    Returns a list of all discovered page URLs.
    """
    print("Starting page discovery process...")
    
    urls_to_visit = deque([base_url])
    visited_urls = set()
    discovered_pages = []
    visited_count = 0
    
    # Common pagination URL patterns
    pagination_patterns = [
        # Format: page=X
        r'[?&]page=(\d+)',
        # Format: /page/X/
        r'/page/(\d+)/',
        # Format: p=X
        r'[?&]p=(\d+)',
        # Format: /X/ at the end of URL
        r'/(\d+)/?$'
    ]

    while urls_to_visit and visited_count < max_discovery:
        url = urls_to_visit.popleft()
        if url in visited_urls:
            continue

        visited_count += 1
        if visited_count % 10 == 0:
            print(f"Discovering pages: {visited_count} URLs checked, {len(discovered_pages)} pages found")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                visited_urls.add(url)
                
                # Check if this is a content page (not just navigation)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Add to discovered pages if it has content
                main_content = soup.select_one('main, article, .content, .post, .thread, .topic')
                if main_content:
                    discovered_pages.append(url)
                
                # Look for pagination links
                # Method 1: Look for "Next" or ">" links
                next_links = soup.find_all('a', string=lambda text: text and re.search(r'next|Next|>|›|»', text, re.IGNORECASE))
                for next_link in next_links:
                    href = next_link.get('href')
                    if href:
                        next_url = urljoin(base_url, href)
                        if next_url not in visited_urls and is_valid_url(next_url):
                            urls_to_visit.append(next_url)
                
                # Method 2: Look for pagination elements with page numbers
                pagination_elements = soup.select('.pagination, .pager, .pages, nav, ul.page-numbers')
                for element in pagination_elements:
                    page_links = element.find_all('a')
                    for link in page_links:
                        href = link.get('href')
                        if href:
                            page_url = urljoin(base_url, href)
                            if page_url not in visited_urls and is_valid_url(page_url):
                                urls_to_visit.append(page_url)
                
                # Method 3: Look for any links that match pagination patterns
                all_links = soup.find_all('a')
                for link in all_links:
                    href = link.get('href', '')
                    for pattern in pagination_patterns:
                        if re.search(pattern, href):
                            page_url = urljoin(base_url, href)
                            if page_url not in visited_urls and is_valid_url(page_url):
                                urls_to_visit.append(page_url)
                
        except requests.RequestException as e:
            print(f"Error accessing {url} during discovery: {e}")
    
    print(f"Page discovery complete. Found {len(discovered_pages)} content pages.")
    return discovered_pages


def crawl_website(base_url, max_pages=None):
    """ 
    Crawl the website starting from the base URL and return a list of URLs to scrape.
    Handles pagination to navigate through all available pages.
    """
    # First, discover all pages
    all_pages = discover_all_pages(base_url)
    total_pages = len(all_pages)
    
    # If max_pages is specified, limit the number of pages to crawl
    if max_pages is not None and max_pages < total_pages:
        pages_to_crawl = all_pages[:max_pages]
        print(f"Limiting crawl to {max_pages} pages out of {total_pages} discovered pages")
    else:
        pages_to_crawl = all_pages
        print(f"Will crawl all {total_pages} discovered pages")
    
    # Now process each page to extract links
    links = []
    visited_urls = set()
    
    for i, url in enumerate(pages_to_crawl):
        print(f"Crawling page {i+1}/{len(pages_to_crawl)}: {url}")
        
        try:
            if url in visited_urls:
                continue
                
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                visited_urls.add(url)
                links.append(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract additional links from the current page
                for anchor in soup.find_all('a'):
                    href = anchor.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if is_valid_url(full_url) and urlparse(full_url).netloc == urlparse(base_url).netloc:
                            if full_url not in visited_urls and full_url not in links:
                                links.append(full_url)
                
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
    
    print(f"Crawling complete. Collected {len(links)} total URLs")
    return links


def extract_qa_content(urls):
    """ Extract Questions and Answers content from the list of URLs. """
    qa_data = []
    question_pattern = re.compile(r'(what|how|why|when|where|who|is|are|do|does|can|could|should|would)\b',
                                  re.IGNORECASE)

    total_urls = len(urls)
    for i, url in enumerate(urls):
        print(f"Extracting Q&A from URL {i + 1}/{total_urls}: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for structured FAQ sections first (common in knowledge bases)
                faq_sections = soup.select('.faq, .faqs, .faq-item, .faq-section, .accordion')

                if faq_sections:
                    for section in faq_sections:
                        # Look for question/answer pairs in structured FAQs
                        questions = section.select('.question, .faq-question, h3, h4, dt')
                        answers = section.select('.answer, .faq-answer, p, dd')

                        # Match questions with their answers
                        for q, a in zip(questions, answers):
                            q_text = clean_text(q.get_text())
                            a_text = clean_text(a.get_text())

                            if q_text and a_text and len(a_text) > 20:
                                # Ensure question ends with question mark
                                if not q_text.endswith('?'):
                                    q_text += '?'

                                qa_data.append({
                                    'question': q_text,
                                    'answer': a_text,
                                    'source': url
                                })

                # If no structured FAQs found, try general text extraction
                if not faq_sections:
                    text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])
                    current_question = None
                    for element in text_elements:
                        text = clean_text(element.get_text())
                        if question_pattern.search(text) and text.endswith('?'):
                            current_question = text
                        elif current_question and len(text) > 20:  # Assuming answer is longer than 20 chars
                            qa_data.append({
                                'question': current_question,
                                'answer': text,
                                'source': url
                            })
                            current_question = None

                # Special handling for Verizon community site
                # Look for discussion threads with questions and replies
                threads = soup.select('.message-list, .thread, .topic, .discussion')
                for thread in threads:
                    # First post is often the question
                    first_post = thread.select_one('.first-post, .topic-post, .thread-question')
                    if first_post:
                        title_elem = first_post.select_one('h1, h2, h3, .post-title')
                        content_elem = first_post.select_one('.post-content, .content, .post-body')

                        if title_elem and content_elem:
                            title = clean_text(title_elem.get_text())
                            content = clean_text(content_elem.get_text())

                            # If title is a question, use it directly
                            if title.endswith('?'):
                                question = title
                            # Otherwise, try to extract a question from the content
                            else:
                                # Look for sentences ending with question marks
                                question_sentences = re.findall(r'[^.!?]*\?', content)
                                question = question_sentences[
                                    0] if question_sentences else f"What information can you provide about {title}?"

                            # Look for accepted solution or best answer
                            solution = thread.select_one('.solution, .accepted-answer, .best-answer')
                            if solution:
                                answer = clean_text(solution.get_text())
                                if len(answer) > 20:
                                    qa_data.append({
                                        'question': question,
                                        'answer': answer,
                                        'source': url
                                    })

        except requests.RequestException as e:
            print(f"Error processing {url}: {e}")

        # Save progress periodically
        if (i + 1) % 50 == 0:
            print(f"Progress update: Extracted {len(qa_data)} Q&A pairs so far from {i + 1} URLs")
            # Save intermediate results to avoid losing data if the process is interrupted
            with open('data_qa_intermediate.jsonl', 'w', encoding='utf-8') as f:
                for item in qa_data:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')

    return qa_data


def extract_discussion_content(urls):
    """ Extract discussion posts and forum content from the list of URLs. """
    discussion_data = []

    # Common selectors for forum posts and discussions
    forum_selectors = {
        'post_containers': ['div.post', 'div.thread', 'article', 'div.message', 'div.topic', 'div.forum-post',
                            '.message-list', '.discussion-thread'],
        'title_selectors': ['h1', 'h2', 'h3', '.post-title', '.thread-title', '.topic-title', '.message-subject'],
        'content_selectors': ['.post-content', '.message-body', '.post-body', '.content', '.post-text', '.message-text',
                              '.thread-body']
    }

    # Verizon community specific selectors
    verizon_selectors = {
        'thread_containers': ['.message-list', '.thread', '.topic', '.discussion-thread'],
        'post_containers': ['.message', '.post', '.reply', '.comment', '.response'],
        'title_selectors': ['.subject', '.title', 'h1', 'h2', 'h3'],
        'content_selectors': ['.content', '.body', '.text', '.message-body']
    }

    total_urls = len(urls)
    for i, url in enumerate(urls):
        print(f"Extracting discussions from URL {i + 1}/{total_urls}: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Check if this is a Verizon community page
                is_verizon = 'verizon.com' in url

                # First, try to find structured forum posts
                posts = []

                # Use appropriate selectors based on the site
                if is_verizon:
                    # For Verizon community pages
                    for selector in verizon_selectors['post_containers']:
                        posts.extend(soup.select(selector))
                else:
                    # For other sites
                    for selector in forum_selectors['post_containers']:
                        posts.extend(soup.select(selector))

                # If structured posts are found
                if posts:
                    for post in posts:
                        title = None
                        content = None

                        # Extract title
                        title_selectors = verizon_selectors['title_selectors'] if is_verizon else forum_selectors[
                            'title_selectors']
                        for title_selector in title_selectors:
                            title_element = post.select_one(title_selector)
                            if title_element:
                                title = clean_text(title_element.get_text())
                                break

                        # Extract content
                        content_selectors = verizon_selectors['content_selectors'] if is_verizon else forum_selectors[
                            'content_selectors']
                        for content_selector in content_selectors:
                            content_element = post.select_one(content_selector)
                            if content_element:
                                content = clean_text(content_element.get_text())
                                break

                        if title and content and len(content) > 20:
                            discussion_data.append({
                                'title': title,
                                'content': content,
                                'source': url
                            })

                # If no structured posts found, try to extract from general page structure
                if not posts:
                    main_title = None
                    main_content = None

                    # Try to find main title
                    for selector in ['h1', 'h2', '.entry-title', '.article-title', '.page-title']:
                        title_element = soup.select_one(selector)
                        if title_element:
                            main_title = clean_text(title_element.get_text())
                            break

                    # Try to find main content
                    for selector in ['article', '.entry-content', '.post-content', '.content', 'main', '.page-content']:
                        content_element = soup.select_one(selector)
                        if content_element:
                            main_content = clean_text(content_element.get_text())
                            break

                    if main_title and main_content and len(main_content) > 50:
                        discussion_data.append({
                            'title': main_title,
                            'content': main_content,
                            'source': url
                        })

        except requests.RequestException as e:
            print(f"Error processing {url}: {e}")

        # Save progress periodically
        if (i + 1) % 50 == 0:
            print(f"Progress update: Extracted {len(discussion_data)} discussion posts so far from {i + 1} URLs")
            # Save intermediate results to avoid losing data if the process is interrupted
            with open('data_discussion_intermediate.jsonl', 'w', encoding='utf-8') as f:
                for item in discussion_data:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')

    return discussion_data


def transform_discussions_to_qa(discussion_data):
    """ Transform discussion posts into Q&A format. """
    qa_data = []

    for item in discussion_data:
        title = item.get('title', '')
        content = item.get('content', '')
        source = item.get('source', '')

        # Skip if title or content is too short
        if len(title) < 5 or len(content) < 20:
            continue

        # Transform into question-answer format
        # If the title already ends with a question mark, use it as is
        if title.endswith('?'):
            question = title
        else:
            # Try to extract a question from the content
            question_sentences = re.findall(r'[^.!?]*\?', content)
            if question_sentences:
                question = clean_text(question_sentences[0])
            else:
                # Generate a question from the title
                question = f"What information can you provide about {title}?"

        # Use the content as the answer
        answer = content

        # For very long content, extract a summary
        if len(answer) > 1000:
            # Try to find the first few sentences that likely contain the main information
            sentences = re.split(r'(?<=[.!?])\s+', answer)
            if sentences:
                # Take first 3-5 sentences as a summary
                summary_length = min(5, len(sentences))
                answer = ' '.join(sentences[:summary_length])

        qa_data.append({
            'question': question,
            'answer': answer,
            'source': source
        })

    return qa_data


def format_data(qa_data, discussion_data, output_format):
    """ 
    Format the extracted data into the specified format for AI training.
    Saves separate files for QA data and discussion data.
    """
    # Handle duplicates by tracking unique questions for QA data
    unique_qa_items = {}
    qa_duplicates_count = 0

    for item in qa_data:
        # Use the question as the key for deduplication
        question = item.get('question', '')
        if question and question not in unique_qa_items:
            unique_qa_items[question] = item
        else:
            qa_duplicates_count += 1

    print(f"Removed {qa_duplicates_count} duplicate items from {len(qa_data)} total QA items.")
    print(f"Keeping {len(unique_qa_items)} unique QA items.")

    # Handle duplicates for discussion data (using title as key)
    unique_discussion_items = {}
    discussion_duplicates_count = 0

    for item in discussion_data:
        # Use the title as the key for deduplication
        title = item.get('title', '')
        if title and title not in unique_discussion_items:
            unique_discussion_items[title] = item
        else:
            discussion_duplicates_count += 1

    print(f"Removed {discussion_duplicates_count} duplicate items from {len(discussion_data)} total discussion items.")
    print(f"Keeping {len(unique_discussion_items)} unique discussion items.")

    # Save QA data
    if output_format == 'jsonl':
        # Save QA data
        with open('data_qa.jsonl', 'w', encoding='utf-8') as f:
            for item in unique_qa_items.values():
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')

        # Save discussion data
        with open('data_discussion.jsonl', 'w', encoding='utf-8') as f:
            for item in unique_discussion_items.values():
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')

    elif output_format == 'csv':
        import csv

        # Save QA data
        with open('data_qa.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['question', 'answer', 'source'])
            writer.writeheader()
            for item in unique_qa_items.values():
                writer.writerow(item)

        # Save discussion data
        with open('data_discussion.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'content', 'source'])
            writer.writeheader()
            for item in unique_discussion_items.values():
                writer.writerow(item)

    elif output_format == 'txt':
        # Save QA data
        with open('data_qa.txt', 'w', encoding='utf-8') as f:
            for item in unique_qa_items.values():
                f.write(f"Q: {item['question']}\nA: {item['answer']}\nSource: {item['source']}\n\n")

        # Save discussion data
        with open('data_discussion.txt', 'w', encoding='utf-8') as f:
            for item in unique_discussion_items.values():
                f.write(f"Title: {item['title']}\nContent: {item['content']}\nSource: {item['source']}\n\n")

    print(f"Data saved to data_qa.{output_format} and data_discussion.{output_format}")
    return len(unique_qa_items), len(unique_discussion_items)


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
            issues.append(f"Item {i + 1}: Question too short - {question}")
        elif len(answer) < 20:
            issues.append(f"Item {i + 1}: Answer too short - {answer}")
        elif not question.endswith('?'):
            issues.append(f"Item {i + 1}: Question does not end with a question mark - {question}")
        else:
            suitable_count += 1

    suitability_ratio = suitable_count / len(qa_data) if qa_data else 0
    if suitability_ratio < 0.7:
        return False, f"Only {suitability_ratio * 100:.1f}% of data is suitable for training. Issues: {'; '.join(issues[:5])}"
    return True, f"{suitability_ratio * 100:.1f}% of data is suitable for LLM training."


def main():
    """ Main function to run the scraper. """
    base_url, output_format, max_pages = get_user_input()
    
    print(f"Starting web crawler at {base_url}")
    if max_pages:
        print(f"Will crawl up to {max_pages} pages")
    else:
        print("Will discover and crawl all available pages")
    print("This may take some time depending on the number of pages...")
    
    # Crawl the website to get URLs
    urls = crawl_website(base_url, max_pages)
    print(f"Found {len(urls)} URLs to process")

    # Extract Q&A content
    print("Extracting Q&A content...")
    qa_data = extract_qa_content(urls)
    print(f"Extracted {len(qa_data)} Q&A pairs")

    # Extract discussion content
    print("Extracting discussion content...")
    discussion_data = extract_discussion_content(urls)
    print(f"Extracted {len(discussion_data)} discussion posts")

    # Transform discussions to Q&A format
    print("Transforming discussions to Q&A format...")
    qa_from_discussions = transform_discussions_to_qa(discussion_data)
    print(f"Transformed {len(qa_from_discussions)} discussions to Q&A format")

    # Combine all Q&A data
    all_qa_data = qa_data + qa_from_discussions
    print(f"Total Q&A pairs: {len(all_qa_data)}")

    # Format and save the data
    print(f"Formatting and saving data in {output_format} format...")
    qa_count, discussion_count = format_data(all_qa_data, discussion_data, output_format)

    # Validate the data
    print("Validating data for LLM training...")
    validation_result = validate_data_for_llm(all_qa_data)

    print("Web scraping and data extraction complete!")
    print(f"Saved {qa_count} QA items to data_qa.{output_format}")
    print(f"Saved {discussion_count} discussion items to data_discussion.{output_format}")

    return validation_result


if __name__ == "__main__":
    main()

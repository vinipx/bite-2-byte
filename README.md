# Bite-2-Byte

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B%20%7C%203.12.1-blue)](https://www.python.org/downloads/)
[![Issues](https://img.shields.io/github/issues/vinipx/bite-2-byte)](https://github.com/vinipx/bite-2-byte/issues)
[![Stars](https://img.shields.io/github/stars/vinipx/bite-2-byte)](https://github.com/vinipx/bite-2-byte/stargazers)
[![Forks](https://img.shields.io/github/forks/vinipx/bite-2-byte)](https://github.com/vinipx/bite-2-byte/network/members)

**Bite-2-Byte** is an innovative web scraping tool designed to crawl websites, extract Questions and Answers (Q&A) content, and format it into structured data suitable for AI model training, particularly for Large Language Models (LLMs). The name reflects the process of 'biting' through raw web information to convert it into 'bytes' of usable data.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Advanced Options](#advanced-options)
- [Data Validation](#data-validation)
- [Output Formats](#output-formats)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **User-Friendly Interface**: Interactive CLI for easy operation.
- **Web Crawling**: Automatically navigates through website links starting from a base URL.
- **Pagination Handling**: Intelligently discovers and navigates through paginated content.
- **Q&A Extraction**: Identifies and extracts question-answer pairs from web content.
- **Discussion Extraction**: Captures forum discussions and converts them to Q&A format.
- **Data Deduplication**: Automatically removes duplicate content to improve data quality.
- **Data Formatting**: Supports multiple output formats (JSONL, CSV, TXT) for AI training compatibility.
- **Validation**: Analyzes extracted data to ensure suitability for LLM training.
- **Progress Tracking**: Provides real-time updates and saves intermediate results during processing.
- **Dependency Management**: Automatically checks and installs required Python libraries.

## Installation

The `bite.sh` script now includes OS detection to ensure compatibility across different systems:

- **macOS**: The script uses `pip` to install required Python packages from `requirements.txt`.
- **Windows**: It checks for `pip` availability. If `pip` is not found, it provides instructions for installing Python or using Chocolatey as an alternative package manager.
- **Other OS**: For unsupported systems, the script will prompt you to install dependencies manually.

To run the installation, simply execute `./bite.sh` in your terminal. The script will handle the rest based on your operating system.

1. **Clone the Repository** (or download the zip file):
   ```bash
   git clone https://github.com/vinipx/bite-2-byte.git
   cd bite-2-byte
   ```
2. **Install Dependencies**:
   Ensure you have Python 3.6+ and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```
   Alternatively, the CLI script will attempt to install missing libraries on startup.

## Usage

Bite-2-Byte offers two ways to run the application:

1. **Interactive CLI Script** (Recommended for ease of use):
   ```bash
   ./bite.sh
   ```
   This script will guide you through providing the base URL and selecting a data format.

2. **Direct Python Execution**:
   ```bash
   python main.py --url https://example.com --format jsonl
   ```

### Example Workflow
- Run the app using `./bite.sh`.
- Enter a base URL (e.g., `https://example.com`).
- Choose a data format (JSONL, CSV, or TXT).
- The app will discover pages, crawl the site, extract Q&A and discussion data, validate it, and save the results.

## Advanced Options

Bite-2-Byte now supports additional command-line options for more control:

```bash
python main.py --url https://example.com --format jsonl --max-pages 100
```

- **--url**: The base URL to start crawling from.
- **--format**: Output format (jsonl, csv, or txt).
- **--max-pages**: Maximum number of pages to crawl (optional). If not specified, the tool will auto-detect and process all available pages.

### Handling Large Websites

For large websites with many pages, the tool now:
1. First discovers all available pages to determine the total count
2. Shows progress as it crawls through the pages
3. Saves intermediate results periodically to prevent data loss if the process is interrupted
4. Automatically handles pagination to navigate through all content pages

## Data Validation

Bite-2-Byte includes a validation step to ensure the extracted data is suitable for AI training:
- Checks for minimum length of questions (10 characters) and answers (20 characters).
- Verifies that questions end with a question mark.
- Requires at least 70% of extracted pairs to meet quality criteria.
- Provides detailed feedback if the data is deemed unsuitable.

## Output Formats

The extracted data is now saved in separate files for different content types:

### Q&A Data
- **data_qa.jsonl**: Each line is a JSON object with `question`, `answer`, and `source` fields.
- **data_qa.csv**: Structured table with columns for question, answer, and source.
- **data_qa.txt**: Human-readable format with Q&A pairs separated by new lines.

### Discussion Data
- **data_discussion.jsonl**: Each line is a JSON object with `title`, `content`, and `source` fields.
- **data_discussion.csv**: Structured table with columns for title, content, and source.
- **data_discussion.txt**: Human-readable format with discussion content.

### Intermediate Files
During processing, the tool saves intermediate results to prevent data loss:
- **data_qa_intermediate.jsonl**: Periodically saved Q&A data.
- **data_discussion_intermediate.jsonl**: Periodically saved discussion data.

## Contributing

Contributions are welcome! If you'd like to improve Bite-2-Byte, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and commit them (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Create a new Pull Request.

Please ensure your code adheres to the project's coding standards and includes appropriate documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, suggestions, or issues, please open an issue on GitHub or contact the maintainers at [vinipxf@gmail.com](mailto:vinipxf@gmail.com).

---

*Built with ❤️ for AI enthusiasts and data scientists.*

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
- [Data Validation](#data-validation)
- [Output Formats](#output-formats)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **User-Friendly Interface**: Interactive CLI for easy operation.
- **Web Crawling**: Automatically navigates through website links starting from a base URL.
- **Q&A Extraction**: Identifies and extracts question-answer pairs from web content.
- **Data Formatting**: Supports multiple output formats (JSONL, CSV, TXT) for AI training compatibility.
- **Validation**: Analyzes extracted data to ensure suitability for LLM training.
- **Dependency Management**: Automatically checks and installs required Python libraries.

## Installation

To get started with Bite-2-Byte, follow these steps:

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
- The app will crawl the site, extract Q&A data, validate it, and save the results.

## Data Validation

Bite-2-Byte includes a validation step to ensure the extracted data is suitable for AI training:
- Checks for minimum length of questions (10 characters) and answers (20 characters).
- Verifies that questions end with a question mark.
- Requires at least 70% of extracted pairs to meet quality criteria.
- Provides detailed feedback if the data is deemed unsuitable.

## Output Formats

The extracted Q&A data will be saved in the specified format as `training_data.[format]`:
- **JSONL** (default): Each line is a JSON object with `question`, `answer`, and `source` fields.
- **CSV**: Structured table with columns for `question`, `answer`, and `source`.
- **TXT**: Human-readable format with Q&A pairs separated by new lines.

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

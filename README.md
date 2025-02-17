# Segugio - The Ultimate Password Wordlist Generator

Segugio is a powerful Python tool that scrapes websites to extract keywords and generate customized password wordlists. It leverages web crawling, NLP-based keyword extraction, and common password mutation techniques to create high-quality wordlists for penetration testing and security research.

## 🚀 Features
- **Web Scraping:** Extracts text from a website and analyzes it.
- **Keyword Extraction:** Uses NLP techniques to extract important words.
- **Password Mutation:** Generates password variations based on real-world patterns.
- **Multi-threaded Crawling:** Efficiently crawls websites to discover more content.
- **Customizable Parameters:** Allows setting password length, crawl depth, and more.
- **Fake User-Agent Support:** Helps bypass simple bot detection.

## ⚠️ Disclaimer
This tool is intended for ethical hacking and security research **only**. Do **not** use it to scrape or attack websites without explicit permission. Unauthorized usage may violate legal and ethical guidelines.

## 📥 Installation
Segugio requires Python 3.6+ and several dependencies. Follow these steps to install:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/segugio.git
cd segugio
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Download NLTK Resources
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('names')
```

### 4️⃣ Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

## 🎯 Usage
Run Segugio from the command line by specifying a URL to scrape and optional parameters.

### Basic Command
```bash
python segugio.py https://example.com
```

### Advanced Usage
```bash
python segugio.py https://example.com --depth 3 --min_length 8 --max_length 16 --password_count 500 --output my_passwords.txt
```

### Parameters
| Parameter       | Description |
|----------------|-------------|
| `url`          | The URL to crawl and extract data from. |
| `--depth`      | Crawl depth (default: 2). |
| `--min_length` | Minimum password length (default: 6). |
| `--max_length` | Maximum password length (default: 12). |
| `--password_count` | Maximum number of passwords to generate. |
| `--output`     | Output filename (default: `segugio_password_wordlist.txt`). |

## 🛠️ Examples

### Generate a wordlist from a site with default settings
```bash
python segugio.py https://example.com
```

### Increase crawling depth and password complexity
```bash
python segugio.py https://example.com --depth 5 --min_length 10 --max_length 18
```

### Limit the number of generated passwords to 1000
```bash
python segugio.py https://example.com --password_count 1000
```

### Save wordlist to a custom file
```bash
python segugio.py https://example.com --output custom_wordlist.txt
```

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## 📝 Author
Created by **cometteetcaramel**. Feel free to contribute or report issues!


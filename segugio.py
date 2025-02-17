import requests
import re
import nltk
import spacy
import time
import logging
import random
import argparse
import sys
import os
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, names
from bs4 import BeautifulSoup

# Suppress NLTK downloading messages
nltk.data.path.append(r'C:\nltk_data')  # Specify a custom path if needed
def suppress_nltk_output():
    sys.stdout = open(os.devnull, 'w')  # Redirect output to null
    sys.stderr = open(os.devnull, 'w')  # Redirect errors to null
suppress_nltk_output()

# Download NLTK resources (silently)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('names', quiet=True)

# Restore standard output and error
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Global Variables
visited_urls = set()
passwordlist = set()
ua = UserAgent()
password_count_generated = 0  # Track how many passwords have been generated

# Logging setup (only log to console)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]  # Log to console only
)

# Funny ASCII Banner
def print_banner():
    banner = r"""
  ██████  ▄▄▄       ██▀███   █    ██  ██████  ██▓ ▒█████   █     █░ ▒█████  
▒██    ▒ ▒████▄    ▓██ ▒ ██▒ ██  ▓██▒██    ▒ ▓██▒▒██▒  ██▒▓█░ █ ░█░▒██▒  ██▒
░ ▓██▄   ▒██  ▀█▄  ▓██ ░▄█ ▒▓██  ▒██░ ▓██▄   ▒██▒▒██░  ██▒▒█░ █ ░█ ▒██░  ██▒
  ▒   ██▒░██▄▄▄▄██ ▒██▀▀█▄  ▓▓█  ░██░ ▒   ██▒░██░▒██   ██░░█░ █ ░█ ▒██   ██░
▒██████▒▒ ▓█   ▓██▒░██▓ ▒██▒▒▒█████▓ ▒██████▒▒░██░░ ████▓▒░░░██▒██▓ ░ ████▓▒░
▒ ▒▓▒ ▒ ░ ▒▒   ▓▒█░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ▒▓▒ ▒ ░░▓  ░ ▒░▒░▒░ ░ ▓░▒ ▒  ░ ▒░▒░▒░ 
░ ░▒  ░ ░  ▒   ▒▒ ░  ░▒ ░ ▒░░░▒░ ░ ░ ░ ░▒  ░ ░ ▒ ░  ░ ▒ ▒░   ▒ ░ ░    ░ ▒ ▒░ 
░  ░  ░    ░   ░  ░░   ░  ░░░ ░ ░ ░  ░  ░  ░   ▒ ░░ ░ ░ ░    ░   ░  ░ ░ ░ ▒  
      ░        ░  ░   ░        ░           ░   ░      ░ ░      ░        ░ ░  
    """
    print(banner)
    print("\n🐕 Welcome to **Segugio** - The Ultimate Password Wordlist Generator!\n")

# Function to clean and normalize words
def clean_word(word):
    word = word.lower().strip()
    word = re.sub(r'[^a-zA-Z0-9@#$%^&*(),.?":{}|<>]', '', word)  # Remove special characters except common password symbols
    return word if len(word) > 2 else None

# Get random headers to bypass bot detection
def get_headers():
    return {"User-Agent": ua.random}

# Scrape a website
def scrape_website(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract visible text
        text = " ".join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])])

        return text, soup
    except requests.RequestException as e:
        logging.error(f"Failed to scrape {url}: {e}")
        return "", None

# Generate password variations from a base word
def generate_password_variations(base_word, min_length, max_length):
    variations = set()

    # Simple case variations
    variations.add(base_word.capitalize())  # "Word" -> "word"
    variations.add(base_word.upper())      # "word" -> "WORD"
    
    # Adding numbers or symbols
    variations.add(base_word + "123")
    variations.add(base_word + "!")
    variations.add(base_word + "2025")
    variations.add(base_word + "@")
    
    # Common password pattern variations
    variations.add(base_word + base_word[::-1])  # "word" -> "worddrow"
    
    # Replacing characters with numbers or symbols
    variations.add(base_word.replace("a", "@"))
    variations.add(base_word.replace("s", "$"))
    variations.add(base_word.replace("i", "1"))
    
    # Remove any spaces from variations
    variations = {password.replace(" ", "") for password in variations}

    # Filter variations by length
    variations = {password for password in variations if min_length <= len(password) <= max_length}

    return variations

# Extract keywords using Named Entity Recognition (NER) and keep raw text
def extract_keywords(text):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE"]]

    # Keep raw words and add NER entities
    return set(entities)

# Get internal links
def get_internal_links(url, soup):
    base_url = f"{urlparse(url).scheme}://{urlparse(url).hostname}"
    links = [urljoin(url, link['href']) for link in soup.find_all('a', href=True)]
    return [link for link in set(links) if base_url in link and link not in visited_urls]

# Multi-threaded crawler
def crawl_and_generate_wordlist(url, depth=2, min_length=6, max_length=12, password_count=None):
    global password_count_generated
    if depth == 0 or url in visited_urls or (password_count and password_count_generated >= password_count):
        return

    visited_urls.add(url)
    logging.info(f"Scraping: {url}")  # This will be displayed in the console only

    text, soup = scrape_website(url)
    if not text or not soup:
        return

    keywords = extract_keywords(text)

    # Generate password variations from extracted keywords
    for word in keywords:
        variations = generate_password_variations(word, min_length, max_length)
        passwordlist.update(variations)
        password_count_generated = len(passwordlist)  # Update count of generated passwords

        # If the user set a limit on the number of passwords, stop once we reach that count
        if password_count and password_count_generated >= password_count:
            logging.info(f"Generated {password_count} passwords, stopping.")
            return

    internal_links = get_internal_links(url, soup)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda link: crawl_and_generate_wordlist(link, depth - 1, min_length, max_length, password_count), internal_links)

    time.sleep(random.uniform(1, 3))

# Keep generating variations until the desired count is reached
def keep_generating_until_target(target_count):
    global password_count_generated
    while password_count_generated < target_count:
        # Use the current password list to generate more variations
        all_base_words = list(passwordlist)
        random_word = random.choice(all_base_words)
        variations = generate_password_variations(random_word, 6, 12)  # Assuming 6-12 length is the desired range
        passwordlist.update(variations)
        password_count_generated = len(passwordlist)
        logging.info(f"Generated {password_count_generated} passwords...")

        if password_count_generated >= target_count:
            break

# Save wordlist
def save_wordlist(output_file):
    with open(output_file, 'w', encoding="utf-8") as f:
        for password in passwordlist:
            f.write(password + "\n")
    print(f"✅ Password wordlist saved as {output_file}")

# Command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a customized password wordlist based on a website's content.")
    parser.add_argument("url", help="The URL to crawl for generating the wordlist.")
    parser.add_argument("--depth", type=int, default=2, help="The depth to crawl (default is 2).")
    parser.add_argument("--min_length", type=int, default=6, help="Minimum length for passwords (default is 6).")
    parser.add_argument("--max_length", type=int, default=12, help="Maximum length for passwords (default is 12).")
    parser.add_argument("--output", type=str, default="segugio_password_wordlist.txt", help="Output file name (default is 'segugio_password_wordlist.txt').")
    parser.add_argument("--password_count", type=int, default=None, help="Limit the number of passwords to generate (default is None).")
    return parser.parse_args()

# Main function
def main():
    print_banner()  # Display the banner at the beginning
    args = parse_arguments()

    logging.info(f"Starting crawl for URL: {args.url} with depth {args.depth}, min length {args.min_length}, max length {args.max_length}")
    crawl_and_generate_wordlist(args.url, args.depth, args.min_length, args.max_length, args.password_count)
    
    if args.password_count and password_count_generated < args.password_count:
        logging.warning(f"Only generated {password_count_generated} passwords, generating more variations...")

    # Keep generating more variations until we reach the target password count
    if args.password_count:
        keep_generating_until_target(args.password_count)
    
    save_wordlist(args.output)

if __name__ == "__main__":
    main()

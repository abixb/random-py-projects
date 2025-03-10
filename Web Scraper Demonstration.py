# Web Scraper Demonstration
# This script scrapes book information from Open Library
# and saves the data as CSV and JSON files in the same directory

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import time
import random
from datetime import datetime

def get_user_agent():
    """Return a random user agent to avoid being blocked"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    ]
    return random.choice(user_agents)

def scrape_book_details(url):
    """Scrape information from a single book page on Open Library"""
    headers = {'User-Agent': get_user_agent()}
    
    # Add random delay between requests to be respectful to the server
    time.sleep(random.uniform(1, 2))
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract book information
        title = soup.select_one('h1.work-title').text.strip() if soup.select_one('h1.work-title') else "No title found"
        
        # Try different selectors for author
        author_elem = soup.select_one('a[href^="/author"]')
        author = author_elem.text.strip() if author_elem else "Unknown Author"
        
        # Get publication year if available
        pub_date_elem = soup.select_one('span.publish_year')
        pub_date = pub_date_elem.text.strip() if pub_date_elem else "Unknown"
        
        # Get book description
        description_elem = soup.select_one('div.book-description')
        description = description_elem.text.strip() if description_elem else "No description available"
        
        # Get subjects/categories
        subjects = [tag.text.strip() for tag in soup.select('div.subjects a.subject-tag')]
        subjects_str = ", ".join(subjects) if subjects else "No subjects listed"
        
        # Get cover image URL if available
        cover_img = soup.select_one('img.cover')
        cover_url = cover_img['src'] if cover_img and 'src' in cover_img.attrs else "No cover image"
        
        return {
            'title': title,
            'author': author,
            'publication_date': pub_date,
            'description': description[:500] + '...' if len(description) > 500 else description,
            'subjects': subjects_str,
            'cover_url': cover_url,
            'page_url': url
        }
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_book_urls(num_books=10):
    """Get URLs for popular books from Open Library"""
    base_url = "https://openlibrary.org"
    popular_url = f"{base_url}/trending/daily"
    
    headers = {'User-Agent': get_user_agent()}
    
    try:
        response = requests.get(popular_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all book links
        book_links = soup.select('a.results')
        
        # Extract URLs (up to num_books)
        book_urls = []
        for link in book_links[:num_books]:
            href = link.get('href')
            if href:
                full_url = base_url + href if href.startswith('/') else href
                book_urls.append(full_url)
        
        return book_urls
    
    except Exception as e:
        print(f"Error getting book URLs: {e}")
        return []

def main():
    """Main function to run the scraper"""
    print("Starting web scraper demonstration...")
    print("Target website: Open Library (openlibrary.org)")
    
    # Create a timestamp for the output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get list of book URLs to scrape (limiting to 10 books for demonstration)
    book_urls = get_book_urls(num_books=10)
    print(f"Found {len(book_urls)} books to scrape")
    
    # Scrape each book page
    all_books_data = []
    for i, url in enumerate(book_urls):
        print(f"Scraping book {i+1}/{len(book_urls)}: {url}")
        book_data = scrape_book_details(url)
        if book_data:
            all_books_data.append(book_data)
    
    print(f"Successfully scraped {len(all_books_data)} books")
    
    if all_books_data:
        # Save data as CSV
        csv_filename = f"openlib_books_{timestamp}.csv"
        pd.DataFrame(all_books_data).to_csv(csv_filename, index=False)
        print(f"CSV data saved to {os.path.abspath(csv_filename)}")
        
        # Save data as JSON
        json_filename = f"openlib_books_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_books_data, f, ensure_ascii=False, indent=4)
        print(f"JSON data saved to {os.path.abspath(json_filename)}")
    else:
        print("No book data was collected. Check for errors above.")
    
if __name__ == "__main__":
    main()
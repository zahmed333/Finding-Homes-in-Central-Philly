import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sqlite3
import time

class CraigslistScraper:
    def __init__(self):
        self.base_url = "https://philadelphia.craigslist.org"
        self.search_url = f"{self.base_url}/search/apa"
        # Central Philly neighborhoods
        self.central_areas = ['center city', 'rittenhouse', 'old city', 'washington square',
                            'university city', 'fairmount', 'northern liberties']
    
    def is_central_philly(self, location):
        location = location.lower()
        return any(area in location for area in self.central_areas)
    
    def parse_price(self, price_str):
        if not price_str:
            return None
        try:
            # Remove '$' and ',' and convert to float
            return float(price_str.replace('$', '').replace(',', ''))
        except ValueError:
            return None

    def scrape_listings(self):
        params = {
            'max_price': 1200,
            'availabilityMode': 0,  # All dates
            'sale_date': 'all'      # All postings
        }

        try:
            response = requests.get(self.search_url, params=params)
            print(f"Scraping URL: {response.url}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the results container and get all listings
            results_container = soup.find('div', class_='cl-results-page')
            if not results_container:
                print("Could not find results container")
                return []
            
            results = results_container.find_all('div', attrs={'data-pid': True})
            print(f"Found {len(results)} initial results")
            
            listings = []
            for item in results:
                try:
                    # Extract price
                    price_elem = item.find('span', class_='priceinfo')
                    if price_elem:
                        print(f"Found price element: {price_elem.text}")
                    price = self.parse_price(price_elem.text if price_elem else None)
                    
                    if not price or price > 1200:
                        print(f"Skipping due to price: {price}")
                        continue

                    # Extract location
                    location_elem = item.find('span', class_='housing')
                    if location_elem:
                        print(f"Found location: {location_elem.text}")
                    location = location_elem.text.strip('()') if location_elem else ''
                    
                    if not self.is_central_philly(location):
                        print(f"Skipping non-central location: {location}")
                        continue

                    # Get other details
                    title_elem = item.find('a', class_='posting-title')
                    if title_elem:
                        print(f"Found title: {title_elem.text}")
                    
                    listing = {
                        'title': title_elem.text if title_elem else '',
                        'price': price,
                        'location': location,
                        'listing_url': title_elem['href'] if title_elem else '',
                        'posted_date': item.select_one('time')['datetime'] if item.select_one('time') else None
                    }
                    
                    # Get full listing details
                    listing.update(self.get_listing_details(listing['listing_url']))
                    listings.append(listing)
                    print(f"Added listing: {listing['title']} - {listing['price']}")
                except Exception as e:
                    print(f"Error processing listing: {str(e)}")
                    continue

            print(f"Final number of filtered listings: {len(listings)}")
            return listings

        except requests.RequestException as e:
            print(f"Error scraping listings: {str(e)}")
            return []

    def get_listing_details(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            description = soup.select_one('#postingbody')
            description = description.text.strip() if description else ''
            
            # Get the first image URL
            image_url = None
            image_elem = soup.select_one('img.thumb')
            if image_elem and 'src' in image_elem.attrs:
                image_url = image_elem['src']

            return {
                'description': description,
                'image_url': image_url
            }

        except requests.RequestException:
            return {'description': '', 'image_url': None}

def save_to_db(listings, db_path='listings.db'):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for listing in listings:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO listings 
                    (title, price, location, description, image_url, listing_url, posted_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    listing['title'],
                    listing['price'],
                    listing['location'],
                    listing['description'],
                    listing['image_url'],
                    listing['listing_url'],
                    listing['posted_date']
                ))
            except sqlite3.Error as e:
                print(f"Error saving listing: {e}")
        conn.commit() 
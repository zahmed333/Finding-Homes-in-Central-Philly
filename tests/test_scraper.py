import unittest
import sqlite3
from datetime import datetime
from scraper import CraigslistScraper, save_to_db
from app import init_db
import os

class TestHouseFinder(unittest.TestCase):
    def setUp(self):
        # Use a test database
        self.test_db = 'test_listings.db'
        # Initialize test database
        with sqlite3.connect(self.test_db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    location TEXT,
                    description TEXT,
                    image_url TEXT,
                    listing_url TEXT UNIQUE,
                    posted_date DATETIME,
                    found_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def tearDown(self):
        # Clean up test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_price_parsing(self):
        scraper = CraigslistScraper()
        self.assertEqual(scraper.parse_price('$1,200'), 1200.0)
        self.assertEqual(scraper.parse_price('$950'), 950.0)
        self.assertIsNone(scraper.parse_price(''))
        self.assertIsNone(scraper.parse_price('Contact'))

    def test_location_filtering(self):
        scraper = CraigslistScraper()
        self.assertTrue(scraper.is_central_philly('Center City'))
        self.assertTrue(scraper.is_central_philly('Rittenhouse Square'))
        self.assertFalse(scraper.is_central_philly('Northeast Philadelphia'))
        self.assertFalse(scraper.is_central_philly('South Jersey'))

    def test_database_operations(self):
        test_listing = {
            'title': 'Test Apartment',
            'price': 1000.0,
            'location': 'Center City',
            'description': 'Test description',
            'image_url': 'http://example.com/image.jpg',
            'listing_url': 'http://example.com/listing',
            'posted_date': datetime.now().isoformat()
        }
        
        # Test saving to database
        save_to_db([test_listing], db_path=self.test_db)
        
        # Verify the listing was saved
        with sqlite3.connect(self.test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM listings WHERE title = ?', (test_listing['title'],))
            saved_listing = cursor.fetchone()
            
            self.assertIsNotNone(saved_listing)
            self.assertEqual(saved_listing['price'], test_listing['price'])
            self.assertEqual(saved_listing['location'], test_listing['location'])

    def test_duplicate_prevention(self):
        test_listing = {
            'title': 'Duplicate Test',
            'price': 1000.0,
            'location': 'Center City',
            'description': 'Test description',
            'image_url': 'http://example.com/image.jpg',
            'listing_url': 'http://example.com/listing',
            'posted_date': datetime.now().isoformat()
        }
        
        # Save the same listing twice
        save_to_db([test_listing], db_path=self.test_db)
        save_to_db([test_listing], db_path=self.test_db)
        
        # Verify only one entry exists
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM listings WHERE title = ?', (test_listing['title'],))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

if __name__ == '__main__':
    unittest.main() 
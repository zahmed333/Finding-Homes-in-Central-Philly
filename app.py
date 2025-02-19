from flask import Flask, render_template, jsonify
from datetime import datetime
import sqlite3
import os
from scraper import CraigslistScraper, save_to_db

app = Flask(__name__)

# Database initialization
def init_db():
    with sqlite3.connect('listings.db') as conn:
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

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        scraper = CraigslistScraper()
        listings = scraper.scrape_listings()
        print(f"Scraped {len(listings)} listings")
        save_to_db(listings)
        
        # Return the latest listings from the database
        with sqlite3.connect('listings.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM listings 
                WHERE found_date >= datetime('now', '-1 hour')
                ORDER BY posted_date DESC 
                LIMIT 50
            ''')
            results = cursor.fetchall()
            print(f"Found {len(results) if results else 0} results in database")
            if not results:
                return jsonify([])
            return jsonify([dict(row) for row in results])
    except Exception as e:
        print(f"Error in scan endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
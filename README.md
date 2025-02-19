# Philly Housing Finder

A web application that helps find affordable housing in central Philadelphia by automatically scraping Craigslist listings.

## Features

- Scrapes Craigslist for housing listings in central Philadelphia
- Filters listings by price (≤ $1200)
- Stores listings in a local database
- Web interface to view and manage listings
- Automatic duplicate detection

## Current Status

🚧 **Work in Progress** 🚧

The application is currently under development. The web interface and database components are functional, but the Craigslist scraper needs updating to match their current HTML structure.

## Requirements

- Python 3.8+
- Flask
- BeautifulSoup4
- SQLite3
- Requests

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Activate the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
python app.py
```

3. Open a web browser and navigate to:
```
http://127.0.0.1:5000
```

## Project Structure

- `app.py` - Flask application and routes
- `scraper.py` - Craigslist scraping functionality
- `templates/` - HTML templates
- `tests/` - Unit tests

## Known Issues

- Craigslist scraper needs updating to match current website structure
- Location filtering needs refinement
- Loading indicator needs improvement

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

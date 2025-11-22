# Marketing Business Scraper

A Python desktop application for scraping business data from Google Maps based on keyword and location.

## Features

- 🔍 Search businesses by keyword and location
- 📊 Extract business details (Name, Phone, Email, Website, Address, Rating, Reviews)
- 🤖 User agent rotation to avoid detection
- 📁 Export results to Excel (.xlsx)
- 🖥️ User-friendly GUI with progress tracking
- 🔄 Automatic deduplication

## Requirements

- Python 3.7+
- Chrome browser installed

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Enter your search parameters:
   - **Keyword**: Type of business (e.g., "dentist", "restaurant")
   - **Location**: City or area (e.g., "New York", "Los Angeles")
   - **Max Results**: Number of businesses to scrape (1-100)

3. Click "Start Scraping" and wait for the process to complete

4. Results will be saved in the `output` folder as an Excel file

## Output Format

The Excel file contains the following columns:
- Business Name
- Category
- Phone
- Email
- Website
- Address
- Rating
- Reviews
- Keyword
- City

## Important Notes

⚠️ **Legal Disclaimer**: Web scraping may violate Google Maps Terms of Service. This tool is for educational purposes only. Use at your own risk.

## Project Structure

```
marketing_scraper/
├── main.py              # GUI application
├── scraper/
│   ├── engine.py        # Scraping logic
│   ├── utils.py         # User agent rotation

├── data/
│   └── exporter.py      # Excel export
├── requirements.txt     # Dependencies
└── output/              # Generated Excel files
```

## Troubleshooting

- **Chrome not found**: Make sure Chrome is installed
- **Timeout errors**: Try reducing max results or running in non-headless mode
- **No data extracted**: Google Maps may have changed their HTML structure

# AWS Partner Scraper

This Python-based web scraper extracts information about AWS consulting service partners from the Amazon Partner Network. It navigates through partner listings, collects details such as company names, profile links, and websites, and exports the data to an Excel file for easy analysis.

## Features

- Scrapes multiple pages of AWS partner listings
- Extracts company names, profile links, and website URLs
- Implements random delays and scrolling to mimic human behavior
- Uses rotating user agents to avoid detection
- Exports data to an Excel file

## Requirements

- Python 3.10
- pandas
- selenium
- beautifulsoup4
- fake_useragent
- openpyxl (for Excel export)

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/aws-partner-scraper.git
   cd aws-partner-scraper
   ```

2. Install the required packages:
   ```
   pip install pandas selenium beautifulsoup4 fake_useragent openpyxl
   ```

3. Download the appropriate ChromeDriver for your system and ensure it's in your PATH.

## Usage

Run the script with:

```
python amazon.py
```

The script will start scraping the AWS partner network and save the results to `companies.xlsx` in the same directory.

## Note

Web scraping may be against the terms of service of some websites. Ensure you have permission to scrape the target website and use the data responsibly.

## License

[MIT License](LICENSE)

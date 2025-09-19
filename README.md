# gomaps_scraper

Command-line helper that searches Google Maps through the `gomaps` Python package and exports the places it finds to a CSV file that you can analyze or import elsewhere.

## Installation
- Install Python 3.8 or newer.
- Install dependencies: `pip install gomaps` (run inside a virtualenv if you prefer).

## Usage
Run the script with the search terms you would normally type into Google Maps. Optional flags let you narrow the results:

```
python main.py "coffee shops"
python main.py "restaurants" --zip 10001 --distance 5 --max-results 40
python main.py "pizza" --page 2
```

### Arguments
- `query` (required): the search phrase to send to Google Maps.
- `--zip`: restrict results to locations near the given ZIP code.
- `--distance`: hint about the search radius in miles (only valid when `--zip` is set).
- `--max-results`: cap the number of places to fetch (default 20).
- `--page`: choose which results page to scrape (default 1).

The script prints a short summary to the console and writes a CSV named `YYYYMMDD_<query>.csv`, where the date is the run date and the query is sanitized for safe filenames. Each row includes the place name, address, coordinates, phone, website, rating, Google Maps URL, current hours status, and the hours for each day of the week when available.

## Notes
- The `gomaps` library handles the underlying scraping and enforces a short delay between requests to reduce the chance of being rate limited.
- If the script cannot retrieve full details for a place, it still records whatever information is available.

# National Parks Brochure Scraper

A Python web scraper that catalogs brochures for all US National Parks from npshistory.com, downloads PDFs, extracts text, parses key information, and exports results to Google Sheets.

## Features

- Scrapes brochure links from all 63 US National Parks
- Downloads PDF brochures (configurable limit for testing)
- Extracts text content from PDFs
- Parses key information:
  - Park name
  - State/location
  - Established year
  - Size (acres/square miles)
- Exports results to Google Sheets
- Respects website with 10-second delays between requests
- Comprehensive error handling and logging
- Designed for Google Colab but works standalone

## Quick Start (Google Colab - Recommended)

1. **Open the Colab Notebook**:
   - Upload `national_parks_scraper_colab.ipynb` to Google Colab
   - Or open directly: [Open in Colab](https://colab.research.google.com/)

2. **Run All Cells**:
   - Click `Runtime > Run all`
   - Authenticate when prompted for Google Sheets access

3. **View Results**:
   - Results are automatically saved to Google Sheets
   - PDFs downloaded to `/content/national_parks_brochures/`
   - JSON results saved in the same directory

## Local Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd National-Parks-Scraper-
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the scraper**:
   ```bash
   python national_parks_brochure_scraper.py
   ```

## Usage

### Basic Usage

```python
from national_parks_brochure_scraper import NationalParksScraper

# Initialize scraper
scraper = NationalParksScraper(
    download_dir='national_parks_brochures',
    request_delay=10,  # seconds between requests
    max_pdfs=20        # limit for testing
)

# Run scraper
results = scraper.scrape_all_parks()

# Save results
scraper.save_to_json()
scraper.write_to_google_sheets()  # Requires Google Colab
scraper.print_summary()
```

### Configuration Options

```python
scraper = NationalParksScraper(
    base_url="https://npshistory.com/publications/",  # Base URL
    download_dir="national_parks_brochures",           # Download directory
    request_delay=10,                                  # Delay between requests (seconds)
    max_pdfs=20                                        # Maximum PDFs to download
)
```

### Customizing Park Selection

To scrape specific parks only:

```python
# Modify the scrape_all_parks method to filter specific parks
target_parks = ['YELL', 'YOSE', 'GRCA']  # Yellowstone, Yosemite, Grand Canyon

for park_code in target_parks:
    brochure_links = scraper.scrape_park_brochures(park_code)
    # ... rest of the logic
```

## National Parks Coverage

The scraper includes all 63 US National Parks:

- Acadia (ACAD)
- Arches (ARCH)
- Badlands (BADL)
- Big Bend (BIBE)
- Biscayne (BISC)
- Black Canyon of the Gunnison (BLCA)
- Bryce Canyon (BRCA)
- Canyonlands (CANY)
- Capitol Reef (CARE)
- Carlsbad Caverns (CAVE)
- Channel Islands (CHIS)
- Congaree (CONG)
- Crater Lake (CRLA)
- Cuyahoga Valley (CUVA)
- Denali (DENA)
- Dry Tortugas (DRTO)
- Everglades (EVER)
- Gates of the Arctic (GAAR)
- Gateway Arch (GOGA)
- Glacier (GLAC)
- Glacier Bay (GLBA)
- Grand Canyon (GRCA)
- Grand Teton (GRTE)
- Great Basin (GRBA)
- Great Sand Dunes (GRSA)
- Great Smoky Mountains (GRSM)
- Guadalupe Mountains (GUMO)
- Haleakalā (HALE)
- Hawaiʻi Volcanoes (HAVO)
- Hot Springs (HOSP)
- Indiana Dunes (INDU)
- Isle Royale (ISRO)
- Joshua Tree (JOTR)
- Katmai (KATM)
- Kenai Fjords (KEFJ)
- Kobuk Valley (KOVA)
- Lake Clark (LACL)
- Lassen Volcanic (LAVO)
- Mammoth Cave (MACA)
- Mesa Verde (MEVE)
- Mount Rainier (MORA)
- New River Gorge (NPSA)
- North Cascades (NOCA)
- Olympic (OLYM)
- Petrified Forest (PEFO)
- Pinnacles (PINN)
- Redwood (REDW)
- Rocky Mountain (ROMO)
- Saguaro (SAGU)
- Sequoia (SEKI)
- Shenandoah (SHEN)
- Theodore Roosevelt (THRO)
- Voyageurs (VOYA)
- White Sands (WHSA)
- Wind Cave (WICA)
- Wrangell-St. Elias (WRST)
- Yellowstone (YELL)
- Yosemite (YOSE)
- Zion (ZION)

## Output Format

### JSON Output

Results are saved to `national_parks_results.json`:

```json
{
  "results": [
    {
      "park_code": "YELL",
      "park_name": "Yellowstone National Park",
      "state": "Wyoming/Montana/Idaho",
      "established_year": "1872",
      "size": "2,219,791 acres",
      "pdf_url": "https://npshistory.com/publications/yell/brochures/1980.pdf",
      "local_file": "national_parks_brochures/YELL_1980.pdf",
      "scraped_at": "2025-01-15T10:30:00"
    }
  ],
  "errors": [],
  "metadata": {
    "total_parks_processed": 10,
    "total_pdfs_downloaded": 20,
    "total_errors": 2,
    "scrape_date": "2025-01-15T10:30:00"
  }
}
```

### Google Sheets Output

Columns:
- Park Code
- Park Name
- State
- Established Year
- Size
- PDF URL
- Local File
- Scraped At

## Error Handling

The scraper handles various errors gracefully:

- **Network errors**: Retries with exponential backoff
- **404 errors**: Logs and continues to next park
- **PDF extraction errors**: Logs and marks text as unavailable
- **Google Sheets errors**: Saves to JSON as fallback

All errors are logged in the `errors` array in the JSON output.

## Rate Limiting

The scraper respects the website with:
- **10-second delay** between requests (configurable)
- **Progressive backoff** on failed requests
- **Proper User-Agent headers** to identify the scraper

## Limitations

- **Data accuracy**: Not all brochures contain structured information about established year and size
- **PDF parsing**: Some older PDFs may be scanned images without extractable text
- **URL structure**: Assumes npshistory.com follows the pattern `/publications/{park_code}/brochures/index.htm`
- **Rate limiting**: May take several hours to scrape all parks with proper delays

## Troubleshooting

### 403 Forbidden Errors
If you encounter 403 errors, try:
- Increasing the `request_delay` to 15-20 seconds
- Running at different times of day
- Checking if your IP has been temporarily blocked

### PDF Extraction Fails
Some PDFs may be scanned images without text:
- The scraper will log these errors and continue
- Consider using OCR (pytesseract) for image-based PDFs

### Google Sheets Authentication
In Google Colab:
- Click the authentication link when prompted
- Grant necessary permissions
- If it fails, restart runtime and try again

### No Brochures Found
Some parks may not have brochures available:
- Check the URL manually: `https://npshistory.com/publications/{park_code}/brochures/`
- The park code may be different or not yet digitized

## Development

### Project Structure

```
National-Parks-Scraper-/
├── national_parks_brochure_scraper.py  # Main scraper script
├── national_parks_scraper_colab.ipynb  # Google Colab notebook
├── requirements.txt                     # Python dependencies
├── README.md                           # This file
└── national_parks_brochures/           # Downloaded PDFs and results (created at runtime)
    ├── {park_code}_{filename}.pdf
    └── national_parks_results.json
```

### Adding New Parks

To add newly designated national parks:

1. Find the park's 4-letter code from [NPS.gov](https://www.nps.gov/articles/000/historic-listing-of-nps-park-codes.htm)
2. Add to the `NATIONAL_PARKS` dictionary in the scraper:

```python
'NEWP': {'name': 'New Park National Park', 'state': 'State'},
```

### Improving Parsing

The text parsing uses regex patterns. To improve extraction:

1. Analyze PDF text patterns
2. Add new regex patterns to `parse_park_info()`:

```python
# Example: Add pattern for different date format
year_patterns.append(r'founded in (\d{4})')
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Legal and Ethical Considerations

- **Respect robots.txt**: Always check the website's robots.txt
- **Rate limiting**: The 10-second delay is mandatory
- **Terms of service**: Review npshistory.com's terms before scraping
- **Data usage**: This is for educational and research purposes
- **Copyright**: Brochures may be copyrighted by the National Park Service

## License

This project is provided as-is for educational purposes.

## Resources

- [npshistory.com](https://npshistory.com/) - National Park Service History
- [NPS.gov](https://www.nps.gov/) - Official National Park Service website
- [NPS Park Codes](https://www.nps.gov/articles/000/historic-listing-of-nps-park-codes.htm) - Official park code listing

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error logs in the JSON output
3. Open an issue in the repository

## Acknowledgments

- National Park Service for preserving park history
- npshistory.com for digitizing historical documents
- Contributors and maintainers of the libraries used

---

**Note**: This scraper is designed for educational and research purposes. Always respect website terms of service and implement appropriate rate limiting when scraping.

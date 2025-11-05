"""
National Parks Brochure Scraper
Scrapes brochures from npshistory.com, downloads PDFs, extracts information,
and writes results to Google Sheets.

Designed to run in Google Colab with proper error handling and rate limiting.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import os
from urllib.parse import urljoin, urlparse
import PyPDF2
import io
from datetime import datetime
import json

# For Google Sheets integration
try:
    import gspread
    from google.colab import auth
    from google.auth import default
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("Warning: Google Sheets integration not available. Run in Google Colab for full functionality.")


class NationalParksScraper:
    """Scraper for National Parks brochures from npshistory.com"""

    # Comprehensive list of US National Parks with their 4-letter codes
    NATIONAL_PARKS = {
        'ACAD': {'name': 'Acadia National Park', 'state': 'Maine'},
        'ARCH': {'name': 'Arches National Park', 'state': 'Utah'},
        'BADL': {'name': 'Badlands National Park', 'state': 'South Dakota'},
        'BIBE': {'name': 'Big Bend National Park', 'state': 'Texas'},
        'BISC': {'name': 'Biscayne National Park', 'state': 'Florida'},
        'BLCA': {'name': 'Black Canyon of the Gunnison National Park', 'state': 'Colorado'},
        'BRCA': {'name': 'Bryce Canyon National Park', 'state': 'Utah'},
        'CANY': {'name': 'Canyonlands National Park', 'state': 'Utah'},
        'CARE': {'name': 'Capitol Reef National Park', 'state': 'Utah'},
        'CAVE': {'name': 'Carlsbad Caverns National Park', 'state': 'New Mexico'},
        'CHIS': {'name': 'Channel Islands National Park', 'state': 'California'},
        'CONG': {'name': 'Congaree National Park', 'state': 'South Carolina'},
        'CRLA': {'name': 'Crater Lake National Park', 'state': 'Oregon'},
        'CUVA': {'name': 'Cuyahoga Valley National Park', 'state': 'Ohio'},
        'DENA': {'name': 'Denali National Park', 'state': 'Alaska'},
        'DRTO': {'name': 'Dry Tortugas National Park', 'state': 'Florida'},
        'EVER': {'name': 'Everglades National Park', 'state': 'Florida'},
        'GAAR': {'name': 'Gates of the Arctic National Park', 'state': 'Alaska'},
        'GLAC': {'name': 'Glacier National Park', 'state': 'Montana'},
        'GLBA': {'name': 'Glacier Bay National Park', 'state': 'Alaska'},
        'GRBA': {'name': 'Great Basin National Park', 'state': 'Nevada'},
        'GRCA': {'name': 'Grand Canyon National Park', 'state': 'Arizona'},
        'GRSA': {'name': 'Great Sand Dunes National Park', 'state': 'Colorado'},
        'GRSM': {'name': 'Great Smoky Mountains National Park', 'state': 'Tennessee/North Carolina'},
        'GRTE': {'name': 'Grand Teton National Park', 'state': 'Wyoming'},
        'GUMO': {'name': 'Guadalupe Mountains National Park', 'state': 'Texas'},
        'HALE': {'name': 'Haleakalā National Park', 'state': 'Hawaii'},
        'HAVO': {'name': 'Hawaiʻi Volcanoes National Park', 'state': 'Hawaii'},
        'HOSP': {'name': 'Hot Springs National Park', 'state': 'Arkansas'},
        'ISRO': {'name': 'Isle Royale National Park', 'state': 'Michigan'},
        'JOTR': {'name': 'Joshua Tree National Park', 'state': 'California'},
        'KATM': {'name': 'Katmai National Park', 'state': 'Alaska'},
        'KEFJ': {'name': 'Kenai Fjords National Park', 'state': 'Alaska'},
        'KOVA': {'name': 'Kobuk Valley National Park', 'state': 'Alaska'},
        'LACL': {'name': 'Lake Clark National Park', 'state': 'Alaska'},
        'LAVO': {'name': 'Lassen Volcanic National Park', 'state': 'California'},
        'MACA': {'name': 'Mammoth Cave National Park', 'state': 'Kentucky'},
        'MEVE': {'name': 'Mesa Verde National Park', 'state': 'Colorado'},
        'MORA': {'name': 'Mount Rainier National Park', 'state': 'Washington'},
        'NOCA': {'name': 'North Cascades National Park', 'state': 'Washington'},
        'OLYM': {'name': 'Olympic National Park', 'state': 'Washington'},
        'PEFO': {'name': 'Petrified Forest National Park', 'state': 'Arizona'},
        'PINN': {'name': 'Pinnacles National Park', 'state': 'California'},
        'REDW': {'name': 'Redwood National Park', 'state': 'California'},
        'ROMO': {'name': 'Rocky Mountain National Park', 'state': 'Colorado'},
        'SAGU': {'name': 'Saguaro National Park', 'state': 'Arizona'},
        'SEKI': {'name': 'Sequoia National Park', 'state': 'California'},
        'SHEN': {'name': 'Shenandoah National Park', 'state': 'Virginia'},
        'THRO': {'name': 'Theodore Roosevelt National Park', 'state': 'North Dakota'},
        'VOYA': {'name': 'Voyageurs National Park', 'state': 'Minnesota'},
        'WICA': {'name': 'Wind Cave National Park', 'state': 'South Dakota'},
        'WRST': {'name': 'Wrangell-St. Elias National Park', 'state': 'Alaska'},
        'YELL': {'name': 'Yellowstone National Park', 'state': 'Wyoming/Montana/Idaho'},
        'YOSE': {'name': 'Yosemite National Park', 'state': 'California'},
        'ZION': {'name': 'Zion National Park', 'state': 'Utah'},
        'INDU': {'name': 'Indiana Dunes National Park', 'state': 'Indiana'},
        'GOGA': {'name': 'Gateway Arch National Park', 'state': 'Missouri'},
        'NPSA': {'name': 'New River Gorge National Park', 'state': 'West Virginia'},
        'WHSA': {'name': 'White Sands National Park', 'state': 'New Mexico'},
    }

    def __init__(self, base_url="https://npshistory.com/publications/",
                 download_dir="national_parks_brochures",
                 request_delay=10,
                 max_pdfs=20):
        """
        Initialize the scraper.

        Args:
            base_url: Base URL for npshistory.com publications
            download_dir: Directory to save downloaded PDFs
            request_delay: Delay between requests in seconds (default 10)
            max_pdfs: Maximum number of PDFs to download (default 20)
        """
        self.base_url = base_url
        self.download_dir = download_dir
        self.request_delay = request_delay
        self.max_pdfs = max_pdfs
        self.session = requests.Session()

        # Set headers to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Create download directory
        os.makedirs(self.download_dir, exist_ok=True)

        # Results storage
        self.results = []
        self.errors = []

    def get_page(self, url, retries=3):
        """
        Fetch a page with error handling and retries.

        Args:
            url: URL to fetch
            retries: Number of retry attempts

        Returns:
            Response object or None if failed
        """
        for attempt in range(retries):
            try:
                print(f"Fetching: {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 5  # Progressive backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.errors.append({'url': url, 'error': str(e), 'type': 'fetch_error'})
                    return None
        return None

    def scrape_park_brochures(self, park_code):
        """
        Scrape brochure links for a specific park.

        Args:
            park_code: 4-letter park code (e.g., 'NOCA')

        Returns:
            List of brochure URLs
        """
        park_code_lower = park_code.lower()
        brochure_url = f"{self.base_url}{park_code_lower}/brochures/index.htm"

        print(f"\nScraping brochures for {park_code} - {self.NATIONAL_PARKS.get(park_code, {}).get('name', 'Unknown')}")
        print(f"URL: {brochure_url}")

        response = self.get_page(brochure_url)
        if not response:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        brochure_links = []

        # Look for PDF links in the brochures section
        # Typically after the #brochures anchor
        brochure_section = soup.find('a', {'name': 'brochures'})

        if brochure_section:
            # Find all links after the brochures anchor
            current = brochure_section.find_next()
            while current:
                if current.name == 'a' and current.get('href', '').endswith('.pdf'):
                    pdf_url = urljoin(brochure_url, current['href'])
                    brochure_links.append(pdf_url)
                current = current.find_next_sibling()
        else:
            # If no anchor found, look for all PDF links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    pdf_url = urljoin(brochure_url, href)
                    brochure_links.append(pdf_url)

        print(f"Found {len(brochure_links)} brochure links for {park_code}")
        return brochure_links

    def download_pdf(self, url, filename):
        """
        Download a PDF file.

        Args:
            url: PDF URL
            filename: Local filename to save

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            filepath = os.path.join(self.download_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"Saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            self.errors.append({'url': url, 'error': str(e), 'type': 'download_error'})
            return None

    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or empty string if failed
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            self.errors.append({'file': pdf_path, 'error': str(e), 'type': 'extraction_error'})
            return ""

    def parse_park_info(self, text, park_code):
        """
        Parse park information from PDF text.

        Args:
            text: Extracted PDF text
            park_code: Park code for fallback data

        Returns:
            Dictionary with parsed information
        """
        info = {
            'park_name': self.NATIONAL_PARKS.get(park_code, {}).get('name', 'Unknown'),
            'state': self.NATIONAL_PARKS.get(park_code, {}).get('state', 'Unknown'),
            'established_year': 'Unknown',
            'size': 'Unknown'
        }

        # Parse established year - look for patterns like "established 1916", "Est. 1916", etc.
        year_patterns = [
            r'established[:\s]+(\d{4})',
            r'est[\.\s]+(\d{4})',
            r'designated[:\s]+(\d{4})',
            r'authorized[:\s]+(\d{4})',
            r'created[:\s]+(\d{4})',
        ]

        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['established_year'] = match.group(1)
                break

        # Parse size - look for patterns like "1,234 acres", "1,234 square miles", etc.
        size_patterns = [
            r'([\d,]+)\s*acres',
            r'([\d,]+)\s*square miles',
            r'([\d,]+)\s*sq\.\s*mi',
            r'([\d,]+)\s*hectares',
        ]

        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['size'] = match.group(0)
                break

        return info

    def scrape_all_parks(self):
        """
        Scrape brochures from all national parks.

        Returns:
            List of results
        """
        pdf_count = 0

        for park_code in sorted(self.NATIONAL_PARKS.keys()):
            if pdf_count >= self.max_pdfs:
                print(f"\nReached maximum PDF limit ({self.max_pdfs}). Stopping.")
                break

            # Get brochure links for this park
            brochure_links = self.scrape_park_brochures(park_code)

            # Respect rate limit
            time.sleep(self.request_delay)

            # Download and process PDFs
            for pdf_url in brochure_links:
                if pdf_count >= self.max_pdfs:
                    break

                # Generate filename
                filename = f"{park_code}_{os.path.basename(urlparse(pdf_url).path)}"

                # Download PDF
                pdf_path = self.download_pdf(pdf_url, filename)

                if pdf_path:
                    # Extract text
                    text = self.extract_text_from_pdf(pdf_path)

                    # Parse information
                    park_info = self.parse_park_info(text, park_code)
                    park_info['pdf_url'] = pdf_url
                    park_info['local_file'] = pdf_path
                    park_info['park_code'] = park_code
                    park_info['scraped_at'] = datetime.now().isoformat()

                    self.results.append(park_info)
                    pdf_count += 1

                    print(f"Processed: {park_info['park_name']} - {filename}")
                    print(f"  State: {park_info['state']}")
                    print(f"  Established: {park_info['established_year']}")
                    print(f"  Size: {park_info['size']}")

                # Respect rate limit between PDFs
                if pdf_count < self.max_pdfs:
                    print(f"Waiting {self.request_delay} seconds before next request...")
                    time.sleep(self.request_delay)

        return self.results

    def save_to_json(self, filename='national_parks_results.json'):
        """
        Save results to JSON file.

        Args:
            filename: Output filename
        """
        output = {
            'results': self.results,
            'errors': self.errors,
            'metadata': {
                'total_parks_processed': len(set([r['park_code'] for r in self.results])),
                'total_pdfs_downloaded': len(self.results),
                'total_errors': len(self.errors),
                'scrape_date': datetime.now().isoformat()
            }
        }

        filepath = os.path.join(self.download_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to: {filepath}")
        return filepath

    def write_to_google_sheets(self, spreadsheet_name='National Parks Brochures'):
        """
        Write results to Google Sheets (requires Google Colab environment).

        Args:
            spreadsheet_name: Name of the spreadsheet to create/update
        """
        if not SHEETS_AVAILABLE:
            print("Google Sheets integration not available. Run in Google Colab.")
            return None

        try:
            # Authenticate
            auth.authenticate_user()
            creds, _ = default()
            gc = gspread.authorize(creds)

            # Create or open spreadsheet
            try:
                spreadsheet = gc.open(spreadsheet_name)
                worksheet = spreadsheet.sheet1
                worksheet.clear()
            except gspread.SpreadsheetNotFound:
                spreadsheet = gc.create(spreadsheet_name)
                worksheet = spreadsheet.sheet1

            # Prepare data
            headers = ['Park Code', 'Park Name', 'State', 'Established Year',
                      'Size', 'PDF URL', 'Local File', 'Scraped At']

            rows = [headers]
            for result in self.results:
                row = [
                    result.get('park_code', ''),
                    result.get('park_name', ''),
                    result.get('state', ''),
                    result.get('established_year', ''),
                    result.get('size', ''),
                    result.get('pdf_url', ''),
                    result.get('local_file', ''),
                    result.get('scraped_at', '')
                ]
                rows.append(row)

            # Write to sheet
            worksheet.update('A1', rows)

            print(f"\nResults written to Google Sheet: {spreadsheet_name}")
            print(f"URL: {spreadsheet.url}")

            return spreadsheet.url
        except Exception as e:
            print(f"Error writing to Google Sheets: {e}")
            self.errors.append({'error': str(e), 'type': 'sheets_error'})
            return None

    def print_summary(self):
        """Print summary of scraping results."""
        print("\n" + "="*70)
        print("SCRAPING SUMMARY")
        print("="*70)
        print(f"Total Parks Processed: {len(set([r['park_code'] for r in self.results]))}")
        print(f"Total PDFs Downloaded: {len(self.results)}")
        print(f"Total Errors: {len(self.errors)}")
        print(f"Download Directory: {self.download_dir}")

        if self.results:
            print("\n" + "-"*70)
            print("SAMPLE RESULTS:")
            print("-"*70)
            for i, result in enumerate(self.results[:5], 1):
                print(f"\n{i}. {result['park_name']}")
                print(f"   State: {result['state']}")
                print(f"   Established: {result['established_year']}")
                print(f"   Size: {result['size']}")

        if self.errors:
            print("\n" + "-"*70)
            print("ERRORS:")
            print("-"*70)
            for i, error in enumerate(self.errors[:10], 1):
                print(f"{i}. {error.get('type', 'unknown')}: {error.get('error', 'Unknown error')[:100]}")


def main():
    """Main function to run the scraper."""
    print("="*70)
    print("NATIONAL PARKS BROCHURE SCRAPER")
    print("="*70)
    print("\nThis script will:")
    print("1. Scrape brochure links from npshistory.com")
    print("2. Download up to 20 PDF files for testing")
    print("3. Extract text from each PDF")
    print("4. Parse park information (name, state, established year, size)")
    print("5. Save results to JSON and Google Sheets (if in Colab)")
    print("\nRate limit: 10 seconds between requests")
    print("-"*70)

    # Initialize scraper
    scraper = NationalParksScraper(
        download_dir='national_parks_brochures',
        request_delay=10,
        max_pdfs=20
    )

    # Run scraper
    print("\nStarting scrape...")
    results = scraper.scrape_all_parks()

    # Save results
    print("\nSaving results...")
    scraper.save_to_json()

    # Try to write to Google Sheets if in Colab
    scraper.write_to_google_sheets()

    # Print summary
    scraper.print_summary()

    print("\n" + "="*70)
    print("SCRAPING COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()

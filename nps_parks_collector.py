"""
National Parks Data Collector for Google Colab
Collects data from the National Parks Service API and saves to Google Sheets
"""

# Import required libraries
import requests
import pandas as pd
import gspread
from google.colab import auth
from google.auth import default

# ============================================================================
# CONFIGURATION - PASTE YOUR VALUES HERE
# ============================================================================

# PASTE YOUR NPS API KEY HERE (get one from https://www.nps.gov/subjects/developer/get-started.htm)
API_KEY = "c5PoOPOxWlyXHj8d2cDe4en6BXDfOX9tUFdq7mec
"

# PASTE YOUR GOOGLE SHEET URL HERE (e.g., https://docs.google.com/spreadsheets/d/1abc.../edit)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1OCOCrZ_EGLvTLIJLDEs8Z97Z6D-PLzAmsDqAKj8rjhY/edit?usp=sharing"

# ============================================================================

# Maximum number of parks to collect
MAX_PARKS = 50

# NPS API endpoint
NPS_API_URL = "https://developer.nps.gov/api/v1/parks"


def authenticate_google():
    """Authenticate with Google and return gspread client"""
    print("Authenticating with Google...")
    auth.authenticate_user()
    creds, _ = default()
    gc = gspread.authorize(creds)
    print("✓ Google authentication successful")
    return gc


def fetch_parks_data(api_key, limit=50):
    """Fetch parks data from NPS API"""
    print(f"\nFetching up to {limit} parks from NPS API...")

    params = {
        "api_key": api_key,
        "limit": limit
    }

    try:
        response = requests.get(NPS_API_URL, params=params)
        response.raise_for_status()
        print(f"✓ API request successful (Status: {response.status_code})")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data from NPS API: {e}")
        return None


def parse_parks_data(api_response):
    """Parse parks data and extract required fields"""
    if not api_response or "data" not in api_response:
        print("✗ No data found in API response")
        return []

    parks_data = []
    parks = api_response.get("data", [])

    print(f"\nParsing data for {len(parks)} parks...")

    for park in parks:
        try:
            park_info = {
                "fullName": park.get("fullName", "N/A"),
                "states": park.get("states", "N/A"),
                "description": park.get("description", "N/A"),
                "acres": park.get("acres", "N/A"),
                "designation": park.get("designation", "N/A")
            }
            parks_data.append(park_info)
        except Exception as e:
            print(f"  Warning: Error parsing park data - {e}")
            continue

    print(f"✓ Successfully parsed {len(parks_data)} parks")
    return parks_data


def create_dataframe(parks_data):
    """Create pandas DataFrame from parks data"""
    if not parks_data:
        print("✗ No parks data to create DataFrame")
        return None

    print("\nCreating DataFrame...")
    df = pd.DataFrame(parks_data)
    print(f"✓ DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    print(f"\nColumns: {', '.join(df.columns.tolist())}")
    return df


def write_to_google_sheet(gc, sheet_url, df):
    """Write DataFrame to Google Sheet"""
    print(f"\nWriting data to Google Sheet...")

    try:
        # Open the Google Sheet
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet.sheet1  # Use the first worksheet

        # Clear existing data
        worksheet.clear()
        print("✓ Cleared existing data")

        # Convert DataFrame to list of lists (including header)
        data = [df.columns.tolist()] + df.values.tolist()

        # Update the sheet
        worksheet.update(data, 'A1')
        print(f"✓ Successfully wrote {len(df)} rows to Google Sheet")
        print(f"\nSheet URL: {sheet_url}")

    except gspread.exceptions.SpreadsheetNotFound:
        print("✗ Error: Could not find the Google Sheet. Make sure the URL is correct.")
    except gspread.exceptions.APIError as e:
        print(f"✗ Error: Google Sheets API error - {e}")
    except Exception as e:
        print(f"✗ Error writing to Google Sheet: {e}")


def main():
    """Main function to orchestrate the data collection"""
    print("=" * 70)
    print("National Parks Data Collector")
    print("=" * 70)

    # Validate configuration
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n✗ ERROR: Please paste your NPS API key in the API_KEY variable")
        print("  Get your API key from: https://www.nps.gov/subjects/developer/get-started.htm")
        return

    if SHEET_URL == "YOUR_GOOGLE_SHEET_URL_HERE":
        print("\n✗ ERROR: Please paste your Google Sheet URL in the SHEET_URL variable")
        return

    # Step 1: Authenticate with Google
    try:
        gc = authenticate_google()
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return

    # Step 2: Fetch parks data from NPS API
    api_response = fetch_parks_data(API_KEY, limit=MAX_PARKS)
    if not api_response:
        return

    # Step 3: Parse the data
    parks_data = parse_parks_data(api_response)
    if not parks_data:
        return

    # Step 4: Create DataFrame
    df = create_dataframe(parks_data)
    if df is None:
        return

    # Step 5: Write to Google Sheet
    write_to_google_sheet(gc, SHEET_URL, df)

    print("\n" + "=" * 70)
    print("Data collection complete!")
    print("=" * 70)


# Run the main function
if __name__ == "__main__":
    main()

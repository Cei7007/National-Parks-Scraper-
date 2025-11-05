"""
Example usage of the National Parks Brochure Scraper
Run this script to see how to use the scraper programmatically.
"""

from national_parks_brochure_scraper import NationalParksScraper


def example_basic_usage():
    """Basic usage example - scrape 5 PDFs with default settings"""
    print("="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)

    scraper = NationalParksScraper(
        download_dir='examples/basic',
        request_delay=10,
        max_pdfs=5
    )

    results = scraper.scrape_all_parks()
    scraper.save_to_json()
    scraper.print_summary()

    return results


def example_specific_parks():
    """Example: Scrape specific parks only"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Scrape Specific Parks")
    print("="*70)

    scraper = NationalParksScraper(
        download_dir='examples/specific',
        request_delay=10,
        max_pdfs=10
    )

    # Target specific parks
    target_parks = ['YELL', 'YOSE', 'GRCA', 'GLAC', 'ZION']
    park_names = [scraper.NATIONAL_PARKS[code]['name'] for code in target_parks]

    print(f"\nTargeting parks: {', '.join(park_names)}")
    print("-"*70)

    pdf_count = 0
    for park_code in target_parks:
        if pdf_count >= scraper.max_pdfs:
            break

        brochure_links = scraper.scrape_park_brochures(park_code)

        import time
        from urllib.parse import urlparse
        import os

        time.sleep(scraper.request_delay)

        for pdf_url in brochure_links:
            if pdf_count >= scraper.max_pdfs:
                break

            filename = f"{park_code}_{os.path.basename(urlparse(pdf_url).path)}"
            pdf_path = scraper.download_pdf(pdf_url, filename)

            if pdf_path:
                text = scraper.extract_text_from_pdf(pdf_path)
                park_info = scraper.parse_park_info(text, park_code)
                park_info['pdf_url'] = pdf_url
                park_info['local_file'] = pdf_path
                park_info['park_code'] = park_code

                from datetime import datetime
                park_info['scraped_at'] = datetime.now().isoformat()

                scraper.results.append(park_info)
                pdf_count += 1

                print(f"\nProcessed: {park_info['park_name']}")
                print(f"  Established: {park_info['established_year']} | Size: {park_info['size']}")

            if pdf_count < scraper.max_pdfs:
                time.sleep(scraper.request_delay)

    scraper.save_to_json('specific_parks_results.json')
    scraper.print_summary()

    return scraper.results


def example_custom_parsing():
    """Example: Custom parsing with additional data extraction"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Parsing")
    print("="*70)

    scraper = NationalParksScraper(
        download_dir='examples/custom',
        request_delay=10,
        max_pdfs=3
    )

    # Override the parse_park_info method to add custom parsing
    original_parse = scraper.parse_park_info

    def custom_parse(text, park_code):
        # Get basic info
        info = original_parse(text, park_code)

        # Add custom parsing for visitor info
        import re

        # Look for visitor numbers
        visitor_pattern = r'([\d,]+)\s*visitors?'
        match = re.search(visitor_pattern, text, re.IGNORECASE)
        if match:
            info['annual_visitors'] = match.group(1)
        else:
            info['annual_visitors'] = 'Unknown'

        # Look for elevation
        elevation_pattern = r'([\d,]+)\s*feet\s*(?:above\s*sea\s*level|elevation)?'
        match = re.search(elevation_pattern, text, re.IGNORECASE)
        if match:
            info['elevation'] = f"{match.group(1)} feet"
        else:
            info['elevation'] = 'Unknown'

        return info

    scraper.parse_park_info = custom_parse

    results = scraper.scrape_all_parks()
    scraper.save_to_json('custom_parsing_results.json')

    print("\n" + "-"*70)
    print("Results with custom fields:")
    print("-"*70)
    for result in results[:3]:
        print(f"\n{result['park_name']}")
        print(f"  Annual Visitors: {result.get('annual_visitors', 'N/A')}")
        print(f"  Elevation: {result.get('elevation', 'N/A')}")

    return results


def example_error_handling():
    """Example: Demonstrate error handling"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Error Handling")
    print("="*70)

    scraper = NationalParksScraper(
        download_dir='examples/errors',
        request_delay=5,  # Faster for testing
        max_pdfs=5
    )

    # Try to scrape with potential errors
    results = scraper.scrape_all_parks()

    print("\n" + "-"*70)
    print("Error Summary:")
    print("-"*70)
    print(f"Total errors: {len(scraper.errors)}")

    if scraper.errors:
        error_types = {}
        for error in scraper.errors:
            error_type = error.get('type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

        print("\nError breakdown:")
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count}")

        print("\nSample errors:")
        for i, error in enumerate(scraper.errors[:3], 1):
            print(f"\n{i}. Type: {error.get('type')}")
            print(f"   Message: {str(error.get('error', ''))[:100]}")

    return results


def main():
    """Run all examples"""
    print("="*70)
    print("NATIONAL PARKS BROCHURE SCRAPER - USAGE EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate different ways to use the scraper.")
    print("Each example will create a separate directory under 'examples/'")
    print("\nNote: Running all examples will take some time due to rate limiting.")
    print("="*70)

    # Uncomment the examples you want to run:

    # Example 1: Basic usage
    example_basic_usage()

    # Example 2: Scrape specific parks
    # example_specific_parks()

    # Example 3: Custom parsing
    # example_custom_parsing()

    # Example 4: Error handling
    # example_error_handling()

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE!")
    print("="*70)
    print("\nCheck the 'examples/' directory for downloaded PDFs and results.")


if __name__ == "__main__":
    main()

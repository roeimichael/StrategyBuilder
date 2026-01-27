"""
Test script for downloading S&P 500 tickers from Wikipedia.

This script tests different methods and configurations to download
the S&P 500 ticker list from Wikipedia and helps debug any issues.
"""

import os
import sys
import pandas as pd
import urllib.request
import urllib.error
from io import StringIO


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_basic_pandas_read_html():
    """Test basic pandas read_html without any special configuration."""
    print_section("Test 1: Basic pandas.read_html()")

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    print(f"URL: {url}")

    try:
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-').tolist()
        print(f"✓ SUCCESS: Downloaded {len(tickers)} tickers")
        print(f"First 10 tickers: {tickers[:10]}")
        return tickers
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return None


def test_pandas_with_custom_headers():
    """Test pandas read_html with custom user agent."""
    print_section("Test 2: pandas.read_html() with custom headers")

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    print(f"URL: {url}")

    try:
        # Create a custom storage_options with headers
        storage_options = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        tables = pd.read_html(url, storage_options=storage_options)
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-').tolist()
        print(f"✓ SUCCESS: Downloaded {len(tickers)} tickers")
        print(f"First 10 tickers: {tickers[:10]}")
        return tickers
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return None


def test_urllib_request():
    """Test using urllib with custom headers."""
    print_section("Test 3: urllib.request with custom headers")

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    print(f"URL: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            print(f"✓ Downloaded HTML (length: {len(html)} bytes)")

            # Parse with pandas
            tables = pd.read_html(StringIO(html))
            df = tables[0]
            tickers = df['Symbol'].str.replace('.', '-').tolist()
            print(f"✓ SUCCESS: Parsed {len(tickers)} tickers")
            print(f"First 10 tickers: {tickers[:10]}")
            return tickers
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP ERROR {e.code}: {e.reason}")
        print(f"Headers: {e.headers}")
        return None
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return None


def test_requests_library():
    """Test using requests library (if available)."""
    print_section("Test 4: requests library with custom headers")

    try:
        import requests
    except ImportError:
        print("✗ SKIPPED: requests library not installed")
        print("  Install with: pip install requests")
        return None

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    print(f"URL: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✓ Downloaded HTML (status: {response.status_code}, length: {len(response.text)} bytes)")

        # Parse with pandas
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-').tolist()
        print(f"✓ SUCCESS: Parsed {len(tickers)} tickers")
        print(f"First 10 tickers: {tickers[:10]}")
        return tickers
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return None


def test_read_from_file():
    """Test reading from the existing tickers file."""
    print_section("Test 5: Reading from src/data/tickers.txt")

    # Determine the file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ticker_file = os.path.join(script_dir, 'src', 'data', 'tickers.txt')
    print(f"File path: {ticker_file}")

    if not os.path.exists(ticker_file):
        print(f"✗ FAILED: File not found at {ticker_file}")
        return None

    try:
        with open(ticker_file, 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
        print(f"✓ SUCCESS: Read {len(tickers)} tickers from file")
        print(f"First 10 tickers: {tickers[:10]}")
        return tickers
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return None


def save_tickers_to_file(tickers):
    """Save successfully downloaded tickers to file."""
    if not tickers:
        print("\n✗ No tickers to save")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'src', 'data')
    ticker_file = os.path.join(data_dir, 'tickers.txt')

    try:
        # Ensure directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Save tickers
        with open(ticker_file, 'w') as f:
            for ticker in tickers:
                f.write(f"{ticker}\n")

        print(f"\n✓ Saved {len(tickers)} tickers to {ticker_file}")
        return True
    except Exception as e:
        print(f"\n✗ Failed to save tickers: {type(e).__name__}: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " S&P 500 Ticker Download Test Suite ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    print("\nThis script will test different methods to download S&P 500 tickers")
    print("from Wikipedia and help identify the best approach.")

    # Store results
    results = {}

    # Run all tests
    results['basic'] = test_basic_pandas_read_html()
    results['custom_headers'] = test_pandas_with_custom_headers()
    results['urllib'] = test_urllib_request()
    results['requests'] = test_requests_library()
    results['file'] = test_read_from_file()

    # Summary
    print_section("Summary")

    successful_methods = []
    for method, tickers in results.items():
        if tickers:
            successful_methods.append((method, len(tickers)))
            print(f"✓ {method:20s}: SUCCESS ({len(tickers)} tickers)")
        else:
            print(f"✗ {method:20s}: FAILED")

    # Recommendations
    print_section("Recommendations")

    if successful_methods:
        print("\n✓ At least one method succeeded!")
        best_method = max(successful_methods, key=lambda x: x[1])
        print(f"\nBest method: {best_method[0]} ({best_method[1]} tickers)")

        # Offer to save if we got results from a web method
        if best_method[0] != 'file' and results[best_method[0]]:
            print("\nWould you like to save these tickers to src/data/tickers.txt? (y/n): ", end='')
            try:
                response = input().strip().lower()
                if response == 'y':
                    save_tickers_to_file(results[best_method[0]])
            except (KeyboardInterrupt, EOFError):
                print("\nSkipped saving.")
    else:
        print("\n✗ All methods failed!")
        print("\nPossible solutions:")
        print("1. Install requests library: pip install requests")
        print("2. Check your internet connection")
        print("3. Check if Wikipedia is accessible from your network")
        print("4. Use a VPN if Wikipedia is blocked")
        print("5. Manually download and save tickers to src/data/tickers.txt")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)

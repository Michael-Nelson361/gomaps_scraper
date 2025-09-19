#!/usr/bin/env python3
"""
Google Maps CLI Search Tool
Searches Google Maps using gomaps package and exports results to CSV
"""

import argparse
import csv
import sys
from datetime import datetime
import re
import os

try:
    import gomaps
except ImportError:
    print("Error: gomaps package not installed.")
    print("Please install it using: pip install gomaps")
    sys.exit(1)


def sanitize_filename(filename):
    """
    Sanitize the query string for use in filename
    Replaces spaces with hyphens and removes special characters
    """
    # Replace spaces with hyphens
    filename = filename.replace(' ', '-')
    # Remove or replace special characters
    filename = re.sub(r'[^\w\-]', '', filename)
    # Convert to lowercase for consistency
    filename = filename.lower()
    # Remove multiple consecutive hyphens
    filename = re.sub(r'-+', '-', filename)
    # Remove leading/trailing hyphens
    filename = filename.strip('-')
    return filename


def format_location_query(base_query, zip_code=None, distance=None):
    """
    Format the search query with location parameters if provided
    """
    if zip_code:
        # Construct location-based query
        query = f"{base_query} near {zip_code}"
        if distance:
            # Note: Google Maps doesn't directly support distance in query,
            # but we can append it as context
            query = f"{base_query} within {distance} miles of {zip_code}"
    else:
        query = base_query
    
    return query


def search_places(query, page_num=1, max_results=20):
    """
    Search for places using gomaps and return results
    """
    print(f"Searching for: {query}")
    print("Please wait, this may take a moment...")
    
    try:
        # Perform the search with delay to avoid being blocked
        results = gomaps.maps_search(query, page_num=page_num, delay=5, log=False)
        
        if not results:
            print("No results found.")
            return []
        
        # Populate all values for each result
        populated_results = []
        for i, place in enumerate(results, 1):
            print(f"Processing result {i}/{len(results)}...")
            try:
                place_data = place.get_values()
                populated_results.append(place_data)
            except Exception as e:
                print(f"Warning: Could not get full details for result {i}: {e}")
                # Still include basic info if available
                basic_data = {
                    'title': place.title if hasattr(place, 'title') else '',
                    'url': place.url if hasattr(place, 'url') else '',
                    'coords': place.coords if hasattr(place, 'coords') else ('', ''),
                    'address': '',
                    'website': '',
                    'phone_number': '',
                    'rating': '',
                    'open_hours': {}
                }
                populated_results.append(basic_data)
            
            # Limit results to max_results
            if len(populated_results) >= max_results:
                break
        
        return populated_results
        
    except Exception as e:
        print(f"Error during search: {e}")
        return []


def export_to_csv(results, query_string):
    """
    Export search results to CSV file with datestamp naming
    """
    if not results:
        print("No results to export.")
        return None
    
    # Generate filename with datestamp
    date_stamp = datetime.now().strftime("%Y%m%d")
    sanitized_query = sanitize_filename(query_string)
    filename = f"{date_stamp}_{sanitized_query}.csv"
    
    # Define CSV columns
    fieldnames = [
        'Place Name',
        'Address',
        'Latitude',
        'Longitude',
        'Phone Number',
        'Website',
        'Rating',
        'Google Maps URL',
        'Current Hours Status',
        'Monday Hours',
        'Tuesday Hours',
        'Wednesday Hours',
        'Thursday Hours',
        'Friday Hours',
        'Saturday Hours',
        'Sunday Hours'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Extract coordinates
                coords = result.get('coords', ('', ''))
                lat = coords[0] if coords else ''
                lon = coords[1] if coords else ''
                
                # Extract open hours
                open_hours = result.get('open_hours', {})
                hours_dict = open_hours.get('Hours', {})
                current_status = open_hours.get('Currently', '')
                
                # Create row for CSV
                row = {
                    'Place Name': result.get('title', ''),
                    'Address': result.get('address', ''),
                    'Latitude': lat,
                    'Longitude': lon,
                    'Phone Number': result.get('phone_number', ''),
                    'Website': result.get('website', ''),
                    'Rating': result.get('rating', ''),
                    'Google Maps URL': result.get('url', ''),
                    'Current Hours Status': current_status,
                    'Monday Hours': hours_dict.get('Monday', ''),
                    'Tuesday Hours': hours_dict.get('Tuesday', ''),
                    'Wednesday Hours': hours_dict.get('Wednesday', ''),
                    'Thursday Hours': hours_dict.get('Thursday', ''),
                    'Friday Hours': hours_dict.get('Friday', ''),
                    'Saturday Hours': hours_dict.get('Saturday', ''),
                    'Sunday Hours': hours_dict.get('Sunday', '')
                }
                
                writer.writerow(row)
        
        print(f"\nSuccess! Results exported to: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error writing CSV file: {e}")
        return None


def main():
    """
    Main CLI function
    """
    parser = argparse.ArgumentParser(
        description='Search Google Maps and export results to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "coffee shops"
  %(prog)s "restaurants" --zip 10001
  %(prog)s "hiking trails" --zip 94025 --distance 10
  %(prog)s "pizza" --max-results 50 --page 2
        """
    )
    
    # Required argument
    parser.add_argument(
        'query',
        help='Search query for Google Maps (e.g., "coffee shops", "restaurants")'
    )
    
    # Optional arguments
    parser.add_argument(
        '--zip',
        type=str,
        help='ZIP code to search near (e.g., 10001)'
    )
    
    parser.add_argument(
        '--distance',
        type=int,
        help='Search radius in miles from ZIP code (requires --zip)'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=20,
        help='Maximum number of results to retrieve (default: 20)'
    )
    
    parser.add_argument(
        '--page',
        type=int,
        default=1,
        help='Page number of results to retrieve (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.distance and not args.zip:
        parser.error("--distance requires --zip to be specified")
    
    if args.max_results <= 0:
        parser.error("--max-results must be a positive number")
    
    if args.page <= 0:
        parser.error("--page must be a positive number")
    
    # Format the query with location if provided
    formatted_query = format_location_query(
        args.query,
        zip_code=args.zip,
        distance=args.distance
    )
    
    # Perform the search
    print("\n" + "="*50)
    print("Google Maps Search Tool")
    print("="*50)
    
    results = search_places(
        formatted_query,
        page_num=args.page,
        max_results=args.max_results
    )
    
    if results:
        print(f"\nFound {len(results)} result(s)")
        
        # Export to CSV
        csv_file = export_to_csv(results, args.query)
        
        if csv_file:
            print("\nSummary of results:")
            print("-" * 30)
            for i, result in enumerate(results[:5], 1):  # Show first 5
                print(f"{i}. {result.get('title', 'Unknown')}")
                print(f"   {result.get('address', 'No address available')}")
                if result.get('rating'):
                    print(f"   Rating: {result.get('rating')}/5.0")
                print()
            
            if len(results) > 5:
                print(f"... and {len(results) - 5} more result(s) in the CSV file")
    else:
        print("\nNo results found. Try adjusting your search query.")
    
    print("\n" + "="*50)
    print("Search complete!")
    print("="*50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
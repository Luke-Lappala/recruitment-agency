"""Simple test file for jsearch API."""

import os
import requests
from dotenv import load_dotenv

def test_api():
    """Test the jsearch API connection."""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("RAPID_API_KEY")
    print(f"API key found: {bool(api_key)}")
    print(f"API key length: {len(api_key) if api_key else 0}")
    
    # API endpoint
    url = "https://jsearch.p.rapidapi.com/search"
    
    # Headers with exact casing
    headers = {
        "x-rapidapi-key": "3a88d2a4damsh1769179a8b7e418p1cb1d7jsnaad94fa4bfb0",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    
    # Parameters
    params = {
        "query": "software engineer",
        "page": "1",
        "num_pages": "1"
    }
    
    print("\nMaking API request...")
    print(f"URL: {url}")
    print(f"Headers: {{'x-rapidapi-key': '*****', 'x-rapidapi-host': {headers['x-rapidapi-host']}}}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"\nResponse status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api() 
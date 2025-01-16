"""Test file to verify the API key and subscription."""

import os
import requests
from pathlib import Path

def test_api_key():
    """Test the API key and subscription."""
    print("Testing API key and subscription...")
    
    # Set API key directly
    api_key = "3a88d2a4damsh1769179a8b7e418p1cb1d7jsnaad94fa4bfb0"
    
    print(f"API key found (length: {len(api_key)})")
    print(f"API key value: {api_key}")
    
    # Test API endpoint
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    
    querystring = {
        "query": "software engineer in Seattle, WA",
        "page": "1",
        "num_pages": "1"
    }
    
    print("\nMaking API request...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Query parameters: {querystring}")
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"\nResponse status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nAPI request successful!")
            print(f"Found {len(data.get('data', []))} jobs")
        else:
            print("\nAPI request failed!")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"\nError making API request: {str(e)}")

if __name__ == "__main__":
    test_api_key() 
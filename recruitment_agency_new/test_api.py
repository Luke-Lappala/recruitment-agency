"""Test file to verify RapidAPI connection."""

import os
from dotenv import dotenv_values
import requests
import json
from datetime import datetime
from pathlib import Path

def test_api_connection():
    """Test the RapidAPI connection by making a job search request."""
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if .env file exists
    env_path = Path('.env')
    print(f"\n.env file exists: {env_path.exists()}")
    print(f".env file path: {env_path.absolute()}")
    
    # Load environment variables directly from .env file
    config = dotenv_values(".env")
    api_key = config.get("RAPID_API_KEY")
    
    print(f"\nLoaded API Key: {api_key}")
    
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in .env file")
        
    # API endpoint and parameters
    url = "https://jsearch.p.rapidapi.com/search"
    query = "communications manager in Seattle, WA"
    
    # Request headers
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    # Query parameters
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }
    
    print("\nMaking API request...")
    print(f"Endpoint: {url}")
    print(f"Query: {query}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"\nAPI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Create job_searches directory if it doesn't exist
            os.makedirs("job_searches", exist_ok=True)
            
            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_searches/api_test_results_{timestamp}.json"
            
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"\nResults saved to: {filename}")
            
            # Print first job details
            if data.get("data"):
                job = data["data"][0]
                print("\nFirst Job Found:")
                print(f"Title: {job.get('job_title')}")
                print(f"Company: {job.get('employer_name')}")
                print(f"Location: {job.get('job_city')}, {job.get('job_state')}")
                print(f"Job Type: {job.get('job_employment_type')}")
            else:
                print("No jobs found in response")
        else:
            print(f"API Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {str(e)}")

if __name__ == "__main__":
    test_api_connection() 
"""Basic test file for the recruitment agency."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

def test_job_search():
    """Test the job search functionality."""
    print("Starting job search test...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("RAPID_API_KEY")
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment variables")
    
    # API endpoint and parameters
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query": "internal communications manager in seattle, wa",
        "page": "1",
        "num_pages": "1",
        "date_posted": "today"
    }
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    try:
        print("Making API request...")
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("job_searches", exist_ok=True)
        results_file = f"job_searches/job_search_results_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(response.json(), f, indent=2)
            
        print(f"Results saved to: {results_file}")
        
        # Print first job details
        data = response.json()
        if data.get("data"):
            job = data["data"][0]
            print("\nFirst Job Details:")
            print(f"Title: {job.get('job_title')}")
            print(f"Company: {job.get('employer_name')}")
            print(f"Location: {job.get('job_city')}, {job.get('job_state')}")
            print(f"Type: {job.get('job_employment_type')}")
            print(f"Apply Link: {job.get('job_apply_link')}")
            
            description = job.get('job_description', '')
            if len(description) > 200:
                description = description[:200] + "..."
            print(f"Description: {description}")
        else:
            print("No jobs found in response")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_job_search() 
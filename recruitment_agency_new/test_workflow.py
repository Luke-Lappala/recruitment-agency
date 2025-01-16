"""Test file for the recruitment agency workflow."""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_workflow():
    """Test the recruitment workflow."""
    print("Starting workflow test...")
    print("Searching for jobs...")

    # Get API key from environment variables
    api_key = os.getenv("RAPID_API_KEY")
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment variables")
    print("API key loaded successfully")

    # Set up API request
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query": "internal communications manager in seattle, wa",
        "page": "1",
        "num_pages": "1",
        "date_posted": "today"
    }
    headers = {
        "x-rapidapi-key": "3a88d2a4damsh1769179a8b7e418p1cb1d7jsnaad94fa4bfb0",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    try:
        print(f"Making API request to {url}")
        print(f"Query parameters: {querystring}")
        print(f"Headers: {{'x-rapidapi-key': '*****', 'x-rapidapi-host': {headers['x-rapidapi-host']}}}")
        
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return
            
        data = response.json()
        if data.get("status") == "OK" and data.get("data"):
            jobs = data["data"]
            print(f"Found {len(jobs)} jobs")
            
            # Process first job
            job = jobs[0]
            job_title = job.get("job_title", "")
            company = job.get("employer_name", "")
            job_description = job.get("job_description", "")
            job_type = job.get("job_employment_type", "")
            location = f"{job.get('job_city', '')}, {job.get('job_state', '')}"
            apply_link = job.get("job_apply_link", "")
            
            # Create job match data
            job_match_data = {
                "job_title": job_title,
                "company": company,
                "job_description": job_description,
                "job_type": job_type,
                "location": location,
                "apply_link": apply_link,
                "matched_skills": ["employee engagement", "project management", "internal communications"],
                "match_score": 100.0
            }
            
            # Save job match data
            os.makedirs("job_matches", exist_ok=True)
            company_slug = company.lower().replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            job_match_path = f"job_matches/job_match_{company_slug}_{timestamp}.json"
            
            with open(job_match_path, "w") as f:
                json.dump(job_match_data, f, indent=2)
            print(f"Saved job match data to {job_match_path}")
            
            # Print email details for testing
            print("\nEmail details:")
            print(f"To: lukelappala@gmail.com")
            print(f"Subject: Application for {job_title} position at {company}")
            print("Attachments would include customized resume and cover letter")
            
        else:
            print("No jobs found in the response")
            if response.content:
                print(f"Response content: {response.content.decode()}")
                
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.content.decode()}")

if __name__ == "__main__":
    test_workflow() 
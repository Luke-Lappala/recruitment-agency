"""Tool for searching job postings using the jsearch API."""

from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from datetime import datetime
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

class JobSearcher(BaseTool):
    """Tool for searching job opportunities across multiple roles and locations."""
    
    search_queries: List[Dict[str, str]] = Field(
        ..., description="List of search queries, each containing 'role' and 'location'"
    )
    max_distance: int = Field(
        25, description="Maximum distance in miles from the specified location"
    )
    num_pages: int = Field(
        1, description="Number of pages of results to return per search"
    )
    min_salary: Optional[int] = Field(
        None, description="Minimum salary requirement (annual)"
    )
    date_posted: Optional[str] = Field(
        "today", description="Filter for job posting date: 'today', 'week', 'month', or 'all'"
    )
    employment_types: Optional[List[str]] = Field(
        None, description="List of employment types to filter for (e.g., 'FULLTIME', 'CONTRACTOR', 'PARTTIME')"
    )
    
    def load_processed_jobs(self) -> List[str]:
        """Load the list of previously processed job IDs."""
        processed_jobs_file = Path(__file__).parent / "processed_jobs.json"
        if processed_jobs_file.exists():
            with open(processed_jobs_file, 'r') as f:
                return json.load(f)['processed_jobs']
        return []
    
    def save_processed_job(self, job_id: str):
        """Save a job ID to the processed jobs list."""
        processed_jobs_file = Path(__file__).parent / "processed_jobs.json"
        processed_jobs = self.load_processed_jobs()
        processed_jobs.append(job_id)
        
        with open(processed_jobs_file, 'w') as f:
            json.dump({"processed_jobs": processed_jobs}, f, indent=2)
    
    def create_job_id(self, job: Dict) -> str:
        """Create a unique identifier for a job."""
        return f"{job['title']}_{job['company']}_{job['location']}"
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs based on criteria and remove duplicates."""
        filtered_jobs = []
        processed_jobs = self.load_processed_jobs()
        
        # Keywords that indicate relevant positions
        relevant_keywords = [
            'communications', 'pr', 'public relations', 'content', 'media relations',
            'corporate communications', 'internal communications',
            'external communications', 'strategic communications', 'digital communications'
        ]
        
        for job in jobs:
            title_lower = job.get('title', '').lower()
            desc_lower = job.get('description', '').lower()
            job_id = self.create_job_id(job)
            
            # Skip if job was already processed
            if job_id in processed_jobs:
                continue
            
            # Check if job title or description contains relevant keywords
            is_relevant = any(keyword in title_lower or keyword in desc_lower 
                            for keyword in relevant_keywords)
            
            # Apply employment type filter if specified
            type_match = True
            if self.employment_types and job.get('type'):
                job_type = job.get('type', '').upper()
                type_match = any(emp_type.upper() in job_type 
                               for emp_type in self.employment_types)
            
            # Apply salary filter if specified and salary information is available
            salary_match = True
            if self.min_salary and job.get('salary_min'):
                salary_match = job['salary_min'] >= self.min_salary
            
            if is_relevant and type_match and salary_match:
                filtered_jobs.append(job)
                self.save_processed_job(job_id)
        
        return filtered_jobs

    def run(self) -> str:
        """Search for jobs using the jsearch API across multiple roles and locations."""
        try:
            all_jobs = []
            api_calls = 0
            max_daily_calls = 333  # 10,000 calls per month ≈ 333 per day
            
            for query in self.search_queries:
                # Check API call limit
                if api_calls >= max_daily_calls:
                    break
                    
                # API endpoint and parameters
                url = "https://jsearch.p.rapidapi.com/search"
                
                headers = {
                    "x-rapidapi-key": "3a88d2a4damsh1769179a8b7e418p1cb1d7jsnaad94fa4bfb0",
                    "x-rapidapi-host": "jsearch.p.rapidapi.com"
                }
                
                querystring = {
                    "query": f"{query['role']} in {query['location']}",
                    "page": "1",
                    "num_pages": str(self.num_pages),
                    "date_posted": self.date_posted
                }
                
                response = requests.get(url, headers=headers, params=querystring)
                api_calls += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('data', []):
                        job_data = {
                            "title": job.get('job_title', ''),
                            "company": job.get('employer_name', ''),
                            "description": job.get('job_description', ''),
                            "type": job.get('job_employment_type', ''),
                            "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}",
                            "apply_link": job.get('job_apply_link', ''),
                            "salary_min": job.get('job_min_salary'),
                            "salary_max": job.get('job_max_salary'),
                            "remote": job.get('job_is_remote', False),
                            "posted_at": job.get('job_posted_at_datetime_utc', ''),
                            "search_query": query
                        }
                        all_jobs.append(job_data)
                
                # Add delay between API calls to prevent rate limiting
                time.sleep(1)
            
            # Filter jobs based on criteria
            filtered_jobs = self.filter_jobs(all_jobs)
            
            # Create output directory if it doesn't exist
            output_dir = Path("job_searches")
            output_dir.mkdir(exist_ok=True)
            
            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"job_search_results_{timestamp}.json"
            
            result = {
                "status": "success",
                "jobs_found": len(filtered_jobs),
                "total_searches": len(self.search_queries),
                "api_calls_made": api_calls,
                "jobs": filtered_jobs,
                "results_file": str(output_file)
            }
            
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            
            return json.dumps(result)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e)
            }
            return json.dumps(error_result) 
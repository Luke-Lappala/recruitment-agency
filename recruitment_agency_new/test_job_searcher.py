"""Test file for the JobSearcher tool."""

from job_prospector.tools.JobSearcher import JobSearcher
import json

def test_job_searcher():
    """Test the JobSearcher tool with various search parameters."""
    print("Testing JobSearcher tool...")
    
    # Initialize the tool
    searcher = JobSearcher(
        keywords="internal communications manager",
        location="Seattle, WA",
        max_distance=25,
        num_pages=1
    )
    
    print("\nSearching for jobs...")
    print(f"Keywords: {searcher.keywords}")
    print(f"Location: {searcher.location}")
    print(f"Max distance: {searcher.max_distance} miles")
    print(f"Number of pages: {searcher.num_pages}")
    
    # Execute the search
    result = searcher.run()
    
    try:
        # Parse the JSON result
        result_data = json.loads(result)
        
        if result_data.get("status") == "success":
            print(f"\nFound {result_data['jobs_found']} jobs")
            print(f"Results saved to: {result_data['results_file']}")
            
            # Print details of first few jobs
            print("\nFirst 3 jobs found:")
            for i, job in enumerate(result_data['jobs'][:3], 1):
                print(f"\nJob {i}:")
                print(f"Title: {job['title']}")
                print(f"Company: {job['company']}")
                print(f"Location: {job['location']}")
                print(f"Type: {job['type']}")
                print(f"Apply Link: {job['apply_link']}")
                print("Description preview:", job['description'][:200] + "...")
        else:
            print("\nError in search result:", result)
            
    except json.JSONDecodeError:
        print("\nError: Could not parse result as JSON")
        print("Raw result:", result)
    except Exception as e:
        print(f"\nError processing results: {str(e)}")

if __name__ == "__main__":
    test_job_searcher() 
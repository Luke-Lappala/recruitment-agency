from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import json
import time
import logging
from pathlib import Path
import hashlib
from math import radians, sin, cos, sqrt, atan2

load_dotenv()

logger = logging.getLogger(__name__)

class JobSearcher(BaseTool):
    """
    Tool for searching Communications job opportunities that match Luke's preferences.
    """
    search_terms: list = Field(
        default=[
            # Core Communications Roles
            "internal communications",
            "corporate communications",
            "communications manager",
            "communications specialist",
            "public relations",
            "media relations",
            "PR manager",
            "communications strategist",
            "employee communications",
            "director of communications",
            "communications lead",
            "head of communications",
            # Leadership/Strategic Roles
            "chief communications officer",
            "vp of communications",
            "communications program manager",
            "global communications director",
            # Internal Communications
            "change communications manager",
            "employee engagement specialist",
            "internal communications strategist",
            "culture communications specialist",
            # External/PR Focus
            "communications and public affairs",
            "stakeholder communications",
            "external relations manager",
            "media communications specialist",
            # Content/Digital Focus
            "editorial communications",
            "content strategy and communications",
            "digital communications strategist",
            "multimedia communications",
            # Industry-Specific
            "tech communications specialist",
            "healthcare communications manager",
            "nonprofit communications director",
            "startup communications lead",
            # Additional Role Variations
            "communications director",
            "senior communications manager",
            "communications business partner",
            "strategic communications",
            "content and communications",
            "brand communications",
            "executive communications",
            "digital communications",
            "communications consultant",
            "PR director",
            "PR specialist"
        ], 
        description="Job titles to search for"
    )
    location: str = Field(default="Seattle, WA", description="Location for the job search")
    max_distance: int = Field(default=50, description="Maximum distance in miles for hybrid positions")
    experience_level: str = Field(default="mid", description="Experience level (entry, mid, senior)")
    remote_preference: bool = Field(default=True, description="Whether to prioritize remote positions")
    industry_preferences: list = Field(
        default=[
            "technology",
            "healthcare",
            "nonprofit",
            "media",
            "startup",
            "enterprise",
            "software",
            "biotech",
            "fintech",
            "education"
        ],
        description="Preferred industries for communications roles"
    )
    date_posted_max: int = Field(
        default=7,
        description="Maximum age of job postings in days"
    )
    salary_min: int = Field(
        default=100000,
        description="Minimum salary requirement"
    )
    force_refresh: bool = Field(
        default=False, 
        description="Force a new search even if cached results exist"
    )

    def _calculate_distance(self, job_location):
        """
        Calculate distance between Seattle and job location using Haversine formula.
        Returns distance in miles.
        """
        # Seattle coordinates
        seattle_lat, seattle_lon = 47.6062, -122.3321
        
        try:
            # Extract coordinates from job location
            # Format could be "City, State" or specific coordinates
            if isinstance(job_location, str):
                # Use a geocoding service in production
                # For now, return None if we can't parse exact coordinates
                return None
            
            job_lat = float(job_location.get('latitude', 0))
            job_lon = float(job_location.get('longitude', 0))
            
            # Convert coordinates to radians
            lat1, lon1 = radians(seattle_lat), radians(seattle_lon)
            lat2, lon2 = radians(job_lat), radians(job_lon)
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            # Earth's radius in miles
            r = 3959
            
            return r * c
        except (ValueError, TypeError, KeyError):
            return None

    def _get_cache_path(self):
        """Get the path to the cache file for today's searches."""
        cache_dir = Path("job_searches/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"search_cache_{datetime.now().strftime('%Y%m%d')}.json"

    def _get_request_count_path(self):
        """Get the path to the request counter file for today."""
        cache_dir = Path("job_searches/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"request_count_{datetime.now().strftime('%Y%m%d')}.txt"

    def _get_monthly_request_count_path(self):
        """Get the path to the monthly request counter file."""
        cache_dir = Path("job_searches/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"monthly_request_count_{datetime.now().strftime('%Y%m')}.txt"

    def _increment_request_count(self):
        """Increment and return both daily and monthly request counts."""
        daily_count = self._increment_daily_count()
        monthly_count = self._increment_monthly_count()
        return daily_count, monthly_count

    def _increment_daily_count(self):
        """Increment and return the daily request count."""
        count_path = self._get_request_count_path()
        try:
            if count_path.exists():
                count = int(count_path.read_text())
            else:
                count = 0
            count += 1
            count_path.write_text(str(count))
            return count
        except Exception as e:
            logger.error(f"Error tracking daily request count: {str(e)}")
            return 0

    def _increment_monthly_count(self):
        """Increment and return the monthly request count."""
        count_path = self._get_monthly_request_count_path()
        try:
            if count_path.exists():
                count = int(count_path.read_text())
            else:
                count = 0
            count += 1
            count_path.write_text(str(count))
            return count
        except Exception as e:
            logger.error(f"Error tracking monthly request count: {str(e)}")
            return 0

    def _get_cached_results(self):
        """Get cached search results if they exist and are recent."""
        cache_path = self._get_cache_path()
        if not self.force_refresh and cache_path.exists():
            try:
                cache_data = json.loads(cache_path.read_text())
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                # Check if cache is less than 8 hours old (increased from 4)
                if datetime.now() - cache_time < timedelta(hours=8):
                    logger.info("Using cached search results")
                    return cache_data['results']
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
        return None

    def _save_to_cache(self, results):
        """Save search results to cache."""
        cache_path = self._get_cache_path()
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            cache_path.write_text(json.dumps(cache_data, indent=4))
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")

    def _get_seen_jobs_path(self):
        """Get the path to the file tracking seen job postings."""
        cache_dir = Path("job_searches/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "seen_jobs.json"

    def _load_seen_jobs(self):
        """Load the set of previously seen job IDs."""
        seen_jobs_path = self._get_seen_jobs_path()
        try:
            if seen_jobs_path.exists():
                with open(seen_jobs_path, 'r') as f:
                    seen_jobs = json.load(f)
                    # Convert stored timestamps to datetime objects
                    return {job_id: datetime.fromisoformat(timestamp) 
                           for job_id, timestamp in seen_jobs.items()}
            return {}
        except Exception as e:
            logger.error(f"Error loading seen jobs: {str(e)}")
            return {}

    def _save_seen_jobs(self, seen_jobs):
        """Save the set of seen job IDs."""
        seen_jobs_path = self._get_seen_jobs_path()
        try:
            # Convert datetime objects to ISO format strings for JSON serialization
            seen_jobs_json = {job_id: timestamp.isoformat() 
                            for job_id, timestamp in seen_jobs.items()}
            with open(seen_jobs_path, 'w') as f:
                json.dump(seen_jobs_json, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving seen jobs: {str(e)}")

    def _clean_old_seen_jobs(self, seen_jobs):
        """Remove jobs older than 30 days from seen jobs tracking."""
        current_time = datetime.now()
        return {
            job_id: timestamp
            for job_id, timestamp in seen_jobs.items()
            if current_time - timestamp < timedelta(days=30)
        }

    def _generate_job_id(self, job):
        """Generate a unique ID for a job posting based on its content."""
        # Combine key fields to create a unique identifier
        job_string = f"{job.get('job_title', '')}{job.get('employer_name', '')}{job.get('job_description', '')[:100]}"
        return hashlib.md5(job_string.encode()).hexdigest()

    def _filter_new_jobs(self, jobs):
        """Filter out previously seen jobs and return only new ones."""
        seen_jobs = self._load_seen_jobs()
        
        # Clean up old entries first
        seen_jobs = self._clean_old_seen_jobs(seen_jobs)
        
        new_jobs = []
        current_time = datetime.now()
        
        for job in jobs:
            job_id = self._generate_job_id(job)
            if job_id not in seen_jobs:
                new_jobs.append(job)
                seen_jobs[job_id] = current_time
        
        # Save updated seen jobs
        self._save_seen_jobs(seen_jobs)
        
        logger.info(f"Found {len(new_jobs)} new jobs out of {len(jobs)} total jobs")
        return new_jobs

    def _build_search_groups(self):
        """Build optimized search groups to find relevant positions."""
        # Core role groups
        core_groups = [
            # Senior/Executive level
            "chief communications officer OR vp of communications OR global communications director",
            # Director level
            "communications director OR director of communications OR head of communications OR PR director OR nonprofit communications director",
            # Program/Manager level
            "communications manager OR senior communications manager OR communications lead OR communications business partner OR communications program manager",
            # Internal Communications
            "internal communications OR employee communications OR corporate communications OR executive communications OR change communications manager OR employee engagement specialist OR internal communications strategist OR culture communications specialist",
            # External/PR focus
            "public relations OR PR manager OR PR specialist OR media relations OR external communications OR communications and public affairs OR stakeholder communications OR external relations manager OR media communications specialist",
            # Specialist/Strategist
            "communications specialist OR communications strategist OR strategic communications OR tech communications specialist OR healthcare communications manager",
            # Content/Digital Focus
            "editorial communications OR content strategy and communications OR digital communications strategist OR multimedia communications OR content communications OR digital communications",
            # Additional specialties
            "brand communications OR startup communications lead"
        ]

        # Add industry-specific variations
        industry_groups = []
        for industry in self.industry_preferences:
            industry_query = f"{industry} communications OR {industry} PR"
            industry_groups.append(industry_query)

        return core_groups + industry_groups

    def _build_query_params(self, search_query):
        """Build query parameters with enhanced filtering."""
        # Base query with location and experience
        query = f"{search_query}"
        if self.location:
            # Include broader area for remote/hybrid search
            query += f" in {self.location} OR remote"
        if self.experience_level:
            query += f" {self.experience_level} level"

        # Add salary requirement to query
        if self.salary_min:
            query += f" salary {self.salary_min}+"

        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "date_posted": f"today-{self.date_posted_max}"
        }

        return params

    def _filter_results(self, results):
        """Filter results based on preferences."""
        filtered_results = []
        
        for job in results:
            # Skip if no salary info and salary requirement specified
            if self.salary_min:
                salary_max = job.get('max_salary', 0)
                salary_min = job.get('min_salary', 0)
                if salary_max < self.salary_min and salary_min < self.salary_min:
                    continue

            # Check job posting date
            if self.date_posted_max:
                posted_date = job.get('posted_at')
                if posted_date:
                    try:
                        posted_time = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                        if datetime.now() - posted_time > timedelta(days=self.date_posted_max):
                            continue
                    except (ValueError, AttributeError):
                        pass

            # Check industry match
            job_description = job.get('job_description', '').lower()
            employer_name = job.get('employer_name', '').lower()
            
            industry_match = False
            for industry in self.industry_preferences:
                if (industry.lower() in job_description or 
                    industry.lower() in employer_name):
                    industry_match = True
                    break
            
            if not industry_match:
                continue

            # Check location requirements
            job_type = job.get('job_type', '').lower()
            job_location = job.get('job_location', {})
            
            # Accept any remote position
            if 'remote' in job_type:
                filtered_results.append(job)
                continue
                
            # For hybrid positions, check distance
            if 'hybrid' in job_type:
                distance = self._calculate_distance(job_location)
                # Include if within max distance or if distance couldn't be calculated
                if distance is None or distance <= self.max_distance:
                    filtered_results.append(job)
                continue
            
            # Skip non-remote, non-hybrid positions outside max distance
            distance = self._calculate_distance(job_location)
            if distance is not None and distance <= self.max_distance:
                filtered_results.append(job)

        return filtered_results

    def run(self):
        """
        Searches for jobs using the RapidAPI Jobs API with rate limiting and caching.
        """
        logger.info(f"USE_MOCK_DATA is set to: {os.getenv('USE_MOCK_DATA')}")
        
        if os.getenv("USE_MOCK_DATA", "").lower() == "true":
            logger.info("Using mock data for job search")
            from .mock_data import MOCK_JOB_DATA
            filtered_results = self._filter_results(MOCK_JOB_DATA['data'])
            return self._save_results(filtered_results)

        # Check cache first
        cached_results = self._get_cached_results()
        if cached_results is not None:
            filtered_results = self._filter_results(cached_results)
            return self._save_results(filtered_results)

        try:
            rapid_api_key = os.getenv("RAPID_API_KEY")
            if not rapid_api_key:
                return "Error: RapidAPI key not found in environment variables"

            # Check both daily and monthly limits
            daily_requests, monthly_requests = self._increment_request_count()
            
            if daily_requests > 300:  # Keep daily limit at 300
                logger.warning("Daily API request limit reached")
                return self._handle_limit_reached()
            
            if monthly_requests > 10000:  # Safe monthly limit
                logger.warning("Monthly API request limit approaching")
                return self._handle_limit_reached()

            url = "https://jsearch.p.rapidapi.com/search"
            all_results = []
            
            headers = {
                "X-RapidAPI-Key": rapid_api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }

            search_groups = self._build_search_groups()

            for search_query in search_groups:
                params = self._build_query_params(search_query)

                try:
                    # Increased delay between requests to 20 seconds
                    if all_results:
                        logger.info("Rate limiting: waiting between requests...")
                        time.sleep(20)  # Increased from 15 to 20 seconds
                    
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    
                    if response.status_code == 429:
                        logger.warning("Rate limit hit, waiting longer...")
                        time.sleep(30)
                        response = requests.get(url, headers=headers, params=params, timeout=30)
                    
                    response.raise_for_status()
                    results = response.json()
                    all_results.extend(results.get('data', []))

                except requests.exceptions.RequestException as e:
                    logger.error(f"Error searching for jobs with term '{search_query}': {str(e)}")
                    continue

            filtered_results = self._filter_results(all_results)
            return self._save_results(filtered_results)

        except Exception as e:
            logger.error(f"Error in job search: {str(e)}")
            return f"Error during job search: {str(e)}"

    def _handle_limit_reached(self):
        """Handle when API limits are reached."""
        cached_results = self._get_cached_results()
        if cached_results:
            filtered_results = self._filter_results(cached_results)
            return self._save_results(filtered_results)
        return "Error: API request limit reached. Using cached results if available."

    def _save_results(self, results):
        """Save results to file and return status message."""
        # Filter for new jobs only
        new_jobs = self._filter_new_jobs(results)
        
        if not new_jobs:
            return "No new job postings found since last check."
        
        os.makedirs("job_searches", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_searches/search_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({"data": new_jobs}, f, indent=4)

        return f"Job search completed. Found {len(new_jobs)} new potential communications positions. Results stored in {filename}"

if __name__ == "__main__":
    # Test the tool
    tool = JobSearcher()  # Using default preferences
    print(tool.run()) 
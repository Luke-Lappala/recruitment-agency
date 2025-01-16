"""Job analyzer tool for evaluating job matches."""

import json
import os
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JobAnalyzer:
    """
    Tool for analyzing job matches based on user preferences and skills.
    """
    search_results_file: str
    min_match_score: float = 0.5
    required_skills: list = None
    preferred_skills: list = None
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = [
                "communications",
                "public relations",
                "stakeholder engagement",
                "content strategy",
                "media relations"
            ]
        if self.preferred_skills is None:
            self.preferred_skills = [
                "internal communications",
                "executive communications",
                "crisis communications",
                "digital communications",
                "social media",
                "brand management",
                "corporate communications",
                "change management",
                "employee engagement"
            ]

    def _calculate_match_score(self, job):
        """Calculate match score for a job based on required and preferred skills."""
        score = 0
        total_skills = len(self.required_skills) + len(self.preferred_skills)
        
        # Check job title and description
        job_text = f"{job.get('job_title', '').lower()} {job.get('job_description', '').lower()}"
        
        # Required skills (weighted more heavily)
        for skill in self.required_skills:
            if skill.lower() in job_text:
                score += 2  # Double weight for required skills
                
        # Preferred skills
        for skill in self.preferred_skills:
            if skill.lower() in job_text:
                score += 1
                
        # Normalize score to 0-1 range
        max_possible_score = 2 * len(self.required_skills) + len(self.preferred_skills)
        normalized_score = score / max_possible_score
        
        return round(normalized_score, 2)

    def run(self):
        """
        Analyze job matches from search results.
        """
        try:
            # Read search results
            if not os.path.exists(self.search_results_file):
                return {"error": f"Search results file not found: {self.search_results_file}"}
                
            with open(self.search_results_file, 'r') as f:
                jobs = json.load(f)
                
            if not isinstance(jobs, list):
                return {"error": "Invalid search results format"}
                
            # Analyze each job
            matches = []
            for job in jobs:
                match_score = self._calculate_match_score(job)
                if match_score >= self.min_match_score:
                    job['match_score'] = match_score
                    matches.append(job)
            
            # Sort matches by score
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Save results
            os.makedirs("job_matches", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_matches/matches_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(matches, f, indent=2)
                
            logger.info(f"Found {len(matches)} matches. Results saved to {filename}")
            return {"filename": filename, "match_count": len(matches)}
            
        except Exception as e:
            logger.error(f"Error during job analysis: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the tool with the most recent search results
    search_results_dir = "job_searches"
    if os.path.exists(search_results_dir):
        search_files = [f for f in os.listdir(search_results_dir) if f.startswith("search_results_")]
        if search_files:
            latest_file = max(search_files, key=lambda x: os.path.getctime(os.path.join(search_results_dir, x)))
            analyzer = JobAnalyzer(search_results_file=os.path.join(search_results_dir, latest_file))
            result = analyzer.run()
            print(result) 
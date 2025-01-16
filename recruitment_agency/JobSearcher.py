"""Job search tool for finding relevant positions."""

import json
import os
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JobSearcher:
    """
    Tool for searching job opportunities based on user preferences.
    """
    location: str = "Seattle, WA"
    experience_level: str = "mid"
    remote_preference: bool = True
    industry_preferences: list = None
    max_distance: int = 50
    min_salary: int = 100000

    def __post_init__(self):
        if self.industry_preferences is None:
            self.industry_preferences = ["technology", "healthcare"]

    def run(self):
        """
        Searches for job opportunities based on user preferences.
        """
        try:
            # Mock job data for testing
            mock_jobs = [
                {
                    "employer": "Enterprise Tech Corp",
                    "job_title": "Corporate Communications Director",
                    "job_description": """Lead internal and external communications strategy for a growing technology company. 
                    Key responsibilities include:
                    - Develop and execute communications strategy aligned with business goals
                    - Manage public relations and media relations initiatives
                    - Lead stakeholder engagement and executive communications
                    - Drive content strategy and brand management
                    - Oversee internal communications and employee engagement programs
                    - Crisis communications and reputation management
                    
                    Required skills:
                    - Strong background in communications and public relations
                    - Experience with stakeholder engagement and content strategy
                    - Proven track record in media relations and crisis communications
                    - Digital communications and social media expertise""",
                    "location": "Seattle, WA",
                    "job_type": "hybrid",
                    "posting_date": "2025-01-14",
                    "salary_range": "120,000 - 150,000",
                    "application_link": "https://example.com/jobs/123"
                },
                {
                    "employer": "Tech Company A",
                    "job_title": "Internal Communications Manager",
                    "job_description": """Looking for an experienced internal communications professional to lead employee communications strategy.
                    Key responsibilities:
                    - Develop and execute internal communications strategy
                    - Lead employee engagement and change management initiatives
                    - Create executive communications and thought leadership content
                    - Manage cross-functional collaboration on key programs
                    - Drive content strategy and storytelling
                    - Support DEI communication efforts
                    - Handle crisis communications when needed
                    
                    Required skills:
                    - Strong background in internal communications
                    - Experience with employee engagement and change management
                    - Executive communications and content strategy expertise
                    - Project management and team leadership""",
                    "location": "Seattle, WA",
                    "job_type": "hybrid",
                    "posting_date": "2025-01-14",
                    "salary_range": "110,000 - 140,000",
                    "application_link": "https://example.com/jobs/234"
                },
                {
                    "employer": "Nonprofit Organization",
                    "job_title": "Communications Specialist",
                    "job_description": """Seeking a communications professional to support our mission through effective storytelling and content strategy.
                    Key responsibilities:
                    - Create compelling content across digital channels
                    - Manage social media presence and content calendar
                    - Write press releases and media pitches
                    - Support internal communications initiatives
                    - Develop marketing and communications materials
                    - Assist with stakeholder engagement
                    
                    Required skills:
                    - Experience in communications and content creation
                    - Strong writing and editing skills
                    - Public relations and media relations experience
                    - Social media and digital communications expertise
                    - Internal communications support""",
                    "location": "Seattle, WA",
                    "job_type": "onsite",
                    "posting_date": "2025-01-14",
                    "salary_range": "80,000 - 100,000",
                    "application_link": "https://example.com/jobs/345"
                },
                {
                    "employer": "Healthcare Corp B",
                    "job_title": "PR Manager",
                    "job_description": """Manage public relations and media strategy for a leading healthcare organization.
                    Key responsibilities include:
                    - Develop and implement PR strategies and campaigns
                    - Lead media relations and external communications
                    - Create compelling content and manage social media presence
                    - Support internal communications initiatives
                    - Collaborate with stakeholders across the organization
                    - Handle crisis communications when needed
                    
                    Required skills:
                    - Proven experience in public relations and communications
                    - Strong media relations and stakeholder engagement skills
                    - Content strategy and social media management
                    - Crisis communications experience
                    - Internal communications support""",
                    "location": "Remote",
                    "job_type": "remote",
                    "posting_date": "2025-01-14",
                    "salary_range": "100,000 - 130,000",
                    "application_link": "https://example.com/jobs/456"
                }
            ]

            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_searches/search_results_{timestamp}.json"

            # Save results
            os.makedirs("job_searches", exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(mock_jobs, f, indent=2)

            logger.info(f"Found {len(mock_jobs)} jobs. Results saved to {filename}")
            return {"filename": filename, "job_count": len(mock_jobs)}

        except Exception as e:
            logger.error(f"Error during job search: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the tool
    searcher = JobSearcher()
    result = searcher.run()
    print(result) 
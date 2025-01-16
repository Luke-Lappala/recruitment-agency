"""Job Prospector agent for searching and analyzing job opportunities."""

from agency_swarm import Agent
from recruitment_agency.job_prospector.tools.JobSearcher import JobSearcher
from recruitment_agency.job_prospector.tools.JobAnalyzer import JobAnalyzer

class JobProspector(Agent):
    """Agent responsible for finding and analyzing job opportunities."""
    
    def __init__(self):
        """Initialize the Job Prospector agent."""
        super().__init__(
            name="Job Prospector",
            description="Searches and analyzes job opportunities matching client profiles",
            instructions="./instructions.md",
            tools=[JobSearcher, JobAnalyzer],
            temperature=0.7
        ) 

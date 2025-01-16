"""Main agency file for the recruitment agency."""

from agency_swarm import Agency
from recruitment_agency.account_manager.account_manager import AccountManager
from recruitment_agency.job_prospector.job_prospector import JobProspector
from recruitment_agency.content_writer.content_writer import ContentWriter

def create_agency():
    """Create and configure the recruitment agency."""
    # Initialize agents
    account_manager = AccountManager()
    job_prospector = JobProspector()
    content_writer = ContentWriter()

    # Create agency with communication flows
    agency = Agency(
        [
            account_manager,  # Account Manager is the entry point for communication
            [account_manager, job_prospector],  # Account Manager can communicate with Job Prospector
            [account_manager, content_writer],  # Account Manager can communicate with Content Writer
            [job_prospector, content_writer],  # Job Prospector can communicate with Content Writer
        ],
        shared_instructions="agency_manifesto.md",
        temperature=0.7
    )
    
    return agency

if __name__ == "__main__":
    agency = create_agency()
    agency.run_demo() 
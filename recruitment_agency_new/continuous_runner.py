"""Script to run the job search workflow continuously."""

import time
from datetime import datetime
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_search.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add the project root to Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from test_full_workflow import test_full_workflow

def run_continuous_workflow():
    """Run the job search workflow continuously with appropriate delays."""
    while True:
        try:
            current_time = datetime.now()
            logging.info(f"Starting workflow at {current_time}")
            
            # Run the workflow
            test_full_workflow()
            
            # Wait for 1 hour before next run
            # This means we'll run 24 times per day, well within our API limits
            logging.info("Workflow completed. Waiting for 1 hour before next run...")
            time.sleep(3600)  # 1 hour in seconds
            
        except Exception as e:
            logging.error(f"Error in workflow: {str(e)}")
            logging.info("Waiting 5 minutes before retry...")
            time.sleep(300)  # 5 minutes in seconds

if __name__ == "__main__":
    logging.info("Starting continuous job search runner...")
    run_continuous_workflow() 
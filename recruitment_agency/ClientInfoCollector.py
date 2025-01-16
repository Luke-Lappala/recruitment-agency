"""Client info collector tool for storing job application details."""

import os
import json
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClientInfoCollector:
    """
    Tool for collecting and storing client information.
    """
    def run(self, client_name, client_id, job_match):
        """
        Collects and stores client information.
        """
        try:
            # Create client info object
            client_info = {
                'client_name': client_name,
                'client_id': client_id,
                'job_title': job_match.get('job_title', ''),
                'company': job_match.get('company', ''),
                'application_link': job_match.get('application_link', ''),
                'application_date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'applied'
            }
            
            # Save client info
            os.makedirs("client_info", exist_ok=True)
            filename = f"client_info/{client_name}_{client_id}.json"
            
            with open(filename, 'w') as f:
                json.dump(client_info, f, indent=2)
            
            return {"file_path": filename}
            
        except Exception as e:
            logger.error(f"Error collecting client info: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the tool
    collector = ClientInfoCollector()
    test_job_match = {
        'job_title': 'Communications Director',
        'company': 'Test Corp',
        'application_link': 'https://example.com/jobs/123'
    }
    result = collector.run(
        client_name="Test Client",
        client_id="TEST001",
        job_match=test_job_match
    )
    print(result) 
"""Test file to verify imports."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agency_swarm import Agency, set_openai_key

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from recruitment_agency.job_prospector.tools.JobSearcher import JobSearcher
    print("JobSearcher imported successfully")
except Exception as e:
    print(f"Error importing JobSearcher: {str(e)}")

try:
    from recruitment_agency.job_prospector.tools.JobAnalyzer import JobAnalyzer
    print("JobAnalyzer imported successfully")
except Exception as e:
    print(f"Error importing JobAnalyzer: {str(e)}")

try:
    from recruitment_agency.content_writer.tools.ResumeEditor import ResumeEditor
    print("ResumeEditor imported successfully")
except Exception as e:
    print(f"Error importing ResumeEditor: {str(e)}")

try:
    from recruitment_agency.content_writer.tools.CoverLetterEditor import CoverLetterEditor
    print("CoverLetterEditor imported successfully")
except Exception as e:
    print(f"Error importing CoverLetterEditor: {str(e)}")

try:
    from recruitment_agency.email_sender.tools.EmailSender import EmailSender
    print("EmailSender imported successfully")
except Exception as e:
    print(f"Error importing EmailSender: {str(e)}")

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("OPENAI_API_KEY not found in environment variables")
else:
    print("OPENAI_API_KEY found in environment variables")
    set_openai_key(openai_api_key)
    print("OpenAI API key set successfully") 
"""Test file to verify imports."""

import os
from dotenv import load_dotenv
from agency_swarm import Agency, set_openai_key
from recruitment_agency.account_manager.account_manager import AccountManager

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
set_openai_key(openai_api_key)

print("Agency module imported successfully")
print("Creating Account Manager agent...")
account_manager = AccountManager()
print("Account Manager agent created successfully") 
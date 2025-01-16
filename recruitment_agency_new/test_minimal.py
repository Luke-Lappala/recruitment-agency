"""Minimal test file to verify imports."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_minimal():
    """Test minimal functionality."""
    
    print("Testing minimal functionality...")
    
    # Check environment variables
    sender_password = os.getenv("SENDER_PASSWORD")
    print(f"SENDER_PASSWORD found: {bool(sender_password)}")
    
    # Check file paths
    resume_path = "../customized_documents/resume_tech_company_a_20250114_151851.txt"
    cover_letter_path = "../customized_documents/cover_letter_tech_company_a_20250114_151851.txt"
    
    print(f"\nChecking file paths:")
    print(f"Resume exists: {os.path.exists(resume_path)}")
    print(f"Cover letter exists: {os.path.exists(cover_letter_path)}")

if __name__ == "__main__":
    test_minimal() 
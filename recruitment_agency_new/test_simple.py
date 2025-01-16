"""Simple test file for the recruitment agency workflow."""

import os
from dotenv import load_dotenv
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

# Load environment variables
load_dotenv()

def test_workflow():
    """Test the recruitment workflow with a focus on document customization and email sending."""
    
    print("Testing Recruitment Workflow")
    print("-------------------------\n")
    
    # Job details
    job_title = "Internal Communications Manager"
    company_name = "Tech Company A"
    matching_skills = [
        "Internal Communications",
        "Leadership",
        "Change Management",
        "Content Strategy",
        "Employee Engagement",
        "Project Management"
    ]
    
    # Document paths
    resume_path = "../customized_documents/resume_tech_company_a_20250114_151851.txt"
    cover_letter_path = "../customized_documents/cover_letter_tech_company_a_20250114_151851.txt"
    
    # Check if documents exist
    if not os.path.exists(resume_path) or not os.path.exists(cover_letter_path):
        print(f"Error: Required documents not found:\n{resume_path}\n{cover_letter_path}")
        return
    
    # Check for sender password
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_password:
        print("Error: SENDER_PASSWORD environment variable not found")
        return
    
    print("\nSending application email...")
    email_sender = EmailSender(
        recipient_email="lukelappala@gmail.com",
        subject=f"Application for {job_title} Position at {company_name}",
        body=f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 
My experience aligns well with the requirements, particularly in:

{chr(10).join('- ' + skill for skill in matching_skills)}

Please find attached my resume and cover letter for your review.

Best regards,
Luke Lappala
        """.strip(),
        attachments=[resume_path, cover_letter_path]
    )
    
    try:
        result = email_sender.run()
        print(result)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    test_workflow() 
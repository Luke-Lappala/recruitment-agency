"""Test file for sending application emails with attachments."""

import os
from dotenv import load_dotenv
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

# Load environment variables
load_dotenv()

def send_application():
    """Send an application email with resume and cover letter attachments."""
    
    # Check for sender password
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_password:
        print("Error: SENDER_PASSWORD environment variable not found")
        return
        
    # Set up file paths - using paths relative to root directory
    resume_path = "../customized_documents/resume_tech_company_a_20250114_151851.txt"
    cover_letter_path = "../customized_documents/cover_letter_tech_company_a_20250114_151851.txt"
    
    # Check if files exist
    if not os.path.exists(resume_path) or not os.path.exists(cover_letter_path):
        print(f"Error: One or more files not found:\n{resume_path}\n{cover_letter_path}")
        return
        
    # Initialize EmailSender with required fields
    email_sender = EmailSender(
        recipient_email="lukelappala@gmail.com",
        subject="Application for Internal Communications Manager Position at Tech Company A",
        body="Please find attached my resume and cover letter for the Internal Communications Manager position.",
        attachments=[resume_path, cover_letter_path]
    )
    
    try:
        result = email_sender.run()
        print(result)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    send_application() 
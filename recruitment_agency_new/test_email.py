"""Test file for email sending functionality."""

import os
from dotenv import load_dotenv
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

# Load environment variables
load_dotenv()

def test_email():
    print("Testing Email Sending")
    print("-------------------\n")

    # Check for email password
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_password:
        print("Error: SENDER_PASSWORD not found in environment variables")
        return

    # Initialize email sender
    email_sender = EmailSender()

    # Test sending email with attachments
    try:
        print("Sending test email...")
        email_result = email_sender.run(
            recipient_email="lukelappala@gmail.com",
            subject="Test Email from Recruitment Agency",
            body="This is a test email to verify the email sending functionality.",
            attachments=[
                "customized_documents/resume_tech_company_a_20250114_151851.txt",
                "customized_documents/cover_letter_tech_company_a_20250114_151851.txt"
            ]
        )
        print("Email sending result:", email_result)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    test_email() 
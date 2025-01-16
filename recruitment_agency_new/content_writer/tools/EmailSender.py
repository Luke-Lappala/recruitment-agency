"""Tool for sending job application emails."""

from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

class EmailSender(BaseTool):
    """Tool for sending job application emails."""
    
    job_title: str = Field(
        ..., description="Title of the job position"
    )
    company_name: str = Field(
        ..., description="Name of the company"
    )
    resume_path: str = Field(
        ..., description="Path to the customized resume file"
    )
    cover_letter_path: str = Field(
        ..., description="Path to the customized cover letter file"
    )
    recipient_email: str = Field(
        ..., description="Email address to send the application to"
    )

    def create_email_subject(self):
        """Create the email subject line."""
        return f"Application for {self.job_title} position at {self.company_name}"

    def create_email_body(self):
        """Create the email body text."""
        return f"""Dear Hiring Manager,

Please find attached my resume and cover letter for the {self.job_title} position at {self.company_name}.

Thank you for considering my application.

Best regards,
Luke Lappala"""

    def run(self):
        """Send the job application email."""
        try:
            # Get email credentials from environment
            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")
            
            if not sender_email or not sender_password:
                raise ValueError("Email credentials not found in environment variables")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = self.create_email_subject()
            
            # Add body
            msg.attach(MIMEText(self.create_email_body(), 'plain'))
            
            # Attach resume
            with open(self.resume_path, 'r') as f:
                resume = MIMEText(f.read())
            resume.add_header('Content-Disposition', 'attachment', filename=os.path.basename(self.resume_path))
            msg.attach(resume)
            
            # Attach cover letter
            with open(self.cover_letter_path, 'r') as f:
                cover_letter = MIMEText(f.read())
            cover_letter.add_header('Content-Disposition', 'attachment', filename=os.path.basename(self.cover_letter_path))
            msg.attach(cover_letter)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            return {
                "status": "success",
                "message": f"Application sent to {self.recipient_email}",
                "subject": msg['Subject']
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == "__main__":
    # Test the tool
    sender = EmailSender(
        job_title="Test Position",
        company_name="Test Company",
        resume_path="customized_documents/test_resume.txt",
        cover_letter_path="customized_documents/test_cover_letter.txt",
        recipient_email="test@example.com"
    )
    
    result = sender.run()
    print("Send Result:", result) 
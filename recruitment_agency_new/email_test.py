"""Basic test for email functionality with attachments."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email():
    print("Testing Email Sending with Attachments")
    print("----------------------------------\n")

    # Get email credentials
    sender_email = "south.lake.union.cougar@gmail.com"
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = "lukelappala@gmail.com"

    if not sender_password:
        print("Error: SENDER_PASSWORD not found in environment variables")
        return

    # Define attachments
    attachments = [
        "../customized_documents/resume_tech_company_a_20250114_151851.txt",
        "../customized_documents/cover_letter_tech_company_a_20250114_151851.txt"
    ]

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Test Email with Attachments from Recruitment Agency"

        # Add body
        body = "This is a test email with resume and cover letter attachments."
        msg.attach(MIMEText(body, 'plain'))

        # Add attachments
        for file_path in attachments:
            if os.path.exists(file_path):
                print(f"Attaching file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Create MIME base object
                    part = MIMEBase('application', 'octet-stream')
                    # Read and encode the file content
                    content = f.read()
                    part.set_payload(content.encode('utf-8'))
                    # Encode in base64
                    encoders.encode_base64(part)
                    # Add header
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=os.path.basename(file_path)
                    )
                    msg.attach(part)
            else:
                print(f"Warning: File not found: {file_path}")

        # Send email
        print("\nConnecting to SMTP server...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            print("Logging in...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.send_message(msg)
            print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    test_email() 
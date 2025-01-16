from agency_swarm.tools import BaseTool
from pydantic import Field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class EmailSender(BaseTool):
    """
    Tool for sending customized emails to employers with application materials.
    """
    recipient_email: str = Field(..., description="Email address of the recipient")
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Body content of the email")
    attachments: list = Field(default=[], description="List of file paths to attach")

    def run(self):
        """
        Sends an email with optional attachments using the configured SMTP settings.
        """
        try:
            sender_email = "south.lake.union.cougar@gmail.com"
            sender_password = os.getenv("SENDER_PASSWORD")

            if not sender_password:
                return "Error: Missing email password in environment variables"

            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = self.subject

            # Add body
            msg.attach(MIMEText(self.body, 'plain'))

            # Add attachments
            for file_path in self.attachments:
                if os.path.exists(file_path):
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
                        logger.info(f"Attached file: {file_path}")
                else:
                    logger.warning(f"Attachment not found: {file_path}")

            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                logger.info(f"Email sent with {len(self.attachments)} attachments")

            return f"Email sent successfully to {self.recipient_email}"

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return f"Error sending email: {str(e)}"

if __name__ == "__main__":
    # Test the tool
    tool = EmailSender(
        recipient_email="test@example.com",
        subject="Test Email",
        body="This is a test email.",
        attachments=["path/to/test/file.pdf"]
    )
    print(tool.run()) 
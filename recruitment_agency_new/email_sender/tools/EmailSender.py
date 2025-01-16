"""Tool for sending emails with attachments."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from agency_swarm.tools import BaseTool
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path

class EmailSender(BaseTool):
    """Tool for sending application emails with attachments."""
    
    recipient_email: str = Field(..., description="Email address of the recipient")
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Body text of the email")
    attachments: list = Field(default=[], description="List of file paths to attach")
    job_title: str = Field(..., description="Title of the job position")
    company_name: str = Field(..., description="Name of the company")
    apply_link: str = Field(default="", description="Link to apply for the job")
    
    def create_email_body(self) -> str:
        """Create the email body with application link."""
        body = f"""Dear Hiring Manager,

Please find attached my resume and cover letter for the {self.job_title} position at {self.company_name}.

Job Application Link: {self.apply_link if self.apply_link else 'No direct application link available'}

Best regards,
Luke Lappala"""
        return body
    
    def compress_text_file(self, file_path: str) -> str:
        """Compress text file content by removing unnecessary whitespace."""
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                print(f"Warning: File not found at {abs_path}")
                return file_path
                
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove extra whitespace
            lines = [line.strip() for line in content.split('\n')]
            compressed = '\n'.join(line for line in lines if line)
            
            # Create compressed file in the same directory
            compressed_path = abs_path.replace('.txt', '_compressed.txt')
            with open(compressed_path, 'w', encoding='utf-8') as f:
                f.write(compressed)
            
            return compressed_path
        except Exception as e:
            print(f"Warning: Could not compress file {file_path}: {str(e)}")
            return file_path
    
    def run(self):
        """Send an email with attachments using Gmail SMTP."""
        try:
            # Load environment variables
            load_dotenv()
            sender_password = os.getenv("SENDER_PASSWORD")
            sender_email = "south.lake.union.cougar@gmail.com"
            
            if not sender_password:
                return "Error: SENDER_PASSWORD not found in environment variables"
            
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = self.subject
            
            # Add body text
            msg.attach(MIMEText(self.create_email_body(), 'plain'))
            
            # Add attachments
            compressed_files = []
            for attachment_path in self.attachments:
                try:
                    # Convert to absolute path
                    abs_path = os.path.abspath(attachment_path)
                    if not os.path.exists(abs_path):
                        print(f"Warning: Attachment not found at {abs_path}")
                        continue
                    
                    # Compress text files before attaching
                    if abs_path.endswith('.txt'):
                        abs_path = self.compress_text_file(abs_path)
                        compressed_files.append(abs_path)
                    
                    with open(abs_path, 'rb') as f:
                        attachment = MIMEApplication(f.read(), _subtype='txt')
                        attachment.add_header('Content-Disposition', 'attachment', 
                                           filename=os.path.basename(abs_path))
                        msg.attach(attachment)
                        print(f"Attached file: {abs_path}")
                except Exception as e:
                    print(f"Warning: Could not attach file {attachment_path}: {str(e)}")
            
            # Send email
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
                
                # Clean up compressed files
                for file_path in compressed_files:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                return "Email sent successfully!"
            except Exception as e:
                # Clean up compressed files on error
                for file_path in compressed_files:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                return f"Error sending email: {str(e)}"
                
        except Exception as e:
            return f"Error preparing email: {str(e)}" 
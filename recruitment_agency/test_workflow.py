"""Test file for the recruitment agency workflow."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agency_swarm import Agency, set_openai_key
from recruitment_agency.job_prospector.tools.JobSearcher import JobSearcher
from recruitment_agency.job_prospector.tools.JobAnalyzer import JobAnalyzer
from recruitment_agency.content_writer.tools.ResumeEditor import ResumeEditor
from recruitment_agency.content_writer.tools.CoverLetterEditor import CoverLetterEditor
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
set_openai_key(openai_api_key)

# Check for email password
sender_password = os.getenv("SENDER_PASSWORD")
if not sender_password:
    print("Warning: SENDER_PASSWORD not found in environment variables. Email sending will be disabled.")

def test_workflow():
    # Initialize tools
    job_searcher = JobSearcher()
    job_analyzer = JobAnalyzer()
    resume_editor = ResumeEditor()
    cover_letter_editor = CoverLetterEditor()
    email_sender = EmailSender()

    print("Starting job search...")
    # Search for Python Developer jobs in Seattle
    job_search_result = job_searcher.run(
        job_title="Python Developer",
        location="Seattle, WA",
        max_distance=25
    )
    print("Job search completed.")

    print("\nAnalyzing job requirements...")
    # Analyze job requirements
    job_description = """
    Senior Python Developer at TechCorp
    Key Requirements:
    - 5+ years Python development experience
    - Strong knowledge of web frameworks (Django, Flask)
    - Experience with cloud platforms (AWS, Azure)
    - Database expertise (PostgreSQL, MongoDB)
    - CI/CD pipeline experience
    """
    candidate_skills = [
        "Python development (7 years)",
        "Django and Flask frameworks",
        "AWS and Azure cloud platforms",
        "PostgreSQL and MongoDB",
        "Jenkins and GitLab CI"
    ]

    analysis_result = job_analyzer.run(
        job_description=job_description,
        candidate_skills=candidate_skills
    )
    print("Job analysis completed.")

    if analysis_result.get("is_match", False):
        print("\nCustomizing resume...")
        # Customize resume
        resume_result = resume_editor.run(
            job_title="Senior Python Developer",
            company_name="TechCorp",
            key_requirements=[
                "Python development",
                "Web frameworks",
                "Cloud platforms",
                "Database expertise",
                "CI/CD experience"
            ]
        )
        print("Resume customization completed.")

        print("\nCreating cover letter...")
        # Create cover letter
        cover_letter_result = cover_letter_editor.run(
            job_title="Senior Python Developer",
            company_name="TechCorp",
            company_info="Leading technology solutions provider",
            key_requirements=[
                "Python development",
                "Web frameworks",
                "Cloud platforms",
                "Database expertise",
                "CI/CD experience"
            ]
        )
        print("Cover letter creation completed.")

        if sender_password:
            print("\nSending application email...")
            try:
                # Send email with attachments
                email_result = email_sender.run(
                    recipient_email="lukelappala@gmail.com",
                    subject="Application for Senior Python Developer Position at TechCorp",
                    body="Please find attached my customized resume and cover letter for the Senior Python Developer position at TechCorp.",
                    attachments=[resume_result["file_path"], cover_letter_result["file_path"]]
                )
                print("Email sending result:", email_result)
            except Exception as e:
                print(f"Error sending email: {str(e)}")
        else:
            print("\nSkipping email sending - SENDER_PASSWORD not set")

    else:
        print("\nJob requirements do not match candidate skills.")

if __name__ == "__main__":
    test_workflow() 
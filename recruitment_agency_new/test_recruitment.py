"""Test file for the recruitment agency workflow."""

import os
from dotenv import load_dotenv
from recruitment_agency.job_prospector.tools.JobSearcher import JobSearcher
from recruitment_agency.job_prospector.tools.JobAnalyzer import JobAnalyzer
from recruitment_agency.content_writer.tools.ResumeEditor import ResumeEditor
from recruitment_agency.content_writer.tools.CoverLetterEditor import CoverLetterEditor
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Check for email password
sender_password = os.getenv("SENDER_PASSWORD")
if not sender_password:
    print("Warning: SENDER_PASSWORD not found in environment variables. Email sending will be disabled.")

def test_workflow():
    print("Testing Recruitment Workflow")
    print("-------------------------\n")

    # Initialize tools
    job_searcher = JobSearcher()
    job_analyzer = JobAnalyzer()
    resume_editor = ResumeEditor()
    cover_letter_editor = CoverLetterEditor()
    email_sender = EmailSender()

    print("Searching for jobs...")
    # Search for Internal Communications Manager jobs in Seattle
    job_search_result = job_searcher.run(
        job_title="Internal Communications Manager",
        location="Seattle, WA",
        max_distance=25
    )
    print("Search result:", job_search_result)

    print("\nAnalyzing job requirements...")
    # Analyze job requirements
    job_description = """
    Internal Communications Manager at Tech Company A
    Key Requirements:
    - 5+ years experience in internal communications
    - Strong leadership and stakeholder management skills
    - Experience with change management communications
    - Content strategy and employee engagement expertise
    - Project management skills
    """
    candidate_skills = [
        "Internal Communications (12 years)",
        "Leadership",
        "Change Management",
        "Content Strategy",
        "Employee Engagement",
        "Project Management"
    ]

    analysis_result = job_analyzer.run(
        job_description=job_description,
        candidate_skills=candidate_skills
    )
    print("Analysis result:", analysis_result)

    if analysis_result.get("is_match", False):
        print("\nCustomizing resume...")
        # Customize resume
        resume_result = resume_editor.run(
            job_title="Internal Communications Manager",
            company_name="Tech Company A",
            key_requirements=[
                "Internal Communications",
                "Leadership",
                "Change Management",
                "Content Strategy",
                "Employee Engagement"
            ]
        )
        print("Resume result:", resume_result)

        print("\nCreating cover letter...")
        # Create cover letter
        cover_letter_result = cover_letter_editor.run(
            job_title="Internal Communications Manager",
            company_name="Tech Company A",
            company_info="Leading technology company focused on innovation",
            key_requirements=[
                "Internal Communications",
                "Leadership",
                "Change Management",
                "Content Strategy",
                "Employee Engagement"
            ]
        )
        print("Cover letter result:", cover_letter_result)

        if sender_password:
            print("\nSending application email...")
            try:
                # Send email with attachments
                email_result = email_sender.run(
                    recipient_email="lukelappala@gmail.com",
                    subject="Application for Internal Communications Manager Position at Tech Company A",
                    body="Please find attached my customized resume and cover letter for the Internal Communications Manager position at Tech Company A.",
                    attachments=[resume_result["file_path"], cover_letter_result["file_path"]]
                )
                print("Email sending result:", email_result)
            except Exception as e:
                print(f"Error sending email: {str(e)}")
        else:
            print("\nSkipping email sending - SENDER_PASSWORD not set")

    else:
        print("\nJob requirements do not match candidate skills.")

    print("\nWorkflow test completed!")

if __name__ == "__main__":
    test_workflow() 
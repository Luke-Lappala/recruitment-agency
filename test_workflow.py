"""Test file for the recruitment agency workflow."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import json

# Add parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from recruitment_agency.job_prospector.tools.JobSearcher import JobSearcher
from recruitment_agency.job_prospector.tools.JobAnalyzer import JobAnalyzer
from recruitment_agency.content_writer.tools.ResumeEditor import ResumeEditor
from recruitment_agency.content_writer.tools.CoverLetterEditor import CoverLetterEditor
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

def test_workflow():
    """Test the full recruitment workflow."""
    print("Starting workflow test...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize tools
    job_searcher = JobSearcher(
        keywords="Internal Communications Manager",
        location="Seattle, WA",
        max_distance=25,
        num_pages=1
    )
    
    job_analyzer = JobAnalyzer()
    
    print("\nSearching for jobs...")
    search_results = job_searcher.run()
    print("Search Results:")
    print(search_results)
    
    if search_results.get("jobs"):
        for job in search_results["jobs"]:
            print(f"\nAnalyzing job: {job['title']} at {job['company']}")
            
            analysis_result = job_analyzer.run(
                job_title=job["title"],
                job_description=job["description"],
                company_name=job["company"]
            )
            
            print(f"Analysis Result: {analysis_result}")
            
            if analysis_result.get("is_match"):
                print(f"\nGood match found! Customizing documents for {job['title']} at {job['company']}")
                
                # Create timestamp for file names
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                company_name_slug = job["company"].lower().replace(" ", "_")
                
                # Create paths for customized documents
                resume_path = f"customized_documents/resume_{company_name_slug}_{timestamp}.txt"
                cover_letter_path = f"customized_documents/cover_letter_{company_name_slug}_{timestamp}.txt"
                
                # Ensure customized_documents directory exists
                os.makedirs("customized_documents", exist_ok=True)
                
                # Save job match data for document customization
                job_match_data = {
                    "job_title": job["title"],
                    "company": job["company"],
                    "job_description": job["description"],
                    "matched_skills": analysis_result["matching_skills"],
                    "application_link": job["apply_link"]
                }
                
                job_match_path = f"job_matches/job_match_{company_name_slug}_{timestamp}.json"
                os.makedirs("job_matches", exist_ok=True)
                
                with open(job_match_path, "w") as f:
                    json.dump([job_match_data], f, indent=2)
                
                # Initialize document editors with required paths
                resume_editor = ResumeEditor(
                    template_path="templates/luke_templates.json",
                    job_match_path=job_match_path
                )
                
                cover_letter_editor = CoverLetterEditor(
                    template_path="templates/luke_templates.json",
                    job_match_path=job_match_path
                )
                
                # Customize resume and cover letter
                resume_result = resume_editor.run()
                cover_letter_result = cover_letter_editor.run()
                
                print(f"Resume saved to: {resume_path}")
                print(f"Cover letter saved to: {cover_letter_path}")
                
                # Send application email
                if os.path.exists(resume_path) and os.path.exists(cover_letter_path):
                    email_sender = EmailSender(
                        recipient_email="lukelappala@gmail.com",
                        subject=f"Application for {job['title']} position at {job['company']}",
                        body=f"Dear Hiring Manager,\n\nPlease find attached my application materials for the {job['title']} position at {job['company']}.\n\nBest regards,\nLuke Lappala",
                        attachments=[resume_path, cover_letter_path]
                    )
                    
                    try:
                        email_result = email_sender.run()
                        print(f"Email sent successfully: {email_result}")
                    except Exception as e:
                        print(f"Error sending email: {str(e)}")
                else:
                    print("Error: Could not find customized documents")
            else:
                print("Not a good match, skipping document customization")
    else:
        print("No jobs found")

if __name__ == "__main__":
    test_workflow() 
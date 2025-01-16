"""Full test file for the recruitment agency workflow."""

import os
from pathlib import Path
from dotenv import load_dotenv
from recruitment_agency.email_sender.tools.EmailSender import EmailSender

# Load environment variables
load_dotenv()

def test_full_workflow():
    """Test the complete recruitment workflow."""
    
    print("Testing Full Recruitment Workflow")
    print("-----------------------------\n")
    
    # Job details for testing
    job_title = "Internal Communications Manager"
    company_name = "Tech Company A"
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
    
    print("Job Analysis:")
    print(f"Title: {job_title}")
    print(f"Company: {company_name}")
    print("\nCandidate Skills:")
    for skill in candidate_skills:
        print(f"- {skill}")
    
    # Calculate match score (simplified version)
    required_skills = [
        "Internal Communications",
        "Leadership",
        "Change Management",
        "Content Strategy",
        "Employee Engagement",
        "Project Management"
    ]
    
    matching_skills = [skill.split(" (")[0] for skill in candidate_skills]
    match_score = len(set(matching_skills) & set(required_skills)) / len(required_skills) * 100
    
    print(f"\nMatch Score: {match_score}%")
    
    if match_score >= 80:
        print("\nGood match found! Customizing documents...")
        
        # Generate filenames with timestamp
        timestamp = Path(__file__).stem
        company_name_slug = company_name.lower().replace(" ", "_")
        resume_path = f"../customized_documents/resume_{company_name_slug}_{timestamp}.txt"
        cover_letter_path = f"../customized_documents/cover_letter_{company_name_slug}_{timestamp}.txt"
        
        # Create resume content
        resume_content = f"""LUKE LAPPALA
Director of Communications

PROFESSIONAL EXPERIENCE
- 12+ years of experience in internal communications and employee engagement
- Led strategic communications initiatives for major organizational changes
- Developed and implemented content strategies across multiple channels
- Strong track record in stakeholder management and project leadership

SKILLS & EXPERTISE
{chr(10).join('- ' + skill for skill in matching_skills)}

EDUCATION
Master's in Communications
Bachelor's in Business Administration"""
        
        # Create cover letter content
        cover_letter_content = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With over 12 years of experience in internal communications and a proven track record in employee engagement, I am confident in my ability to contribute significantly to your organization.

My experience aligns perfectly with your requirements:

{chr(10).join('- ' + skill for skill in matching_skills)}

I am particularly drawn to {company_name}'s commitment to innovation and employee engagement. My background in leading change management communications and developing comprehensive content strategies would enable me to make an immediate impact in this role.

Thank you for considering my application. I look forward to discussing how my skills and experience align with your needs.

Best regards,
Luke Lappala"""
        
        # Save documents
        os.makedirs("../customized_documents", exist_ok=True)
        
        with open(resume_path, "w") as f:
            f.write(resume_content)
        print(f"Resume saved to: {resume_path}")
        
        with open(cover_letter_path, "w") as f:
            f.write(cover_letter_content)
        print(f"Cover letter saved to: {cover_letter_path}")
        
        # Send application email
        sender_password = os.getenv("SENDER_PASSWORD")
        if sender_password:
            print("\nSending application email...")
            email_sender = EmailSender(
                recipient_email="lukelappala@gmail.com",
                subject=f"Application for {job_title} Position at {company_name}",
                body=f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 
My experience aligns well with your requirements, particularly in:

{chr(10).join('- ' + skill for skill in matching_skills)}

Please find attached my resume and cover letter for your review.

Best regards,
Luke Lappala""".strip(),
                attachments=[resume_path, cover_letter_path]
            )
            
            try:
                result = email_sender.run()
                print(result)
            except Exception as e:
                print(f"Error sending email: {str(e)}")
        else:
            print("\nSkipping email send - SENDER_PASSWORD not set")
    else:
        print("\nNot a good match. No documents customized.")

if __name__ == "__main__":
    test_full_workflow() 
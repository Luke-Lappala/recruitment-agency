"""Test file for the recruitment agency workflow."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agency_swarm import Agency, set_openai_key

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from recruitment_agency.email_sender.tools.EmailSender import EmailSender
from recruitment_agency.job_prospector.job_prospector import JobProspector
from recruitment_agency.content_writer.content_writer import ContentWriter

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
set_openai_key(openai_api_key)

print("Environment test completed successfully")

# Test job analysis workflow
print("\nTesting job analysis workflow...")

# Extract skills from templates
job_prospector = JobProspector()
skills = job_prospector.tools[0].extract_skills_from_templates()
print(f"Extracted {len(skills)} skills from templates")

# Test job analysis for multiple positions
jobs = [
    {
        "employer": "Tech Company A",
        "job_title": "Internal Communications Manager",
        "job_description": """
        Key responsibilities:
        - Develop and execute internal communications strategy
        - Create engaging content for employee communications
        - Support change management initiatives
        - Manage internal communication channels
        
        Required skills:
        - Strategic Communications
        - Employee Engagement
        - Change Management
        - Content Creation
        - Project Management
        """
    },
    {
        "employer": "Healthcare Corp B",
        "job_title": "PR Manager",
        "job_description": """
        Key responsibilities:
        - Lead media relations and PR campaigns
        - Develop communications strategies
        - Manage crisis communications
        - Create compelling content
        
        Required skills:
        - Public Relations
        - Media Relations
        - Crisis Communications
        - Content Strategy
        - Stakeholder Management
        """
    },
    {
        "employer": "Enterprise Tech Corp",
        "job_title": "Corporate Communications Director",
        "job_description": """
        Key responsibilities:
        - Lead corporate communications strategy
        - Manage executive communications
        - Drive PR and media relations
        - Oversee internal communications
        
        Required skills:
        - Corporate Communications
        - Executive Communications
        - Public Relations
        - Strategic Planning
        - Team Leadership
        """
    },
    {
        "employer": "Nonprofit Organization",
        "job_title": "Communications Specialist",
        "job_description": """
        Key responsibilities:
        - Create content for multiple channels
        - Manage social media presence
        - Support PR initiatives
        - Assist with internal communications
        
        Required skills:
        - Content Creation
        - Social Media Management
        - Public Relations
        - Internal Communications
        - Project Management
        """
    }
]

content_writer = ContentWriter()

for job in jobs:
    print(f"\nAnalyzing job: {job['job_title']} at {job['employer']}")
    
    # Analyze job requirements
    analysis_result = job_prospector.tools[1].analyze_job_requirements(
        job['job_description'],
        skills
    )
    
    if analysis_result['is_match']:
        print(f"Good match! Score: {analysis_result['match_score']:.2f}")
        print("Matching skills:", ", ".join(analysis_result['matching_skills']))
        print("Key requirements:", ", ".join(analysis_result['key_requirements']))
        
        # Customize documents
        resume_path = f"customized_documents/resume_{job['employer'].lower().replace(' ', '_')}_{job['job_title'].lower().replace(' ', '_')}.txt"
        cover_letter_path = f"customized_documents/cover_letter_{job['employer'].lower().replace(' ', '_')}_{job['job_title'].lower().replace(' ', '_')}.txt"
        
        # Create customized documents
        content_writer.tools[0].customize_resume(
            job_title=job['job_title'],
            company=job['employer'],
            key_requirements=analysis_result['key_requirements'],
            output_path=resume_path
        )
        
        content_writer.tools[1].customize_cover_letter(
            job_title=job['job_title'],
            company=job['employer'],
            key_requirements=analysis_result['key_requirements'],
            output_path=cover_letter_path
        )
        
        print(f"Created customized resume: {resume_path}")
        print(f"Created customized cover letter: {cover_letter_path}")
        
        # Send email with attachments
        email_sender = EmailSender(
            recipient_email="lukelappala@gmail.com",
            subject=f"Application for {job['job_title']} position at {job['employer']}",
            body=f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job['job_title']} position at {job['employer']}. With over 12 years of experience in strategic communication and a proven track record in {', '.join(analysis_result['matching_skills'][:3])}, I am confident in my ability to contribute to your team.

Please find my customized resume and cover letter attached.

Best regards,
Luke Lappala""",
            attachments=[resume_path, cover_letter_path]
        )
        
        email_result = email_sender.run()
        print(f"Email result: {email_result}")
    else:
        print(f"Not a good match. Score: {analysis_result['match_score']:.2f}")

print("\nAll tests completed successfully")
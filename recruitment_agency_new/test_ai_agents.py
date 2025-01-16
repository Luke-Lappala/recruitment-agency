"""Test file for AI agents in the recruitment agency."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agency_swarm import Agency, set_openai_key

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import agents
from recruitment_agency_new.job_prospector.job_prospector import JobProspector
from recruitment_agency_new.content_writer.content_writer import ContentWriter

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
set_openai_key(openai_api_key)

print("Environment test completed successfully")

# Initialize agents
job_prospector = JobProspector()
content_writer = ContentWriter()

print("\nTesting job analysis workflow...")

# Test job description
job_description = """
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

# Test job details
job_title = "Internal Communications Manager"
company = "Tech Company A"

print("\nTest data:")
print("Job title:", job_title)
print("Company:", company)
print("Job description:", job_description)

# Extract skills from templates
skills = job_prospector.tools[0].extract_skills_from_templates()
print(f"\nExtracted {len(skills)} skills from templates")

# Analyze job requirements
analysis_result = job_prospector.tools[1].analyze_job_requirements(
    job_description=job_description,
    candidate_skills=skills
)

print("\nJob Analysis Results:")
print(f"Match score: {analysis_result['match_score']:.2f}")
print("Matching skills:", ", ".join(analysis_result['matching_skills']))
print("Key requirements:", ", ".join(analysis_result['key_requirements']))

if analysis_result['is_match']:
    print("\nGood match! Customizing documents...")
    
    # Customize documents
    resume_path = f"customized_documents/resume_{company.lower().replace(' ', '_')}_{job_title.lower().replace(' ', '_')}.txt"
    cover_letter_path = f"customized_documents/cover_letter_{company.lower().replace(' ', '_')}_{job_title.lower().replace(' ', '_')}.txt"
    
    # Create customized documents
    content_writer.tools[0].customize_resume(
        job_title=job_title,
        company=company,
        key_requirements=analysis_result['key_requirements'],
        output_path=resume_path
    )
    
    content_writer.tools[1].customize_cover_letter(
        job_title=job_title,
        company=company,
        key_requirements=analysis_result['key_requirements'],
        output_path=cover_letter_path
    )
    
    print(f"Created customized resume: {resume_path}")
    print(f"Created customized cover letter: {cover_letter_path}")
else:
    print("\nNot a good match. Skipping document customization.")

print("\nAll tests completed successfully") 
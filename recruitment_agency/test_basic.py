"""Basic test file for the recruitment agency."""

import os
from dotenv import load_dotenv
from agency_swarm import Agency, set_openai_key

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
set_openai_key(openai_api_key)

# Test job description and candidate skills
job_description = """
Internal Communications Manager at Tech Company A
Key Responsibilities:
- Develop and execute internal communications strategies
- Create and manage employee engagement initiatives
- Lead change management communications
- Oversee content creation for internal channels
- Project manage communications initiatives

Required Skills:
- Strategic Communications
- Employee Engagement
- Change Management
- Content Creation
- Project Management
- Internal Communications
- Leadership
- Stakeholder Management
- Digital Communications
"""

candidate_skills = [
    "Strategic Communications",
    "Employee Engagement",
    "Change Management",
    "Content Creation",
    "Project Management",
    "Internal Communications"
]

# Calculate match score
requirements = [
    "Strategic Communications",
    "Employee Engagement",
    "Change Management",
    "Content Creation",
    "Project Management",
    "Internal Communications",
    "Leadership",
    "Stakeholder Management",
    "Digital Communications",
    "Communication Strategy"
]

matching_skills = [skill for skill in candidate_skills if skill in requirements]
match_score = len(matching_skills) / len(requirements)

print("Job Description:")
print(job_description)
print("\nCandidate Skills:")
print(candidate_skills)
print("\nMatching Skills:")
print(matching_skills)
print(f"\nMatch Score: {match_score:.2f}") 
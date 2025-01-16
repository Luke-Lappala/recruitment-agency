"""Tool for analyzing job requirements and matching with candidate skills."""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict, Any
import re
import json
from datetime import datetime
import os
from pathlib import Path

class JobAnalyzer(BaseTool):
    """Tool for analyzing job requirements and matching with candidate skills."""
    
    job_title: str = Field(..., description="Title of the job posting")
    company_name: str = Field(..., description="Name of the hiring company")
    job_description: str = Field(..., description="Full text of the job description")
    candidate_skills: List[str] = Field(
        default=[
            "Internal Communications",
            "Content Strategy",
            "Project Management",
            "Leadership",
            "Team Management",
            "Strategic Planning",
            "Crisis Communications",
            "Employee Engagement",
            "Digital Communications",
            "Change Management",
            "Executive Communications",
            "Corporate Communications",
            "Media Relations",
            "Public Relations",
            "Stakeholder Management",
            "Brand Management",
            "Social Media Strategy",
            "Marketing Communications",
            "Event Planning",
            "Budget Management"
        ],
        description="List of candidate's skills to match against job requirements"
    )

    def extract_requirements(self) -> List[str]:
        """Extract key requirements from job description."""
        requirements = []
        
        # Split description into sections
        sections = self.job_description.split('\n\n')
        
        # Look for sections that likely contain requirements
        requirement_indicators = [
            'we are looking for',
            'requirements',
            'qualifications',
            'required',
            'must have',
            'skills',
            'experience'
        ]
        
        # Keywords that indicate a requirement
        requirement_keywords = [
            'experience',
            'knowledge',
            'ability',
            'skill',
            'proficiency',
            'expertise',
            'background',
            'understanding',
            'demonstrated',
            'proven',
            'required',
            'must have'
        ]
        
        for section in sections:
            section_lower = section.lower()
            
            # Check if this section contains requirements
            if any(indicator in section_lower for indicator in requirement_indicators):
                # Split by bullet points or newlines
                lines = section.split('\n')
                for line in lines:
                    # Clean up the line
                    line = line.strip()
                    # Remove bullet points and other markers
                    line = re.sub(r'^[\u2022\-\*]\s*', '', line)
                    
                    # Skip empty lines or very short ones
                    if len(line) < 10:
                        continue
                    
                    # Skip lines that are likely headers
                    if line.endswith(':') or line.isupper():
                        continue
                    
                    # Skip lines that are likely not requirements
                    if any(skip in line.lower() for skip in ['apply', 'www.', 'http', '@', 'salary', 'contact', 'equal opportunity']):
                        continue
                    
                    # Check if line contains requirement keywords
                    if any(keyword in line.lower() for keyword in requirement_keywords):
                        requirements.append(line)
        
        # If no requirements found in sections, try to extract from bullet points
        if not requirements:
            bullet_points = re.findall(r'[\u2022\-\*]\s*([^\n]+)', self.job_description)
            for point in bullet_points:
                point = point.strip()
                if len(point) > 10 and any(keyword in point.lower() for keyword in requirement_keywords):
                    requirements.append(point)
        
        # Clean up requirements
        cleaned_reqs = []
        for req in requirements:
            # Remove common prefixes
            req = re.sub(r'^(must have|should have|required|preferred|you have|you will have|including|such as)\s*', '', req)
            # Remove extra whitespace
            req = ' '.join(req.split())
            # Extract key phrases
            if len(req) > 100:  # If requirement is too long, try to extract key phrase
                key_phrases = []
                for keyword in requirement_keywords:
                    if keyword in req.lower():
                        # Extract phrase around keyword
                        match = re.search(f'.{{0,50}}{keyword}.{{0,50}}', req, re.IGNORECASE)
                        if match:
                            key_phrases.append(match.group(0).strip())
                if key_phrases:
                    cleaned_reqs.extend(key_phrases)
            else:
                cleaned_reqs.append(req)
        
        # Remove duplicates while preserving order
        seen = set()
        final_reqs = []
        for req in cleaned_reqs:
            req_lower = req.lower()
            if req_lower not in seen and len(req) > 10:
                # Skip if too similar to existing requirement
                if not any(self.calculate_similarity(req_lower, existing.lower()) > 0.8 for existing in final_reqs):
                    seen.add(req_lower)
                    final_reqs.append(req)
        
        return final_reqs[:10]  # Return top 10 most relevant requirements

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        # Convert to lowercase for comparison
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Create word sets
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0

    def find_matching_skills(self, requirements: List[str]) -> List[str]:
        """Find candidate skills that match job requirements."""
        matching_skills = []
        
        for skill in self.candidate_skills:
            skill_lower = skill.lower()
            # Check if skill directly matches any requirement
            for req in requirements:
                req_lower = req.lower()
                similarity = self.calculate_similarity(skill, req)
                # Lower the similarity threshold and check for partial matches
                if similarity > 0.2 or skill_lower in req_lower or any(word in req_lower for word in skill_lower.split()):
                    matching_skills.append(skill)
                    break
        
        return list(set(matching_skills))  # Remove duplicates

    def calculate_match_score(self, matching_skills: List[str], requirements: List[str]) -> float:
        """Calculate a match score based on matching skills and requirements."""
        if not requirements:
            return 0.0
        
        # Base score on number of matching skills relative to requirements
        base_score = (len(matching_skills) / len(requirements)) * 100
        
        # Adjust score based on job title relevance
        title_lower = self.job_title.lower()
        title_keywords = [
            'communications', 'pr', 'public relations', 'content', 'media',
            'internal', 'corporate', 'strategic', 'marketing', 'digital',
            'manager', 'director', 'specialist', 'lead', 'head'
        ]
        # Count how many relevant keywords are in the title
        title_relevance = sum(1 for keyword in title_keywords if keyword in title_lower)
        
        # Apply stronger multiplier based on title relevance
        multiplier = 1.0 + (title_relevance * 0.2)  # Each relevant keyword adds 20% to the multiplier
        final_score = base_score * multiplier
        
        # Cap at 100
        return min(final_score, 100.0)

    def run(self) -> Dict[str, Any]:
        """Analyze job requirements and match with candidate skills."""
        try:
            # Extract requirements from job description
            requirements = self.extract_requirements()
            
            # Find matching skills
            matching_skills = self.find_matching_skills(requirements)
            
            # Calculate match score
            match_score = self.calculate_match_score(matching_skills, requirements)
            
            # Create output directory if it doesn't exist
            output_dir = Path("job_matches")
            output_dir.mkdir(exist_ok=True)
            
            # Create safe filename from company name
            company_name_safe = re.sub(r'[^\w\s-]', '', self.company_name.lower())
            company_name_safe = re.sub(r'[-\s]+', '_', company_name_safe)
            
            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"job_match_{company_name_safe}_{timestamp}.json"
            
            result = {
                "status": "success",
                "job_title": self.job_title,
                "company_name": self.company_name,
                "match_score": match_score,
                "matching_skills": matching_skills,
                "key_requirements": requirements,
                "results_file": str(output_file)
            }
            
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            print(f"Error in JobAnalyzer: {str(e)}")
            return {
                "status": "error",
                "job_title": self.job_title,
                "company_name": self.company_name,
                "match_score": 0.0,
                "matching_skills": [],
                "key_requirements": [],
                "message": str(e)
            }

if __name__ == "__main__":
    # Test the tool
    test_description = """
    We are seeking a Communications Manager with:
    - Strong writing and editing skills
    - Experience with social media management
    - Public relations background
    - Team leadership experience
    
    Required skills:
    - Content strategy
    - Crisis communications
    - Stakeholder management
    """
    
    test_skills = [
        "Content Strategy",
        "Social Media Management",
        "Public Relations",
        "Crisis Communications",
        "Team Leadership"
    ]
    
    analyzer = JobAnalyzer(
        job_description=test_description,
        candidate_skills=test_skills
    )
    
    result = analyzer.run()
    print("Analysis Result:", result) 
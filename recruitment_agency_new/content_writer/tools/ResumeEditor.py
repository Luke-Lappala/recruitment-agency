"""Tool for customizing resumes based on job requirements."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.base_tool import BaseTool
from pydantic import Field
from typing import List, Dict, Any
import os
import re
import json
from datetime import datetime

class ResumeEditor(BaseTool):
    """Tool for customizing resumes based on job requirements."""
    
    template_path: str = Field(..., description="Path to the resume template file")
    job_title: str = Field(..., description="Title of the job position")
    company_name: str = Field(..., description="Name of the company")
    key_requirements: List[str] = Field(..., description="List of key job requirements")
    
    def determine_focus(self) -> str:
        """Determine if the job is focused on internal or external communications."""
        job_title_lower = self.job_title.lower()
        
        # Keywords indicating internal communications focus
        internal_keywords = [
            'internal', 'employee', 'corporate', 'change management',
            'organizational', 'staff', 'workforce', 'culture'
        ]
        
        # Keywords indicating external communications focus
        external_keywords = [
            'external', 'public relations', 'pr', 'media', 'press',
            'publicity', 'brand', 'marketing'
        ]
        
        # Count matches for each focus
        internal_matches = sum(1 for kw in internal_keywords if kw in job_title_lower)
        external_matches = sum(1 for kw in external_keywords if kw in job_title_lower)
        
        # Also check requirements for focus indicators
        for req in self.key_requirements:
            req_lower = req.lower()
            internal_matches += sum(1 for kw in internal_keywords if kw in req_lower)
            external_matches += sum(1 for kw in external_keywords if kw in req_lower)
        
        return 'internal' if internal_matches >= external_matches else 'external'
    
    def customize_resume(self) -> str:
        """Customize the resume content based on job requirements."""
        # Determine which template to use based on job focus
        focus = self.determine_focus()
        template_file = 'luke_lappala_internal_resume.txt' if focus == 'internal' else 'luke_lappala_external_resume.txt'
        template_path = os.path.join(os.path.dirname(self.template_path), template_file)
        
        # Read the appropriate resume template
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                resume_content = file.read()
            return resume_content
        except Exception as e:
            raise ValueError(f"Error reading template file: {str(e)}")
    
    def run(self) -> Dict[str, Any]:
        """Customize resume for the specific job."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs('customized_documents', exist_ok=True)
            
            # Customize resume
            customized_content = self.customize_resume()
            
            # Save customized resume
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            company_name_safe = self.company_name.lower().replace(' ', '_')
            output_file = f"customized_documents/resume_{company_name_safe}_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(customized_content)
            
            focus = self.determine_focus()
            return {
                'message': f"Customized {focus} resume for {self.job_title} position at {self.company_name}",
                'file_path': output_file,
                'focus': focus
            }
            
        except Exception as e:
            return self.handle_error(e)

if __name__ == "__main__":
    # Test the tool
    test_requirements = [
        "Strategic Communications",
        "Employee Engagement",
        "Change Management"
    ]
    
    editor = ResumeEditor(
        template_path="templates/luke_lappala_internal_resume.txt",
        job_title="Internal Communications Manager",
        company_name="Test Corp",
        key_requirements=test_requirements
    )
    
    result = editor.run()
    print("Result:", result) 
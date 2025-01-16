"""Tool for customizing cover letters based on job requirements."""

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

class CoverLetterEditor(BaseTool):
    """Tool for customizing cover letters based on job requirements."""
    
    template_path: str = Field(..., description="Path to the cover letter template file")
    job_title: str = Field(..., description="Title of the job position")
    company_name: str = Field(..., description="Name of the company")
    key_requirements: List[str] = Field(..., description="List of key job requirements")
    
    def customize_cover_letter(self) -> str:
        """Customize the cover letter content based on job requirements."""
        try:
            # Use the correct template file
            template_file = 'luke_lappala_cover_letter.txt'
            template_path = os.path.join(os.path.dirname(self.template_path), template_file)
            
            # Read the cover letter template
            with open(template_path, 'r', encoding='utf-8') as file:
                cover_letter_content = file.read()
            
            # Replace job-specific placeholders
            customized_content = cover_letter_content
            customized_content = customized_content.replace('[Role]', self.job_title)
            customized_content = customized_content.replace('[Company]', self.company_name)
            
            # Add today's date
            today = datetime.now().strftime('%B %d, %Y')
            customized_content = customized_content.replace('[Date]', today)
            
            return customized_content
            
        except Exception as e:
            raise ValueError(f"Error reading template file: {str(e)}")
    
    def run(self) -> Dict[str, Any]:
        """Customize cover letter for the specific job."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs('customized_documents', exist_ok=True)
            
            # Customize cover letter
            customized_content = self.customize_cover_letter()
            
            # Save customized cover letter
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            company_name_safe = self.company_name.lower().replace(' ', '_')
            output_file = f"customized_documents/cover_letter_{company_name_safe}_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(customized_content)
            
            return {
                'message': f"Customized cover letter for {self.job_title} position at {self.company_name}",
                'file_path': output_file
            }
            
        except Exception as e:
            return self.handle_error(e) 
"""Tool for customizing resumes based on job requirements."""

from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import os
from datetime import datetime
from recruitment_agency.utils.logging_config import get_tool_logger
from recruitment_agency.utils.template_loader import TemplateLoader
from recruitment_agency.config import DIRECTORIES, DOCUMENT_SETTINGS

logger = get_tool_logger('ResumeEditor')

class ResumeEditor(BaseTool):
    """
    Tool for customizing Luke's resume based on communications job requirements.
    """
    template_path: str = Field(..., description="Path to Luke's template JSON file")
    job_match_path: str = Field(..., description="Path to the job match JSON file")
    job_index: int = Field(default=0, description="Index of the job in the matches file to customize for")

    def _load_template(self, template_type: str) -> str:
        """Load the appropriate resume template based on type."""
        return TemplateLoader.load_template(template_type)

    def _select_resume_template(self, job_title: str, job_description: str) -> dict:
        """
        Selects the appropriate resume template based on job title and description.
        Returns a dictionary with template sections.
        """
        try:
            # Determine resume type based on job title and description
            job_title_lower = job_title.lower()
            job_desc_lower = job_description.lower()
            
            # Check for internal communications focus
            internal_keywords = {'internal', 'employee', 'organizational', 'corporate'}
            internal_match = any(keyword in job_title_lower or keyword in job_desc_lower 
                               for keyword in internal_keywords)
            
            # Check for external communications focus
            external_keywords = {'pr', 'public relations', 'media', 'external', 'press'}
            external_match = any(keyword in job_title_lower or keyword in job_desc_lower 
                               for keyword in external_keywords)
            
            # Select template based on job focus
            if internal_match and not external_match:
                logger.info("Selected internal communications template")
                template_text = self._load_template("internal_resume")
            else:
                logger.info("Selected external communications template")
                template_text = self._load_template("external_resume")
                
            # Parse template sections
            sections = [s for s in template_text.split('\n\n') if s.strip()]
            logger.info(f"Found {len(sections)} sections in template")
            
            # Extract skills from Areas of Expertise section
            skills = []
            for section in sections:
                if 'Areas of Expertise:' in section:
                    skills_lines = section.split('Areas of Expertise:')[1].strip().split('\n')
                    for line in skills_lines:
                        skills.extend([skill.strip() for skill in line.split('|')])
                    logger.info(f"Extracted {len(skills)} skills from template")
                    break
            
            # Extract summary
            summary = ""
            for i, section in enumerate(sections):
                if i > 0 and 'Areas of Expertise:' in sections[i]:
                    summary = sections[i-1].strip()
                    logger.info("Successfully extracted summary section")
                    break
            
            # Extract experience sections
            experience = []
            in_experience_section = False
            current_role = None
            
            for section in sections:
                if 'PROFESSIONAL EXPERIENCE' in section:
                    in_experience_section = True
                    continue
                    
                if in_experience_section:
                    lines = section.strip().split('\n')
                    if len(lines) >= 2:  # At least company and title/dates line
                        company = lines[0]
                        title_dates = lines[1].split('\t')
                        if len(title_dates) == 2:
                            current_role = {
                                'company': company,
                                'title': title_dates[0],
                                'dates': title_dates[1],
                                'achievements': []
                            }
                            
                            # Add achievements
                            for line in lines[2:]:
                                if line.startswith('-'):
                                    current_role['achievements'].append(line[1:].strip())
                                    
                            experience.append(current_role)
                            
            logger.info(f"Extracted {len(experience)} roles with achievements")
            
            template_data = {
                'summary': summary,
                'skills': skills,
                'experience': experience[:DOCUMENT_SETTINGS['max_roles_to_include']]
            }
            
            logger.info("Successfully created template data structure")
            return template_data
            
        except Exception as e:
            logger.error(f"Error in template selection: {str(e)}")
            raise

    def _customize_resume(self, template_data: dict, job_title: str, company: str, 
                         matched_skills: list, job_description: str) -> dict:
        """
        Customize the resume template for a specific job.
        Returns a dictionary with customized resume sections.
        """
        try:
            # Prioritize matched skills
            all_skills = template_data['skills']
            prioritized_skills = (
                [skill for skill in all_skills if skill in matched_skills] +
                [skill for skill in all_skills if skill not in matched_skills]
            )
            
            # Update template data with prioritized skills
            template_data['skills'] = prioritized_skills
            
            # Customize summary based on job
            summary = template_data['summary']
            if 'internal' in job_title.lower():
                summary = summary.replace('communications professional', 'internal communications professional')
            elif 'external' in job_title.lower() or 'pr' in job_title.lower():
                summary = summary.replace('communications professional', 'public relations professional')
                
            template_data['summary'] = summary
            
            return template_data
            
        except Exception as e:
            logger.error(f"Error customizing resume: {str(e)}")
            raise

    def _format_resume_for_email(self, resume_data: dict, job_title: str, company: str) -> str:
        """
        Converts the resume data structure into a properly formatted text document.
        Uses ASCII characters for compatibility.
        """
        sections = []
        
        # Header
        sections.append("LUKE LAPPALA")
        sections.append("Seattle, WA 98109 | 206-313-7520 | lukelappala@gmail.com | www.linkedin.com/in/luke-lappala")
        sections.append("")
        
        # Title (customized for the specific role)
        sections.append(f"DIRECTOR OF COMMUNICATIONS | {job_title.upper()}")
        sections.append("")
        
        # Summary
        sections.append(resume_data['summary'])
        sections.append("")
        
        # Skills
        sections.append("Areas of Expertise:")
        skills = resume_data['skills']
        for i in range(0, len(skills), DOCUMENT_SETTINGS['max_skills_per_line']):
            skill_group = skills[i:i + DOCUMENT_SETTINGS['max_skills_per_line']]
            sections.append(" | ".join(skill_group))
        sections.append("")
        
        # Experience
        sections.append("PROFESSIONAL EXPERIENCE")
        sections.append("")
        for role in resume_data['experience']:
            sections.append(f"{role['company']}")
            sections.append(f"{role['title']}\t{role['dates']}")
            for achievement in role['achievements'][:DOCUMENT_SETTINGS['max_achievements_per_role']]:
                sections.append(f"- {achievement}")
            sections.append("")
        
        # Education (static section)
        sections.append("EDUCATION")
        sections.append("WASHINGTON STATE UNIVERSITY, Pullman, WA")
        sections.append("Bachelor of Arts, Communications – Public Relations Emphasis")
        sections.append("")
        
        # Technology Skills (static section)
        sections.append("TECHNOLOGY SKILLS")
        sections.append("Cision | Meltwater | Muckrack | JustReachOut | Microsoft Suite | Google Suite | Google Analytics | Hubspot | Wordpress")
        sections.append("Mailchimp | Sprout Social | Hootsuit | Canva | Figma | Claude | ChatGPT | Hunter | PR Newswire | Business Wire")
        
        return "\n".join(sections)

    def run(self) -> dict:
        """
        Customizes Luke's resume based on the specific communications role.
        Returns a dictionary with file paths and status message.
        """
        try:
            logger.info("Starting resume customization process")
            
            # Load job match
            with open(self.job_match_path, 'r') as f:
                job_matches = json.load(f)

            if not job_matches or self.job_index >= len(job_matches):
                logger.error("Invalid job index or no job matches found")
                return "Error: Invalid job index or no job matches found"

            job = job_matches[self.job_index]
            logger.info(f"Processing job: {job['job_title']} at {job['company']}")
            
            # Extract relevant information
            job_title = job['job_title']
            company = job['company']
            matched_skills = job.get('matched_skills', [])
            application_link = job.get('application_link', '')
            
            logger.info(f"Found {len(matched_skills)} matched skills")
            
            # Select appropriate resume template
            logger.info("Selecting resume template")
            selected_template = self._select_resume_template(job['job_title'], job['job_description'])
            logger.info("Successfully selected template")
            
            # Customize resume using selected template
            logger.info("Customizing resume")
            customized_resume = self._customize_resume(
                selected_template,
                job_title,
                company,
                matched_skills,
                job['job_description']
            )
            logger.info("Successfully customized resume")

            # Create timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_slug = company.lower().replace(' ', '_')
            
            # Save JSON version
            os.makedirs(DIRECTORIES['customized_documents'], exist_ok=True)
            json_filename = os.path.join(
                DIRECTORIES['customized_documents'], 
                f"resume_{company_slug}_{timestamp}.json"
            )
            
            logger.info(f"Saving JSON version to {json_filename}")
            with open(json_filename, 'w') as f:
                json.dump({
                    'job_title': job_title,
                    'company': company,
                    'customized_resume': customized_resume,
                    'matched_skills': matched_skills,
                    'application_link': application_link
                }, f, indent=4)

            # Save text version for email
            text_filename = os.path.join(
                DIRECTORIES['customized_documents'], 
                f"resume_{company_slug}_{timestamp}.txt"
            )
            logger.info(f"Formatting resume for email and saving to {text_filename}")
            formatted_resume = self._format_resume_for_email(customized_resume, job_title, company)
            
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(formatted_resume)

            logger.info("Resume customization completed successfully")
            return {
                'message': f"Resume customized successfully for {job_title} at {company}",
                'json_file': json_filename,
                'text_file': text_filename,
                'application_link': application_link
            }

        except Exception as e:
            logger.error(f"Error in resume customization: {str(e)}")
            return f"Error customizing resume: {str(e)}"

if __name__ == "__main__":
    # Test the tool
    tool = ResumeEditor(
        template_path="templates/luke_templates.json",
        job_match_path="job_matches/matches_20240101_120000.json",
        job_index=0
    )
    print(tool.run()) 
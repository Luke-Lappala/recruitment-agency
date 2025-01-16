"""Tool for customizing cover letters based on job requirements."""

from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import os
from datetime import datetime
from recruitment_agency.utils.logging_config import get_tool_logger
from recruitment_agency.utils.template_loader import TemplateLoader
from recruitment_agency.config import DIRECTORIES, DOCUMENT_SETTINGS

logger = get_tool_logger('CoverLetterEditor')

class CoverLetterEditor(BaseTool):
    """
    Tool for customizing Luke's cover letter based on communications job requirements.
    """
    job_match_path: str = Field(..., description="Path to the job match JSON file")
    job_index: int = Field(default=0, description="Index of the job in the matches file to customize for")

    def _load_template(self) -> dict:
        """Load the cover letter template."""
        return TemplateLoader.load_template('cover_letter')

    def _customize_letter(self, template: str, job_title: str, company: str, 
                         matched_skills: list, job_description: str) -> str:
        """
        Customize the cover letter template for a specific job.
        Returns the customized letter as a string.
        """
        try:
            # Format date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Format header
            header = f"LUKE LAPPALA\nSEATTLE, WA 98109 | (206) 313-7520 | LUKELAPPALA@GMAIL.COM\n\n{current_date}\n\n"
            header += f"Hiring Manager\n{company}\n{company} Headquarters\nSeattle, WA\n\n"
            header += f"RE: Opportunity for {job_title}\n\nDear Hiring Manager,\n\n"
            
            # Format introduction
            intro = "With more than 12 years of experience developing strategic communication frameworks and enhancing employee engagement, I am eager to apply for the "
            intro += f"{job_title} role at {company}. I specialize in crafting internal communications strategies that foster trust, drive alignment across diverse teams, "
            intro += f"and elevate organizational cohesion—delivering results in dynamic, fast-paced environments like {company}.\n\n"
            
            # Format body based on job focus
            job_focus = self._determine_job_focus(job_title, job_description)
            body = self._get_body_paragraphs(job_focus, company)
            
            # Format closing
            closing = self._customize_closing(company, job_description)
            
            # Combine all sections
            letter = header + intro + body + closing
            
            return letter
            
        except Exception as e:
            logger.error(f"Error customizing cover letter: {str(e)}")
            raise

    def _determine_job_focus(self, job_title: str, job_description: str) -> str:
        """Determine the primary focus of the job."""
        job_title_lower = job_title.lower()
        job_desc_lower = job_description.lower()
        
        internal_keywords = {'internal', 'employee', 'organizational', 'corporate'}
        external_keywords = {'pr', 'public relations', 'media', 'external', 'press'}
        
        internal_match = any(keyword in job_title_lower or keyword in job_desc_lower 
                           for keyword in internal_keywords)
        external_match = any(keyword in job_title_lower or keyword in job_desc_lower 
                           for keyword in external_keywords)
        
        if internal_match and not external_match:
            return 'internal'
        elif external_match and not internal_match:
            return 'external'
        else:
            return 'general'

    def _get_body_paragraphs(self, job_focus: str, company: str) -> str:
        """Get the appropriate body paragraphs based on job focus."""
        paragraphs = []
        
        # Achievement paragraphs based on focus
        achievements = {
            'internal': [
                "At Coding Dojo, I spearheaded the development and execution of comprehensive internal communications strategies that significantly enhanced employee engagement and organizational alignment. I established new communication channels and frameworks that increased employee satisfaction scores by 35% and improved cross-departmental collaboration.",
                "My experience includes leading change management communications for major organizational transitions, developing executive communication strategies, and creating engaging content that resonates with diverse employee audiences. I've successfully managed sensitive communications during periods of significant change, maintaining employee trust and engagement throughout.",
            ],
            'external': [
                "At Coding Dojo, I led comprehensive PR campaigns that secured over 700 media placements across major outlets including TechCrunch, ZDNet, and Good Morning America. By developing strategic messaging frameworks and building strong media relationships, I significantly enhanced the company's market presence and thought leadership position.",
                "My expertise spans crisis communications, media relations, and strategic storytelling. I've successfully managed high-stakes PR situations, developed impactful thought leadership programs, and created compelling narratives that resonate with diverse audiences.",
            ],
            'general': [
                "At Coding Dojo, I developed and executed comprehensive communications strategies that drove both internal engagement and external visibility. I led initiatives that increased employee satisfaction by 35% while securing over 700 media placements in major outlets.",
                "My experience spans the full spectrum of communications, from change management and executive communications to media relations and crisis management. I've consistently delivered results by creating compelling narratives that resonate with diverse stakeholders.",
            ]
        }
        
        paragraphs.extend(achievements[job_focus])
        
        # Add company-specific paragraph
        company_paragraph = f"I am particularly drawn to {company}'s commitment to innovation and excellence in communications. "
        company_paragraph += "My track record of developing and executing successful communication strategies, combined with my passion for creating impactful narratives, "
        company_paragraph += f"makes me an ideal candidate to contribute to {company}'s continued success.\n\n"
        
        paragraphs.append(company_paragraph)
        
        return "\n\n".join(paragraphs) + "\n\n"

    def _customize_closing(self, company: str, job_description: str) -> str:
        """Customize the closing paragraph based on company and job description."""
        closings = {
            'internal': (
                "I am excited about the opportunity to bring my expertise in internal communications "
                f"and employee engagement to {company}. I would welcome the chance to discuss how "
                "my experience aligning communications with business objectives and fostering "
                "employee engagement could benefit your organization.\n\n"
                "Thank you for considering my application.\n\n"
                "Best regards,\n\n"
                "Luke Lappala"
            ),
            'external': (
                "I am excited about the opportunity to bring my expertise in public relations "
                f"and strategic communications to {company}. I would welcome the chance to discuss how "
                "my experience in media relations and brand storytelling could help elevate "
                "your organization's market presence.\n\n"
                "Thank you for considering my application.\n\n"
                "Best regards,\n\n"
                "Luke Lappala"
            ),
            'general': (
                f"I am excited about the opportunity to bring my communications expertise to {company}. "
                "I would welcome the chance to discuss how my diverse experience in strategic "
                "communications could contribute to your organization's success.\n\n"
                "Thank you for considering my application.\n\n"
                "Best regards,\n\n"
                "Luke Lappala"
            )
        }
        
        job_focus = self._determine_job_focus('', job_description)
        return closings[job_focus]

    def run(self) -> dict:
        """
        Customizes Luke's cover letter based on the specific communications role.
        Returns a dictionary with file paths and status message.
        """
        try:
            logger.info("Starting cover letter customization process")
            
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
            
            # Load template
            template = self._load_template()
            
            # Customize cover letter
            logger.info("Customizing cover letter")
            customized_letter = self._customize_letter(
                template,
                job_title,
                company,
                matched_skills,
                job['job_description']
            )
            logger.info("Successfully customized cover letter")

            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_slug = company.lower().replace(' ', '_')
            
            # Save text version for email
            os.makedirs(DIRECTORIES['customized_documents'], exist_ok=True)
            text_filename = os.path.join(
                DIRECTORIES['customized_documents'], 
                f"cover_letter_{company_slug}_{timestamp}.txt"
            )
            
            logger.info(f"Saving customized cover letter to {text_filename}")
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(customized_letter)

            logger.info("Cover letter customization completed successfully")
            return {
                'message': f"Cover letter customized successfully for {job_title} at {company}",
                'text_file': text_filename,
                'application_link': application_link
            }

        except Exception as e:
            logger.error(f"Error in cover letter customization: {str(e)}")
            return f"Error customizing cover letter: {str(e)}"

if __name__ == "__main__":
    # Test the tool
    tool = CoverLetterEditor(
        job_match_path="job_matches/matches_20240101_120000.json",
        job_index=0
    )
    print(tool.run()) 
from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import os
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class JobAnalyzer(BaseTool):
    """
    Tool for analyzing communications job postings and matching them with Luke's profile.
    """
    template_path: str = Field(..., description="Path to Luke's template JSON file")
    job_posting_path: str = Field(..., description="Path to the job search results JSON file")
    required_skills_match: float = Field(
        default=0.5,
        description="Minimum percentage of required skills that should match"
    )

    def run(self):
        """
        Analyzes communications job postings and returns matches based on Luke's profile.
        """
        try:
            # Load template profile
            with open(self.template_path, 'r') as f:
                profile = json.load(f)

            # Load job postings
            with open(self.job_posting_path, 'r') as f:
                job_data = json.load(f)

            # Extract skills from both resume versions separately
            internal_template = profile['resumes']['internal_communications']['template']
            external_template = profile['resumes']['external_communications']['template']
            
            # Also check the focus keywords as skills
            internal_focus = profile['resumes']['internal_communications']['focus']
            external_focus = profile['resumes']['external_communications']['focus']
            
            # Extract skills for internal and external resumes separately
            internal_skills = set(
                skill.lower() for skill in (
                    self._extract_skills_from_text(internal_template) +
                    internal_focus
                )
            )
            
            external_skills = set(
                skill.lower() for skill in (
                    self._extract_skills_from_text(external_template) +
                    external_focus
                )
            )
            
            logger.info(f"Internal resume skills: {internal_skills}")
            logger.info(f"External resume skills: {external_skills}")

            matches = []
            
            # Debug: Print skills found in each job posting
            for job in job_data.get('data', []):
                job_skills = set(
                    skill.lower() 
                    for skill in self._extract_communications_skills(job.get('job_description', ''))
                )
                logger.info(f"Skills found in job '{job.get('job_title')}': {job_skills}")
                
                # Calculate match score using new method
                match_score, matched_skills, resume_type = self._calculate_match_score(
                    job.get('job_title', ''),
                    job_skills,
                    internal_skills,
                    external_skills
                )
                
                # Consider a strong match if the score is high enough (adjusted threshold)
                if match_score >= 3:  # Adjusted threshold to account for weighted scoring
                    match_percentage = (match_score / (len(internal_skills) if resume_type == 'internal' else len(external_skills))) * 100
                    
                    matches.append({
                        'job_title': job.get('job_title'),
                        'company': job.get('employer_name'),
                        'location': job.get('job_location'),
                        'match_percentage': round(match_percentage, 2),
                        'job_link': job.get('job_apply_link'),
                        'job_description': job.get('job_description'),
                        'matched_skills': list(matched_skills),
                        'resume_type': resume_type,
                        'match_score': round(match_score, 2)
                    })

            # Sort matches by match percentage
            matches.sort(key=lambda x: x['match_percentage'], reverse=True)

            # Save matches
            os.makedirs("job_matches", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_matches/matches_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(matches, f, indent=4)

            return f"Job analysis completed. Found {len(matches)} strong matches. Results stored in {filename}"

        except Exception as e:
            logger.error(f"Error in job analysis: {str(e)}")
            return f"Error analyzing jobs: {str(e)}"

    def _extract_communications_skills(self, text):
        """
        Helper method to extract communications-related skills from text.
        """
        # Just extract skills from the provided text
        return self._extract_skills_from_text(text)

    def _extract_skills_from_text(self, text):
        """
        Extract skills from given text using simplified regular expressions for more accurate matching.
        """
        # Define skill variations and related terms with your exact keywords
        skill_variations = {
            # Strategic Planning & Leadership
            "strategic planning": [
                "strategic development", "strategy development",
                "strategic direction", "strategic initiatives",
                "strategic leadership", "strategic management",
                "communications strategy", "strategic communications",
                "strategic foresight", "strategic vision"
            ],
            "stakeholder management": [
                "stakeholder engagement", "stakeholder relations",
                "relationship management", "key stakeholders",
                "stakeholder communications", "executive relationships",
                "stakeholder collaboration", "stakeholder partnerships"
            ],
            "brand messaging": [
                "brand communications", "brand strategy",
                "brand voice", "brand management",
                "brand alignment", "messaging strategy",
                "corporate messaging", "brand positioning",
                "brand identity", "brand narrative"
            ],
            
            # Core Communications Areas
            "communications strategy": [
                "communication strategies", "strategic communications", 
                "communications planning", "strategic planning",
                "integrated communications", "integrated strategy",
                "communications roadmap", "communications program",
                "communication framework", "communication blueprint"
            ],
            "public relations": [
                "pr", "media relations", "press relations",
                "media outreach", "press outreach", "media strategy",
                "publicity", "external communications",
                "public affairs", "public engagement"
            ],
            "executive communications": [
                "executive thought leadership", "leadership communications",
                "executive messaging", "leadership messaging",
                "executive positioning", "c-suite communications",
                "leadership content", "executive content"
            ],
            
            # Content & Storytelling
            "content strategy": [
                "content planning", "content development",
                "copywriting", "content management",
                "editorial strategy", "content operations",
                "customer storytelling", "data-driven storytelling"
            ],
            "storytelling": [
                "narrative development", "brand storytelling",
                "content creation", "story development",
                "messaging", "narrative"
            ],
            
            # Management & Leadership
            "project management": [
                "program management", "campaign management",
                "event management", "event & speaker program management",
                "initiative management", "project leadership"
            ],
            "team leadership": [
                "cross-functional collaboration", "stakeholder management",
                "agency management", "team management",
                "people leadership", "organizational leadership"
            ],
            
            # Employee & Change Management
            "employee engagement": [
                "internal communications", "employee communications",
                "workforce communications", "staff engagement",
                "employee experience", "internal engagement"
            ],
            "dei communication": [
                "diversity communications", "inclusion communications",
                "equity communications", "dei initiatives",
                "diversity and inclusion"
            ],
            "policy communication": [
                "policy messaging", "compliance communications",
                "regulatory communications", "policy initiatives"
            ],
            
            # Digital & Technical
            "social media": [
                "digital communications", "digital channels",
                "social platforms", "digital strategy",
                "social strategy", "online presence"
            ],
            "crm": [
                "customer relationship management",
                "stakeholder database", "contact management",
                "relationship tracking"
            ],
            
            # Crisis & Brand Management
            "crisis management": [
                "issues management", "reputation management",
                "crisis communications", "risk management",
                "emergency communications"
            ],
            "brand alignment": [
                "brand strategy", "brand messaging",
                "brand voice", "brand communications",
                "brand management"
            ]
        }

        # Base communications skills
        communications_skills = [
            # Strategic Skills
            "communications strategy", "public relations", "media relations",
            "strategic communications", "executive thought leadership",
            "strategic planning", "stakeholder management", "brand messaging",
            
            # Content & Engagement
            "data-driven storytelling", "customer storytelling",
            "content strategy", "copywriting",
            
            # Management & Leadership
            "project management", "team leadership",
            "cross-functional collaboration", "agency management",
            
            # Employee Communications
            "employee engagement", "dei communication",
            "policy communication", "brand alignment",
            
            # Technical & Digital
            "social media", "crm",
            
            # Event & Program Management
            "event & speaker program management",
            "campaign management",
            
            # Risk & Crisis
            "crisis management"
        ]

        # Use simplified regex to find skills
        found_skills = set()
        for skill in communications_skills:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                found_skills.add(skill)

        for main_skill, variations in skill_variations.items():
            if re.search(rf"\b{re.escape(main_skill)}\b", text, re.IGNORECASE):
                found_skills.add(main_skill)
            for variation in variations:
                if re.search(rf"\b{re.escape(variation)}\b", text, re.IGNORECASE):
                    found_skills.add(main_skill)

        return list(found_skills)

    def _select_resume_template(self, job_title, job_description):
        """
        Selects the most appropriate resume template based on the job focus.
        """
        job_text = (job_title + " " + job_description).lower()
        
        # Load templates
        with open(self.template_path, 'r') as f:
            profile = json.load(f)
        
        # Score each template
        scores = {}
        for template_name, template_data in profile['resumes'].items():
            score = sum(1 for focus in template_data['focus'] if focus.lower() in job_text)
            scores[template_name] = score
        
        # Select template with highest score
        best_template = max(scores.items(), key=lambda x: x[1])[0]
        return profile['resumes'][best_template]['template']

    def _extract_required_skills(self, job_description):
        """Extract and normalize required skills from job description."""
        try:
            # Get the required skills section
            required_section = job_description.split('Required skills:')[-1].split('\n')[0]
            
            # Split by commas and clean up
            skills = [
                skill.strip().lower()
                for skill in required_section.split(',')
                if skill.strip()
            ]
            
            # Normalize common variations
            normalized_skills = set()
            for skill in skills:
                # Remove trailing periods and normalize text
                skill = skill.rstrip('.').replace('-', ' ').replace('&', 'and')
                
                # Handle common variations
                if skill in ['pr', 'public relations', 'media relations', 'press relations']:
                    normalized_skills.update(['public relations', 'media relations', 'external communications'])
                elif 'communication' in skill or 'communications' in skill:
                    if 'strategy' in skill or 'strategic' in skill:
                        normalized_skills.update(['communications strategy', 'strategic communications', 'strategic planning'])
                    elif 'internal' in skill or 'employee' in skill:
                        normalized_skills.update(['internal communications', 'employee communications', 'employee engagement'])
                    elif 'external' in skill or 'public' in skill:
                        normalized_skills.update(['external communications', 'public relations', 'media relations'])
                    else:
                        normalized_skills.update(['communications strategy', 'strategic communications'])
                elif 'executive' in skill or 'leadership' in skill:
                    normalized_skills.update(['executive communications', 'executive thought leadership', 'team leadership'])
                elif 'content' in skill:
                    if 'strategy' in skill or 'strategic' in skill:
                        normalized_skills.update(['content strategy', 'content development', 'strategic communications'])
                    else:
                        normalized_skills.update(['content creation', 'content development', 'content strategy'])
                elif 'team' in skill or 'cross functional' in skill:
                    normalized_skills.update(['team leadership', 'cross-functional collaboration', 'stakeholder management'])
                elif 'project' in skill or 'program' in skill:
                    normalized_skills.update(['project management', 'program management', 'strategic planning'])
                elif 'strategic' in skill or 'strategy' in skill:
                    normalized_skills.update(['strategic planning', 'communications strategy', 'strategic communications'])
                elif 'brand' in skill or 'messaging' in skill:
                    normalized_skills.update(['brand messaging', 'brand communications', 'strategic communications'])
                elif 'stakeholder' in skill or 'relationship' in skill:
                    normalized_skills.update(['stakeholder management', 'team leadership', 'executive communications'])
                else:
                    normalized_skills.add(skill)
                    
            logger.info(f"Normalized required skills: {normalized_skills}")
            return normalized_skills
            
        except Exception as e:
            logger.error(f"Error extracting required skills: {str(e)}")
            return set()

    def _get_normalized_skill(self, skill):
        """
        Returns a normalized version of a skill, handling common variations.
        """
        # Define common variations
        variations = {
            "communications strategy": ["strategic communications", "communication strategy"],
            "public relations": ["pr", "media relations", "press relations"],
            "internal communications": ["employee communications", "internal comms"],
            "external communications": ["public communications", "external comms"],
            "content strategy": ["content development", "content planning"],
            "executive communications": ["leadership communications", "executive content"]
        }
        
        skill = skill.lower()
        for main_skill, skill_variations in variations.items():
            if skill == main_skill or skill in skill_variations:
                return main_skill
        return skill

    def _calculate_match_score(self, job_title, job_skills, internal_skills, external_skills):
        """
        Calculate match score considering job title, core skills, and skill variations.
        """
        # Define core skills that are valuable for both internal and external roles
        core_skills = {
            "communications strategy",
            "executive communications",
            "content strategy",
            "stakeholder management",
            "project management",
            "public relations",
            "employee engagement",
            "storytelling",
            "social media"  # Added as it's increasingly important for all comms roles
        }
        
        # Normalize all skills
        normalized_job_skills = {self._get_normalized_skill(skill) for skill in job_skills}
        normalized_internal_skills = {self._get_normalized_skill(skill) for skill in internal_skills}
        normalized_external_skills = {self._get_normalized_skill(skill) for skill in external_skills}
        
        # Calculate core skills match (weighted more heavily)
        core_matches = len(normalized_job_skills.intersection(core_skills))
        core_score = core_matches * 1.5  # Weight core skills more heavily
        
        # Calculate internal and external matches
        internal_matches = normalized_job_skills.intersection(normalized_internal_skills)
        external_matches = normalized_job_skills.intersection(normalized_external_skills)
        
        # Job title relevance score
        title_score = 0
        job_title_lower = job_title.lower()
        if any(term in job_title_lower for term in ["internal", "employee", "corporate"]):
            title_score = len(internal_matches) * 0.5
        elif any(term in job_title_lower for term in ["pr", "public", "external", "media"]):
            title_score = len(external_matches) * 0.5
        elif "communications" in job_title_lower or "specialist" in job_title_lower:
            # Boost score for general communications roles
            title_score = (len(internal_matches) + len(external_matches)) * 0.25
        
        # Calculate final scores
        # For generalist positions, consider both internal and external matches
        if "specialist" in job_title_lower or "communications" in job_title_lower:
            combined_score = (len(internal_matches) + len(external_matches)) * 0.5 + core_score + title_score
            return combined_score, internal_matches.union(external_matches), "generalist"
        else:
            internal_score = len(internal_matches) + core_score + (title_score if "internal" in job_title_lower else 0)
            external_score = len(external_matches) + core_score + (title_score if "external" in job_title_lower else 0)
            
            if internal_score >= external_score:
                return internal_score, internal_matches, "internal"
            else:
                return external_score, external_matches, "external"

if __name__ == "__main__":
    # Test the tool
    tool = JobAnalyzer(
        template_path="templates/luke_templates.json",
        job_posting_path="job_searches/search_results_20240101_120000.json",
        required_skills_match=0.5
    )
    print(tool.run()) 
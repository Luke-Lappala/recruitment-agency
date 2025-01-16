"""Content Writer agent for customizing and managing application documents."""

from agency_swarm import Agent
from recruitment_agency.content_writer.tools.ResumeEditor import ResumeEditor
from recruitment_agency.content_writer.tools.CoverLetterEditor import CoverLetterEditor

class ContentWriter(Agent):
    """Agent responsible for customizing and managing application documents."""
    
    def __init__(self):
        """Initialize the Content Writer agent."""
        super().__init__(
            name="Content Writer",
            description="Customizes and manages application documents",
            instructions="./instructions.md",
            tools=[ResumeEditor, CoverLetterEditor],
            temperature=0.7
        ) 
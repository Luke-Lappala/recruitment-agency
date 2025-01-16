"""Template loader utility for the recruitment agency."""

import json
import os
from typing import Dict, Any
from recruitment_agency.config import TEMPLATE_PATHS

class TemplateLoader:
    """Utility class for loading and caching templates."""
    
    _template_cache: Dict[str, Any] = {}
    
    @classmethod
    def load_template(cls, template_type: str) -> str:
        """
        Load a template from file, using cache if available.
        
        Args:
            template_type: Type of template to load ('internal_resume', 'external_resume', 'cover_letter')
            
        Returns:
            Template content as string
        """
        if template_type not in TEMPLATE_PATHS:
            raise ValueError(f"Unknown template type: {template_type}")
            
        # Check cache first
        if template_type in cls._template_cache:
            return cls._template_cache[template_type]
            
        template_path = TEMPLATE_PATHS[template_type]
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                if template_path.endswith('.json'):
                    content = json.load(f)
                else:
                    content = f.read()
                    
            cls._template_cache[template_type] = content
            return content
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {template_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in template file: {template_path}")
        except Exception as e:
            raise Exception(f"Error loading template {template_type}: {str(e)}")
    
    @classmethod
    def clear_cache(cls):
        """Clear the template cache."""
        cls._template_cache.clear() 
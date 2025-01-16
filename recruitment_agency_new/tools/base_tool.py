"""Base tool class for all tools in the recruitment agency."""

from pydantic import BaseModel
from typing import Dict, Any, Optional

class BaseTool(BaseModel):
    """Base class for all tools in the recruitment agency."""
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
    
    def run(self) -> Dict[str, Any]:
        """Run the tool. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement run()")
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate the result of the tool run."""
        return isinstance(result, dict)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors that occur during tool execution."""
        return {
            'error': str(error),
            'type': type(error).__name__
        } 
"""Logging configuration for the recruitment agency."""

import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging for the recruitment agency."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/agency_{timestamp}.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('recruitment_agency')

def get_tool_logger(tool_name: str) -> logging.Logger:
    """Get a logger for a specific tool."""
    logger = logging.getLogger(f'recruitment_agency.tools.{tool_name}')
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Add file handler if not already present
    if not logger.handlers:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_handler = logging.FileHandler(f'logs/tool_{tool_name}_{timestamp}.log')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(console_handler)
        
        # Set level
        logger.setLevel(logging.INFO)
    
    return logger
"""Configuration settings for the recruitment agency."""

import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
CUSTOMIZED_DOCUMENTS_DIR = os.path.join(BASE_DIR, 'customized_documents')
JOB_MATCHES_DIR = os.path.join(BASE_DIR, 'job_matches')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Template paths
TEMPLATE_PATHS = {
    'internal_resume': os.path.join(TEMPLATES_DIR, 'luke lappala_internal resume.txt'),
    'external_resume': os.path.join(TEMPLATES_DIR, 'luke lappala_external resume.txt'),
    'cover_letter': os.path.join(TEMPLATES_DIR, 'luke_templates.json'),
}

# Directory configurations
DIRECTORIES = {
    'templates': TEMPLATES_DIR,
    'customized_documents': CUSTOMIZED_DOCUMENTS_DIR,
    'job_matches': JOB_MATCHES_DIR,
    'logs': LOGS_DIR,
}

# Document settings
DOCUMENT_SETTINGS = {
    'max_skills_per_line': 3,
    'max_achievements_per_role': 5,
    'max_roles_to_include': 4,
    'email_settings': {
        'sender_email': 'south.lake.union.cougar@gmail.com',
        'recipient_email': 'lukelappala@gmail.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
    }
}

# Ensure directories exist
for directory in DIRECTORIES.values():
    os.makedirs(directory, exist_ok=True) 
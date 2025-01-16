"""Test file for the ResumeEditor tool."""

import sys
from pathlib import Path
import traceback

# Add the project root to Python path
project_root = str(Path(__file__).parent)
print(f"Project root: {project_root}")
print(f"Python path before: {sys.path}")

if project_root not in sys.path:
    sys.path.append(project_root)
    print(f"Added {project_root} to Python path")

print(f"Python path after: {sys.path}")

try:
    print("Attempting to import ResumeEditor...")
    from content_writer.tools.ResumeEditor import ResumeEditor
    print("Successfully imported ResumeEditor")
except Exception as e:
    print(f"Failed to import ResumeEditor: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)

import json
import os

def test_resume_editor():
    """Test the ResumeEditor tool with both internal and external job types."""
    
    # Test cases
    test_cases = [
        {
            "job_title": "Internal Communications Manager",
            "company_name": "Tech Corp",
            "key_requirements": [
                "Change Management",
                "Employee Engagement",
                "Corporate Communications",
                "Leadership Communication",
                "Culture Building"
            ]
        },
        {
            "job_title": "Public Relations Manager",
            "company_name": "Media Corp",
            "key_requirements": [
                "Media Relations",
                "Press Release Writing",
                "Brand Management",
                "Crisis Communications",
                "Social Media Strategy"
            ]
        }
    ]
    
    template_path = os.path.join(project_root, "templates", "luke_templates.json")
    
    print("\nTesting ResumeEditor tool...")
    print(f"Using template at: {template_path}")
    print(f"Template exists: {os.path.exists(template_path)}")
    
    for case in test_cases:
        print(f"\nTesting with job: {case['job_title']}")
        
        try:
            # Create ResumeEditor instance
            editor = ResumeEditor(
                template_path=template_path,
                job_title=case['job_title'],
                company_name=case['company_name'],
                key_requirements=case['key_requirements']
            )
            
            # Run the editor
            result = editor.run()
            
            # Print results
            if 'error' in result:
                print(f"Error: {result['error']}")
                print(f"Type: {result.get('type', 'Unknown')}")
            else:
                print(f"Focus determined: {result['focus']}")
                print(f"Output file: {result['file_path']}")
                print(f"Message: {result['message']}")
                
                # Verify the output file exists
                if os.path.exists(result['file_path']):
                    print("✓ Output file created successfully")
                    
                    # Read and print first few lines of the customized resume
                    with open(result['file_path'], 'r') as f:
                        content = f.read()
                        print("\nFirst 200 characters of customized resume:")
                        print(content[:200] + "...")
                else:
                    print("✗ Failed to create output file")
        except Exception as e:
            print(f"Error processing {case['job_title']}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()

if __name__ == "__main__":
    test_resume_editor() 
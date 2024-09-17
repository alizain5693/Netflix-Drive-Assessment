import os
import json
from dotenv import load_dotenv
from setup import get_drive_service
from drive_utils import count_items

# Load environment variables from .env file
load_dotenv()
SOURCE_FOLDER_ID = os.getenv('SOURCE_FOLDER_ID')

def generate_report() -> None:
    """
    Generate a report of file and folder counts in the source folder.
    The report is printed to console and saved to a JSON file.
    """
    # Get the Google Drive service object
    service = get_drive_service()
    if not service:
        print("Failed to create Drive service. Please check your setup.")
        return

    # Count files and folders in the source folder (non-recursive)
    file_count, folder_count, _ = count_items(service, SOURCE_FOLDER_ID, recursive=False)
    
    if file_count is not None and folder_count is not None:
        # Calculate total items
        total_items = file_count + folder_count
        
        # Create report dictionary
        report = {
            "source_folder_id": SOURCE_FOLDER_ID,
            "file_count": file_count,
            "folder_count": folder_count,
            "total_items": total_items
        }

        # Print report to console
        print(json.dumps(report, indent=4))

        # Save report to JSON file
        with open('report1.json', 'w') as f:
            json.dump(report, f, indent=4)
        print("Report has been saved to report1.json")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    generate_report()
import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from setup import get_drive_service
from drive_utils import count_items, get_top_level_folders

# Load environment variables from .env file
load_dotenv()
SOURCE_FOLDER_ID = os.getenv('SOURCE_FOLDER_ID')

def generate_report(service, source_folder_id: str) -> Optional[Dict]:
    """
    Generate a report of file and folder counts for top-level folders in the source folder.

    Args:
        service: Google Drive service object.
        source_folder_id (str): ID of the source folder.

    Returns:
        Optional[Dict]: A dictionary containing the report data, or None if an error occurs.
    """
    # Get all top-level folders in the source folder
    top_level_folders = get_top_level_folders(service, source_folder_id)
    if top_level_folders is None:
        return None

    # Initialize report dictionary
    report = {
        "source_folder_id": source_folder_id,
        "top_level_folders": [],
        "total_nested_folders": 0
    }

    # Process each top-level folder
    for folder in top_level_folders:
        # Count items recursively in the folder
        files, folders, nested = count_items(service, folder['id'], recursive=True)
        if files is None or folders is None or nested is None:
            continue
        
        # Add folder information to the report
        report["top_level_folders"].append({
            "name": folder['name'],
            "id": folder['id'],
            "total_files": files,
            "total_folders": folders,
            "total_items": files + folders
        })
        
        # Update total nested folders count
        report["total_nested_folders"] += nested

    return report

def main() -> None:
    """
    Main function to generate and output the report.
    """
    # Get the Google Drive service object
    service = get_drive_service()
    if not service:
        print("Failed to create Drive service. Please check your setup.")
        return

    # Generate the report
    report = generate_report(service, SOURCE_FOLDER_ID)
    
    if report:
        # Print report to console
        print(json.dumps(report, indent=4))

        # Save report to JSON file
        with open('report2.json', 'w') as f:
            json.dump(report, f, indent=4)
        print("Report has been saved to report2.json")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    main()
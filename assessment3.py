import os
from dotenv import load_dotenv
from setup import get_drive_service
from drive_utils import get_top_level_folders, copy_folder

# Load environment variables from .env file
load_dotenv()
SOURCE_FOLDER_ID = os.getenv('SOURCE_FOLDER_ID')
DESTINATION_FOLDER_ID = os.getenv('DESTINATION_FOLDER_ID')

def main():
    """
    Main function to copy contents from source folder to destination folder.
    """
    # Get the Google Drive service object
    service = get_drive_service()
    if not service:
        print("Failed to create Drive service. Please check your setup.")
        return

    print(f"Starting to copy contents from folder {SOURCE_FOLDER_ID} to {DESTINATION_FOLDER_ID}")
    
    # Get top-level folders in the source folder
    top_level_folders = get_top_level_folders(service, SOURCE_FOLDER_ID)
    
    if top_level_folders is None:
        print("Failed to retrieve top-level folders.")
        return

    # Copy each top-level folder
    for folder in top_level_folders:
        print(f"Copying folder: {folder['name']}")
        copied_folder_id = copy_folder(service, folder['id'], DESTINATION_FOLDER_ID, folder['name'])
        if copied_folder_id:
            print(f"Successfully copied folder {folder['name']} to {copied_folder_id}")
        else:
            print(f"Failed to copy folder {folder['name']}")

    print("Copy process completed.")

if __name__ == "__main__":
    main()
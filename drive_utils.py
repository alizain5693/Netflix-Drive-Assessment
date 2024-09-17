from typing import Dict, List, Tuple, Optional
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

def count_items(service, folder_id: str, recursive: bool = False) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Count items in a Google Drive folder, optionally recursing into subfolders.
    Uses pagination to handle large folders.

    Args:
        service: Google Drive service object.
        folder_id (str): ID of the folder to count items in.
        recursive (bool): Whether to count items in subfolders recursively. Default is False.

    Returns:
        Tuple[Optional[int], Optional[int], Optional[int]]: A tuple containing the count of files, folders, and nested folders.
                                                            Returns (None, None, None) if an error occurs.
    """
    try:
        # Construct the query to get all non-trashed files and folders
        query = (f"'{folder_id}' in parents and trashed = false and "
                 f"(mimeType = 'application/vnd.google-apps.folder' or "
                 f"not mimeType contains 'application/vnd.google-apps.file')")
        
        file_count, folder_count, nested_folder_count = 0, 0, 0
        page_token = None

        # Use pagination to handle large folders
        while True:
            # Make API request to list files and folders
            results = service.files().list(q=query, 
                                           fields="nextPageToken, files(id, mimeType)",
                                           pageToken=page_token,
                                           pageSize=1000).execute()
            items = results.get('files', [])

            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folder_count += 1
                    if recursive:
                        # Recursively count items in subfolders
                        sub_files, sub_folders, sub_nested = count_items(service, item['id'], recursive=True)
                        # Only update counts if recursive call was successful
                        if sub_files is not None and sub_folders is not None and sub_nested is not None:
                            file_count += sub_files
                            folder_count += sub_folders
                            # Add 1 to nested_folder_count to account for current subfolder
                            nested_folder_count += sub_nested + 1
                else:
                    file_count += 1

            # Get the next page token, if any
            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return file_count, folder_count, nested_folder_count

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        return None, None, None

def get_top_level_folders(service, folder_id: str) -> Optional[List[Dict[str, str]]]:
    """
    Get the top-level folders in a Google Drive folder.
    Uses pagination to handle large folders.

    Args:
        service: Google Drive service object.
        folder_id (str): ID of the folder to get top-level folders from.

    Returns:
        Optional[List[Dict[str, str]]]: A list of dictionaries containing folder information,
                                        or None if an error occurs.
    """
    try:
        # Construct query to get only folders (not files) that aren't in trash
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        top_level_folders = []
        page_token = None

        # Use pagination to handle large folders
        while True:
            # Make API request to list folders
            results = service.files().list(q=query, 
                                           fields="nextPageToken, files(id, name)",
                                           pageToken=page_token,
                                           pageSize=1000).execute()
            top_level_folders.extend(results.get('files', []))

            # Get the next page token, if any
            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return top_level_folders

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        return None
    

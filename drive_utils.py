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
    
def copy_file(service, file_id: str, destination_folder_id: str, file_name: str) -> Optional[str]:
    """
    Copy a file from one Google Drive folder to another.

    Args:
        service: Google Drive service object.
        file_id (str): ID of the file to copy.
        destination_folder_id (str): ID of the destination folder.
        file_name (str): Name of the file.

    Returns:
        Optional[str]: ID of the copied file, or None if an error occurs.
    """
    try:
        file = service.files().get(fileId=file_id, fields='mimeType').execute()
        mime_type = file.get('mimeType')
        # For copying google workspace files
        if 'application/vnd.google-apps.' in mime_type:
            copied_file = service.files().copy(
                fileId=file_id,
                body={'name': file_name, 'parents': [destination_folder_id]}
            ).execute()
        # For copying all other files
        else:
            # Download
            request = service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            # Reset Buffer, Set Metadata, and Upload
            file_content.seek(0)
            file_metadata = {'name': file_name, 'parents': [destination_folder_id]}
            media = MediaIoBaseUpload(file_content, mimetype=mime_type, resumable=True)
            copied_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        return copied_file.get('id')

    except HttpError as error:
        print(f"An HTTP error occurred while copying {file_name}: {error}")
        return None
    except Exception as error:
        print(f"An unexpected error occurred while copying {file_name}: {error}")
        return None

def copy_folder(service, source_folder_id: str, destination_folder_id: str, folder_name: Optional[str] = None) -> Optional[str]:
    """
    Copy a folder and its contents recursively.

    Args:
        service: Google Drive service object.
        source_folder_id (str): ID of the source folder.
        destination_folder_id (str): ID of the destination folder.
        folder_name (Optional[str]): Name of the folder to create. If None, copies to root of destination.

    Returns:
        Optional[str]: ID of the copied folder, or None if an error occurs.
    """
    try:
        # If folder should be copied to a subfolder at destination
        if folder_name:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [destination_folder_id]
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            new_folder_id = folder.get('id')
        # Copies folder contents to root of destination
        else:
            new_folder_id = destination_folder_id

        # Query for all items inside the source folder
        query = f"'{source_folder_id}' in parents and trashed = false"
        page_token = None

        while True:
            # Get all items within source folder
            results = service.files().list(q=query, 
                                           fields="nextPageToken, files(id, name, mimeType)",
                                           pageToken=page_token,
                                           pageSize=1000).execute()
            items = results.get('files', [])

            for item in items:
                # Recursively copy any subfolders
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    copy_folder(service, item['id'], new_folder_id, item['name'])
                # Copy any files
                else:
                    copy_file(service, item['id'], new_folder_id, item['name'])

            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return new_folder_id

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        return None
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        return None

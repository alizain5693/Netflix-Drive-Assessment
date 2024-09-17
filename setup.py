import os
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def get_drive_service() -> Optional[object]:
    """
    Authenticate and build a Google Drive service object.

    Returns:
        Optional[object]: A Google Drive service object if successful, None otherwise.

    Raises:
        Exception: If there's an error loading or refreshing credentials.
        HttpError: If there's an error building the Drive service.
    """
    userCreds = None

    # Load existing user credentials if available
    if os.path.exists(TOKEN_FILE):
        try:
            userCreds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading credentials from file: {e}")

    # If userCreds are not valid or don't exist
    if not userCreds or not userCreds.valid:
        # If they are expired, refresh
        if userCreds and userCreds.expired and userCreds.refresh_token:
            try:
                userCreds.refresh(Request())
            # Unable to refresh, perform auth flow
            except Exception as e:
                print(f"Error refreshing user credentials: {e}")
                userCreds = perform_auth_flow()
        # No creds available, perform auth flow
        else:
            userCreds = perform_auth_flow()

    # Save valid user credentials back to the token file
    if userCreds and userCreds.valid:
        with open(TOKEN_FILE, 'w') as token:
            token.write(userCreds.to_json())
    else:
        print("Failed to obtain valid user credentials.")
        return None

    # Try to build the Google Drive service with the user credentials
    try:
        return build('drive', 'v3', credentials=userCreds)
    except HttpError as error:
        print(f"Error building Drive service: {error}")
        return None

def perform_auth_flow() -> Optional[Credentials]:
    """
    Perform the OAuth2 authentication flow.

    Returns:
        Optional[Credentials]: The authenticated user credentials if successful, None otherwise.

    Raises:
        Exception: If there's an error during the authentication flow.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        return flow.run_local_server(port=0)
    except Exception as e:
        print(f"Error during authentication flow: {e}")
        return None

def test_authentication() -> bool:
    """
    Test the authentication process and print user information if successful.

    Returns:
        bool: True if authentication is successful, False otherwise.

    Raises:
        HttpError: If there's an error retrieving user information.
    """
    service = get_drive_service()
    if not service:
        print("Authentication failed. Please check your credentials and try again.")
        return False

    try:
        about = service.about().get(fields="user").execute()
        print(f"Authentication successful. Authenticated as: {about['user']['displayName']}")
        return True
    except HttpError as e:
        print(f"Error retrieving user information: {e}")
        return False

if __name__ == '__main__':
    if test_authentication():
        print("Setup completed successfully.")
    else:
        print("Setup failed. Please check your credentials and try again.")
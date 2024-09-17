# Google Drive Assessment Project

This project provides Python scripts to perform various assessments on Google Drive folders, including file and folder counting, report generation, and folder structure copying.

## Features

- Count files and folders in the root of a source folder
- Generate detailed reports on child objects for each top-level folder
- Copy entire folder structures from a source to a destination folder

## Project Structure

- `setup.py`: Handles Google Drive API authentication
- `drive_utils.py`: Contains utility functions for interacting with Google Drive
- `assessment1.py`: Counts files and folders in the source folder root
- `assessment2.py`: Generates a report on child objects in top-level folders
- `assessment3.py`: Copies the source folder structure to a destination folder

## Prerequisites

- Python 3.7 or higher
- Google Cloud Project with the Google Drive API enabled
- OAuth 2.0 credentials for a desktop application

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/google-drive-assessment.git
   cd google-drive-assessment
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up Google Cloud Project and Credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Drive API for your project
   - Create credentials for a desktop application:
     - Navigate to "APIs & Services" > "Credentials"
     - Click "Create Credentials" > "OAuth client ID"
     - Select "Desktop app" as the application type
     - Download the credentials JSON file
   - Rename the downloaded file to `credentials.json` and place it in the project root directory

4. Create a `.env` file in the project root with the following content:
   ```
   SOURCE_FOLDER_ID=your_source_folder_id
   DESTINATION_FOLDER_ID=your_destination_folder_id
   ```
   Replace the placeholder values with your actual Google Drive folder IDs.

## Usage

You can run each assessment individually:

1. Count files and folders in the source folder root:
   ```
   python assessment1.py
   ```

2. Generate a report on child objects in top-level folders:
   ```
   python assessment2.py
   ```

3. Copy the source folder structure to the destination folder:
   ```
   python assessment3.py
   ```

## Output

- Assessments 1 and 2 generate JSON reports (`report1.json` and `report2.json`) in the project directory.
- Assessment 3 provides console output on the folder copying progress.
- All assessments print formatted results to the console.

## Authentication

The project uses OAuth 2.0 for authentication with the Google Drive API. On the first run, you'll be prompted to authorize the application. The resulting token will be saved to `token.json` for future use.

## Error Handling

The scripts include error handling for common issues such as authentication problems or API errors. Check the console output for any error messages or warnings during execution.

## Limitations

- The scripts use pagination to handle large folders, but processing extremely large folder structures may still take considerable time.
- Google Workspace files (Docs, Sheets, etc.) are handled differently during the copy process to maintain their integrity.

## Contributing

Contributions to improve the scripts or extend their functionality are welcome. Please submit a pull request with your proposed changes.

## Author

Zain Ali
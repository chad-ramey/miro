"""
Script: Miro Boards Export to CSV

Description:
This script exports the list of boards from Miro to a CSV file.
The exported CSV file includes details such as Board ID, Name, Owner, Created At, Modified At, and Link.

Functions:
- fetch_boards: Fetches boards from the Miro account using the API with pagination support.
- export_to_csv: Exports the fetched board data to a CSV file.

Usage:
1. Run the script.
2. Enter the path to the text file containing the Miro API token when prompted.
3. The script will export the board data to 'miro_boards_export.csv'.

Notes:
- Ensure the API token has the necessary permissions to access and export board information.
- Handle the API token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: December 19, 2024
"""

import requests
import csv
import os

def fetch_boards(api_token):
    """
    Fetch all boards from Miro using the API.

    :param api_token: Miro API token with necessary permissions.
    :return: List of boards with their details.
    """
    url = "https://api.miro.com/v2/boards"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    boards = []
    params = {
        "limit": 50  # Adjusted to comply with API restrictions
    }

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        try:
            data = response.json()
        except ValueError:
            print("Error: Failed to parse JSON response.")
            break

        boards.extend(data.get("data", []))

        next_link = data.get("links", {}).get("next")
        if next_link:
            url = next_link
        else:
            break

    return boards

def export_to_csv(boards, output_file):
    """
    Export board details to a CSV file.

    :param boards: List of boards.
    :param output_file: Path to the output CSV file.
    """
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Writing header
        writer.writerow(["Board ID", "Name", "Owner", "Created At", "Modified At", "Link"])

        for board in boards:
            writer.writerow([
                board.get("id"),
                board.get("name"),
                board.get("owner", {}).get("name"),
                board.get("createdAt"),
                board.get("modifiedAt"),
                board.get("viewLink")
            ])

def main():
    """
    Main function to fetch and export Miro boards.
    """
    print("\n--- Miro Boards Export Script ---")
    token_file_path = input("Enter the path to the text file containing your Miro API token: ").strip()

    if not os.path.isfile(token_file_path):
        print("Error: File not found. Exiting...")
        return

    try:
        with open(token_file_path, 'r') as token_file:
            api_token = token_file.read().strip()
    except Exception as e:
        print(f"Error: Unable to read token file ({e}). Exiting...")
        return

    if not api_token:
        print("Error: API token is required. Exiting...")
        return

    print("Fetching boards from Miro...")
    boards = fetch_boards(api_token)

    if not boards:
        print("No boards found or an error occurred.")
        return

    output_file = "miro_boards_export.csv"
    print(f"Exporting boards to {output_file}...")
    export_to_csv(boards, output_file)
    print("Export completed.")

if __name__ == "__main__":
    main()

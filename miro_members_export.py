"""
Script: Miro Organization Members Export to CSV

Description:
This script exports the list of organization members from Miro to a CSV file.
The exported CSV file includes details such as ID, Active Status, Admin Roles, Email, Last Activity, License, License Assigned Date, Role, and Type.

Functions:
- fetch_members: Fetches members from the Miro organization using the API with cursor-based pagination.
- export_to_csv: Exports the fetched member data to a CSV file.

Usage:
1. Run the script.
2. Enter the path to the text file containing the Miro API token when prompted.
3. The script will export the member data to 'miro_users_export.csv'.

Notes:
- Ensure the API token has the necessary permissions to access and export user information.
- Handle the API token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import csv
import os

def fetch_members(api_token):
    """
    Fetch members from the Miro organization using the API with pagination support.
    
    Args:
        api_token (str): The Miro API token.

    Returns:
        list: A list of members with their details.
    """
    url = "https://api.miro.com/v2/orgs/{org_id}/members"
    org_id = input("Enter your Miro Organization ID: ").strip()
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }

    members = []
    cursor = None

    print("Fetching Miro organization members...")

    while True:
        params = {"cursor": cursor} if cursor else {}
        response = requests.get(url.format(org_id=org_id), headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: Unable to fetch data (Status Code {response.status_code}): {response.text}")
            break

        data = response.json()
        members.extend(data.get("data", []))

        cursor = data.get("cursor")
        if not cursor:
            break

        print("Fetching next page...")

    print(f"Fetched {len(members)} members.")
    return members

def export_to_csv(members, filename):
    """
    Export members to a CSV file.

    Args:
        members (list): List of member dictionaries.
        filename (str): Name of the output CSV file.
    """
    print(f"Exporting data to {filename}...")
    fieldnames = ["id", "active", "adminRoles", "email", "lastActivityAt", "license", "licenseAssignedAt", "role", "type"]
    
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for member in members:
            admin_roles = member.get("adminRoles", [])
            admin_roles_str = ", ".join([str(role) if isinstance(role, str) else str(role) for role in admin_roles])
            writer.writerow({
                "id": member.get("id"),
                "active": member.get("active"),
                "adminRoles": admin_roles_str,
                "email": member.get("email"),
                "lastActivityAt": member.get("lastActivityAt", "N/A"),
                "license": member.get("license"),
                "licenseAssignedAt": member.get("licenseAssignedAt", "N/A"),
                "role": member.get("role"),
                "type": member.get("type")
            })

    print(f"Data successfully exported to {filename}.")

def main():
    """
    Main function to execute the script.
    """
    print("\n--- Miro Organization Members Export Script ---")
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

    members = fetch_members(api_token)
    if members:
        export_to_csv(members, "miro_users_export.csv")
    else:
        print("No members data fetched.")

if __name__ == "__main__":
    main()

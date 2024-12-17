"""
Script: miro_license_monitor - Monitor Miro License Usage and Send Alerts

Description:
This script monitors Miro license usage by fetching all organization members using the Miro API.
It filters active users with a "full" license and compares the count against a predefined total.
Alerts are sent to a Slack channel if license usage exceeds the total allocated.

Functions:
- fetch_members: Fetches Miro organization members with pagination.
- post_to_slack: Sends a message to a Slack channel via webhook.
- main: Main function to calculate license usage and send alerts.

Usage:
1. Set the following environment variables:
   - `MIRO_API_TOKEN`: Miro API token with org member access.
   - `MIRO_ORG_ID`: Miro Organization ID.
   - `SLACK_WEBHOOK_URL`: Webhook URL for Slack alerts.
2. Run the script in a Python environment or via GitHub Actions.

Notes:
- Ensure the API token and Organization ID are valid and have sufficient permissions.
- Adjust the `total_licenses` variable to reflect your organization's license allocation.

Author: Chad Ramey
Date: December 11, 2024
"""

import os
import requests

def fetch_members(api_token, org_id):
    """
    Fetch members from the Miro organization using API pagination.
    Args:
        api_token (str): Miro API token.
        org_id (str): Miro Organization ID.
    Returns:
        list: List of member dictionaries.
    """
    url = f"https://api.miro.com/v2/orgs/{org_id}/members"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }

    members = []
    cursor = None

    while True:
        params = {"cursor": cursor} if cursor else {}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        members.extend(data.get("data", []))
        cursor = data.get("cursor")

        if not cursor:
            break

    return members

def post_to_slack(webhook_url, message):
    """Send a message to Slack via webhook."""
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

def main():
    """Main function to monitor Miro licenses and send Slack alerts."""
    # Environment variables
    api_token = os.getenv("MIRO_API_TOKEN")
    org_id = os.getenv("MIRO_ORG_ID")
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    total_licenses = 600  # Total allocated licenses

    if not api_token or not org_id or not slack_webhook_url:
        raise ValueError("Environment variables MIRO_API_TOKEN, MIRO_ORG_ID, and SLACK_WEBHOOK_URL are required.")

    # Fetch all organization members
    members = fetch_members(api_token, org_id)

    # Filter licensed users: active = true and license = "full"
    licensed_users = [member for member in members if member.get("active") and member.get("license") == "full"]
    used_licenses = len(licensed_users)
    available_licenses = total_licenses - used_licenses

    # Generate Slack message
    if used_licenses > total_licenses:
        alert_message = (
            f":rotating_light::miro: *Miro License Alert* :miro::rotating_light:\n"
            f"Used Licenses: {used_licenses}\n"
            f"Total Licenses: {total_licenses}\n"
            f"Overage: {used_licenses - total_licenses}\n"
            f"*Immediate action required to resolve the overage.*"
        )
    else:
        alert_message = (
            f":miro: *Miro License Report* :miro:\n"
            f"Used Licenses: {used_licenses}\n"
            f"Total Licenses: {total_licenses}\n"
            f"Available Licenses: {available_licenses}\n"
            f"*All licenses are within the allocated limit.*"
        )

    # Send message to Slack
    post_to_slack(slack_webhook_url, alert_message)

if __name__ == "__main__":
    main()

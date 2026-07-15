#!/usr/bin/env python3
"""
List all lead gen forms on the LinkedIn Ads account.

Usage:
    python list_lead_forms.py
    python list_lead_forms.py --account-id 111222333
"""

import argparse
import sys
import urllib.parse
from client import get_session, get_account_id, BASE_URL
from tabulate import tabulate


def list_lead_forms(account_id=None):
    session = get_session()
    account_id = account_id or get_account_id()

    owner = f"(sponsoredAccount:urn:li:sponsoredAccount:{account_id})"
    resp = session.get(f"{BASE_URL}/leadForms?q=owner&owner={urllib.parse.quote(owner, safe='()')}&count=100")
    if resp.status_code != 200:
        print(f"ERROR: Failed to fetch lead forms: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    forms = data.get("elements", [])

    if not forms:
        print("No lead gen forms found.")
        return

    rows = []
    for form in forms:
        form_id = form.get("id", "N/A")
        name = form.get("name", "N/A")
        state = form.get("state", form.get("status", "UNKNOWN"))
        content = form.get("content", {})
        headline = content.get("headline", {}).get("localized", {}).get("en_US", "-")
        questions = content.get("questions", [])
        rows.append([form_id, name[:40], state, headline[:35] if headline else "-", len(questions)])

    headers = ["Form ID", "Name", "State", "Headline", "Fields"]

    print(f"\nLead Gen Forms for account {account_id}")
    print(tabulate(rows, headers=headers, tablefmt="simple"))
    print(f"\nTotal: {len(rows)} forms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List LinkedIn Ads lead gen forms")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    list_lead_forms(args.account_id)

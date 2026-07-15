#!/usr/bin/env python3
"""
Create a new LinkedIn Ads campaign group.

A campaign group is the container that holds campaigns. Creating one first
lets you organize campaigns and (optionally) share a lifetime budget across
them.

Usage:
    python create_campaign_group.py --name "Q2 Lead Gen"
    python create_campaign_group.py --name "Brand - 2026" --total-budget 500000 --end-date 2026-12-31
    python create_campaign_group.py --name "Always On" --status PAUSED --account-id 123456789

Budget amounts are in CENTS (e.g., 500000 = $5,000.00).
Campaign group always starts in DRAFT (or PAUSED) so nothing serves until you review.
"""

import argparse
import sys
import time
from datetime import datetime

from client import get_session, get_account_id, BASE_URL


def to_millis(date_str: str) -> int:
    """Convert a YYYY-MM-DD string to epoch milliseconds."""
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)


def create_campaign_group(args):
    session = get_session()
    account_id = args.account_id or get_account_id()

    if args.total_budget is not None and not args.end_date:
        print("ERROR: --end-date is required when --total-budget is set.")
        sys.exit(1)

    start_millis = to_millis(args.start_date) if args.start_date else int(time.time() * 1000)

    payload = {
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "name": args.name,
        "status": args.status,
        "runSchedule": {"start": start_millis},
    }

    if args.end_date:
        payload["runSchedule"]["end"] = to_millis(args.end_date)

    if args.total_budget is not None:
        payload["totalBudget"] = {
            "amount": str(args.total_budget),
            "currencyCode": args.currency,
        }

    resp = session.post(f"{BASE_URL}/adAccounts/{account_id}/adCampaignGroups", json=payload)

    if resp.status_code == 201:
        group_id = resp.headers.get("x-restli-id", "unknown")
        print(f"\nCampaign group created successfully!")
        print(f"  ID:     {group_id}")
        print(f"  Name:   {args.name}")
        print(f"  Status: {args.status}")
        if args.total_budget is not None:
            print(f"  Total Budget: ${args.total_budget / 100:,.2f} {args.currency}")
        print(f"\nNext step:")
        print(f"  Create campaigns under it:")
        print(f"    python create_campaign.py --name \"...\" --campaign-group-id {group_id} --objective LEAD_GENERATION --daily-budget 5000")
    else:
        print(f"ERROR: Failed to create campaign group: {resp.status_code}")
        print(resp.text)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new LinkedIn Ads campaign group")
    parser.add_argument("--name", required=True, help="Campaign group name (max 100 chars)")
    parser.add_argument("--status", default="DRAFT", choices=["DRAFT", "PAUSED", "ACTIVE"],
                        help="Initial status (default: DRAFT - nothing serves until reviewed)")
    parser.add_argument("--total-budget", type=int,
                        help="Lifetime budget in cents (requires --end-date)")
    parser.add_argument("--currency", default="USD", help="Currency code (default: USD, must match account)")
    parser.add_argument("--start-date", help="Start date YYYY-MM-DD (default: now)")
    parser.add_argument("--end-date", help="End date YYYY-MM-DD (required if --total-budget set)")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    create_campaign_group(args)

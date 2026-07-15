#!/usr/bin/env python3
"""
Attach conversion tracking to a LinkedIn Ads campaign.

LinkedIn does not attach account conversions to new campaigns automatically.
This script associates conversions (defined at the account level via the
Insight Tag) with a campaign so the campaign reports conversions and can
optimize toward them.

Usage:
    python attach_conversions.py --campaign-id 123456                 # Attach ALL enabled account conversions
    python attach_conversions.py --campaign-id 123456 --conversion-id 987654 --conversion-id 987655
    python attach_conversions.py --list                               # Just list account conversions
    python attach_conversions.py --campaign-id 123456 --account-id 111222333

Conversion association is a PUT and does not spend budget.
"""

import argparse
import sys
import urllib.parse

from client import get_session, get_account_id, BASE_URL


def list_account_conversions(session, account_id):
    """Return all conversions defined on the account."""
    enc_acct = urllib.parse.quote(f"urn:li:sponsoredAccount:{account_id}", safe="")
    conversions = []
    start = 0
    while True:
        resp = session.get(
            f"{BASE_URL}/conversions?q=account&account={enc_acct}&start={start}&count=100"
        )
        if resp.status_code != 200:
            print(f"ERROR: Failed to list conversions: {resp.status_code}")
            print(resp.text)
            sys.exit(1)
        data = resp.json()
        elements = data.get("elements", [])
        conversions.extend(elements)
        links = data.get("paging", {}).get("links", [])
        if not elements or not any(l.get("rel") == "next" for l in links):
            break
        start += 100
    return conversions


def attach(session, account_id, campaign_id, conversion_ids):
    campaign_urn = f"urn:li:sponsoredCampaign:{campaign_id}"
    enc_campaign = urllib.parse.quote(campaign_urn, safe="")

    ok, fail = 0, 0
    for conv_id in conversion_ids:
        conv_urn = f"urn:lla:llaPartnerConversion:{conv_id}"
        enc_conv = urllib.parse.quote(conv_urn, safe="")
        url = f"{BASE_URL}/campaignConversions/(campaign:{enc_campaign},conversion:{enc_conv})"
        resp = session.put(url, json={"campaign": campaign_urn, "conversion": conv_urn})
        if resp.status_code in (200, 201, 204):
            ok += 1
            print(f"  Attached conversion {conv_id}")
        else:
            fail += 1
            print(f"  FAILED conversion {conv_id}: {resp.status_code} {resp.text[:200]}")
    print(f"\nDone. {ok} attached, {fail} failed on campaign {campaign_id}.")


def main():
    parser = argparse.ArgumentParser(description="Attach conversions to a LinkedIn Ads campaign")
    parser.add_argument("--campaign-id", type=int, help="Campaign ID to attach conversions to")
    parser.add_argument("--conversion-id", action="append", type=int,
                        help="Specific conversion ID (repeatable). Default: all enabled account conversions")
    parser.add_argument("--list", action="store_true", help="List account conversions and exit")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()

    session = get_session()
    account_id = args.account_id or get_account_id()

    conversions = list_account_conversions(session, account_id)

    if args.list or not args.campaign_id:
        if not conversions:
            print("No conversions defined on this account.")
            return
        print(f"\nAccount conversions ({account_id}):")
        for c in conversions:
            state = "enabled" if c.get("enabled") else "disabled"
            print(f"  {c.get('id')}  {c.get('name', '(unnamed)')}  [{state}]")
        if not args.campaign_id:
            print("\nPass --campaign-id to attach these to a campaign.")
        return

    if args.conversion_id:
        conversion_ids = args.conversion_id
    else:
        conversion_ids = [c["id"] for c in conversions if c.get("enabled")]
        if not conversion_ids:
            print("No enabled conversions to attach. Use --conversion-id to force specific ones.")
            sys.exit(1)

    attach(session, account_id, args.campaign_id, conversion_ids)


if __name__ == "__main__":
    main()

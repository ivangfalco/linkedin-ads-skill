#!/usr/bin/env python3
"""
Create a Thought Leader Ad by promoting an existing post.

A Thought Leader Ad (TLA) sponsors a post authored by a person or your company
Page. This script attaches an existing post (by its share or ugcPost URN) as a
creative under a campaign, which is the API-doable half of the workflow.

Usage:
    python create_thought_leader_ad.py --campaign-id 123456 \
        --post-urn "urn:li:share:7300000000000000000" \
        --name "TLA | Founder POV"

    python create_thought_leader_ad.py --campaign-id 123456 \
        --post-urn "urn:li:ugcPost:7300000000000000000" --name "TLA | Team Post"

Campaign requirements: objective ENGAGEMENT or BRAND_AWARENESS, and format
STANDARD_UPDATE (single image) or SINGLE_VIDEO (video). Format is set at
campaign creation and cannot be changed later.

IMPORTANT: This promotes a post you already have the share/ugcPost URN for.
Promoting a *member's organic* post that you only have the feed URL for
(the "-activity-<id>" URL) is NOT possible through the API - LinkedIn provides
no way to resolve an activity ID to a share URN, and API access to arbitrary
member posts is restricted. That path must be done in Campaign Manager
(Create ad -> Browse existing content -> LinkedIn members).

The creative is created PAUSED so nothing serves until you review and enable it.
"""

import argparse
import sys

from client import get_session, get_account_id, BASE_URL


VALID_PREFIXES = ("urn:li:share:", "urn:li:ugcPost:")


def create_thought_leader_ad(args):
    session = get_session()
    account_id = args.account_id or get_account_id()

    if not args.post_urn.startswith(VALID_PREFIXES):
        print("ERROR: --post-urn must be a urn:li:share:{id} or urn:li:ugcPost:{id}.")
        print("A feed URL containing '-activity-<id>' cannot be used - see the header of this script.")
        sys.exit(1)

    payload = {
        "campaign": f"urn:li:sponsoredCampaign:{args.campaign_id}",
        "content": {"reference": args.post_urn},
        "intendedStatus": "PAUSED",
        "name": args.name,
    }

    resp = session.post(f"{BASE_URL}/adAccounts/{account_id}/creatives", json=payload)

    if resp.status_code == 201:
        creative = resp.headers.get("x-restli-id", "unknown")
        print(f"\nThought Leader Ad created successfully (PAUSED)!")
        print(f"  Creative: {creative}")
        print(f"  Campaign: {args.campaign_id}")
        print(f"  Post:     {args.post_urn}")
        print(f"\nReview it in Campaign Manager, then enable.")
    else:
        print(f"ERROR: Failed to create Thought Leader Ad: {resp.status_code}")
        print(resp.text)
        print("\nCommon causes: the campaign format is not STANDARD_UPDATE/SINGLE_VIDEO,")
        print("the objective is not ENGAGEMENT/BRAND_AWARENESS, or the post is not")
        print("available for sponsoring (author not added to the account / auto-approval off).")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promote an existing post as a Thought Leader Ad")
    parser.add_argument("--campaign-id", required=True, type=int,
                        help="TLA-compatible campaign ID (ENGAGEMENT/BRAND_AWARENESS)")
    parser.add_argument("--post-urn", required=True,
                        help="Existing post URN (urn:li:share:{id} or urn:li:ugcPost:{id})")
    parser.add_argument("--name", default="Thought Leader Ad", help="Creative name for reference")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    create_thought_leader_ad(args)

#!/usr/bin/env python3
"""
Create a LinkedIn carousel ad (2-10 cards).

Uploads one image per card, builds a carousel sponsored post, and attaches it
as a creative under a campaign. The campaign should be a carousel-format
campaign (format CAROUSEL).

Each card is passed as: IMAGE_PATH|HEADLINE|LANDING_URL

Usage:
    python create_carousel_ad.py --campaign-id 123456 \
        --body "Swipe through the 3-step playbook." \
        --name "TOF | Carousel | Playbook" \
        --card "./card1.png|Step 1: Connect|https://example.com/step-1" \
        --card "./card2.png|Step 2: Model|https://example.com/step-2" \
        --card "./card3.png|Step 3: Decide|https://example.com/step-3"

The creative is created PAUSED so nothing serves until you review and enable it.
"""

import argparse
import sys
import time
import urllib.parse

from client import get_session, get_account_id, BASE_URL
from config import get_config


def upload_image(session, org_urn, image_path):
    init = session.post(
        f"{BASE_URL}/images?action=initializeUpload",
        json={"initializeUploadRequest": {"owner": org_urn}},
    )
    if init.status_code != 200:
        raise RuntimeError(f"Image init failed: {init.status_code} {init.text[:300]}")
    value = init.json()["value"]
    upload_url, image_urn = value["uploadUrl"], value["image"]

    with open(image_path, "rb") as f:
        token = session.headers["Authorization"]
        up = session.put(upload_url, headers={"Authorization": token}, data=f.read())
    if up.status_code not in (200, 201):
        raise RuntimeError(f"Image upload failed: {up.status_code} {up.text[:300]}")

    enc = urllib.parse.quote(image_urn, safe="")
    for _ in range(20):
        status = session.get(f"{BASE_URL}/images/{enc}").json().get("status")
        if status == "AVAILABLE":
            return image_urn
        time.sleep(2)
    raise RuntimeError("Timed out waiting for image to become AVAILABLE")


def parse_card(raw):
    parts = raw.split("|")
    if len(parts) != 3:
        raise ValueError(f"Card must be IMAGE_PATH|HEADLINE|LANDING_URL, got: {raw!r}")
    image_path, headline, url = (p.strip() for p in parts)
    return {"image": image_path, "headline": headline, "url": url}


def create_post(session, org_urn, account_id, body, cards):
    payload = {
        "author": org_urn,
        "lifecycleState": "PUBLISHED",
        "visibility": "PUBLIC",
        "commentary": body,
        "distribution": {"feedDistribution": "NONE", "thirdPartyDistributionChannels": []},
        "content": {"carousel": {"cards": cards}},
        "adContext": {"dscAdAccount": f"urn:li:sponsoredAccount:{account_id}", "dscStatus": "ACTIVE"},
    }
    r = session.post(f"{BASE_URL}/posts", json=payload)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Post creation failed: {r.status_code} {r.text[:300]}")
    return r.headers.get("x-restli-id")


def create_creative(session, account_id, campaign_id, post_urn, name):
    payload = {
        "campaign": f"urn:li:sponsoredCampaign:{campaign_id}",
        "content": {"reference": post_urn},
        "intendedStatus": "PAUSED",
        "name": name,
    }
    r = session.post(f"{BASE_URL}/adAccounts/{account_id}/creatives", json=payload)
    if r.status_code != 201:
        raise RuntimeError(f"Creative creation failed: {r.status_code} {r.text[:300]}")
    return r.headers.get("x-restli-id")


def main():
    parser = argparse.ArgumentParser(description="Create a LinkedIn carousel ad (2-10 cards)")
    parser.add_argument("--campaign-id", required=True, help="Campaign ID to attach the ad to")
    parser.add_argument("--card", action="append", required=True,
                        help="Card as IMAGE_PATH|HEADLINE|LANDING_URL (repeatable, 2-10 cards)")
    parser.add_argument("--body", default="", help="Post commentary / ad body text")
    parser.add_argument("--name", default="Carousel Ad", help="Creative name for reference")
    parser.add_argument("--org-id", help="Override the organization (Page) ID from config/.env")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()

    try:
        parsed_cards = [parse_card(c) for c in args.card]
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not (2 <= len(parsed_cards) <= 10):
        print(f"ERROR: carousel needs 2 to 10 cards, got {len(parsed_cards)}.")
        sys.exit(1)

    org_id = args.org_id or get_config().get("org_id")
    if not org_id:
        print("ERROR: LINKEDIN_ORG_ID is not set in .env (your company Page's organization ID).")
        print("Pass --org-id or add it to .env.")
        sys.exit(1)
    org_urn = f"urn:li:organization:{org_id}"

    session = get_session()
    account_id = args.account_id or get_account_id()

    print(f"1. Uploading {len(parsed_cards)} card images...")
    cards = []
    for i, card in enumerate(parsed_cards, 1):
        image_urn = upload_image(session, org_urn, card["image"])
        cards.append({
            "media": {"id": image_urn, "title": card["headline"]},
            "landingPage": card["url"],
        })
        print(f"   card {i}: {image_urn}")

    print("2. Creating carousel post...")
    post_urn = create_post(session, org_urn, account_id, args.body, cards)
    print(f"   {post_urn}")
    print("3. Creating creative (PAUSED)...")
    creative = create_creative(session, account_id, args.campaign_id, post_urn, args.name)
    print(f"   {creative}")
    print("\nDone. The carousel ad is PAUSED - review it in Campaign Manager, then enable.")


if __name__ == "__main__":
    main()

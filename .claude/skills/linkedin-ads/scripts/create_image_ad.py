#!/usr/bin/env python3
"""
Create a single-image LinkedIn ad.

Uploads an image, creates the sponsored post, and attaches it as a creative
under a campaign. The creative is created PAUSED so nothing spends until you
review and enable it.

Single ad:
    python create_image_ad.py --campaign-id 123456 \
        --image ./creative.png --headline "6-8 hours on reporting. 15 minutes now." \
        --body "How 200 finance teams cut reporting time." \
        --url "https://yoursite.com/demo" --name "TOF | Single Image | Reporting"

Bulk (one row per ad):
    python create_image_ad.py --csv ads.csv
    # CSV columns: campaign_id,image,headline,body,url,name

UTM params are appended to the destination URL when provided.
"""

import argparse
import csv
import sys
import time
import urllib.parse

from client import get_session, get_account_id, BASE_URL
from config import get_config


def with_utm(url, source, medium, campaign):
    params = {}
    if source:
        params["utm_source"] = source
    if medium:
        params["utm_medium"] = medium
    if campaign:
        params["utm_campaign"] = campaign
    if not params:
        return url
    sep = "&" if "?" in url else "?"
    return url + sep + urllib.parse.urlencode(params)


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


def create_post(session, org_urn, account_id, headline, body, url, image_urn):
    payload = {
        "author": org_urn,
        "lifecycleState": "PUBLISHED",
        "visibility": "PUBLIC",
        "commentary": body,
        "distribution": {"feedDistribution": "NONE", "thirdPartyDistributionChannels": []},
        "content": {"article": {"title": headline, "source": url, "thumbnail": image_urn}},
        "adContext": {"dscAdAccount": f"urn:li:sponsoredAccount:{account_id}", "dscStatus": "ACTIVE"},
    }
    r = session.post(f"{BASE_URL}/posts", json=payload)
    if r.status_code != 201:
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


def build_one(session, account_id, org_urn, row):
    url = with_utm(row["url"], row.get("utm_source"), row.get("utm_medium"), row.get("utm_campaign"))
    image_urn = upload_image(session, org_urn, row["image"])
    post_urn = create_post(session, org_urn, account_id, row["headline"], row["body"], url, image_urn)
    creative = create_creative(session, account_id, row["campaign_id"], post_urn, row["name"])
    print(f"  Created (PAUSED): {row['name']} -> {creative}")
    return creative


def main():
    parser = argparse.ArgumentParser(description="Create single-image LinkedIn ads (single or bulk)")
    parser.add_argument("--csv", help="CSV file for bulk: campaign_id,image,headline,body,url,name[,utm_source,utm_medium,utm_campaign]")
    parser.add_argument("--campaign-id")
    parser.add_argument("--image")
    parser.add_argument("--headline")
    parser.add_argument("--body", default="")
    parser.add_argument("--url")
    parser.add_argument("--name", default="Single Image Ad")
    parser.add_argument("--utm-source")
    parser.add_argument("--utm-medium")
    parser.add_argument("--utm-campaign")
    args = parser.parse_args()

    org_id = get_config().get("org_id")
    if not org_id:
        print("ERROR: LINKEDIN_ORG_ID is not set in .env. It's your company Page's organization ID,")
        print("needed to host the ad creative. Run /onboarding or add it manually.")
        sys.exit(1)
    org_urn = f"urn:li:organization:{org_id}"

    session = get_session()
    account_id = get_account_id()

    if args.csv:
        with open(args.csv, newline="") as f:
            rows = list(csv.DictReader(f))
        print(f"Creating {len(rows)} ads (all PAUSED)...")
        created = 0
        for i, row in enumerate(rows, 1):
            try:
                print(f"[{i}/{len(rows)}] {row.get('name', '')}")
                build_one(session, account_id, org_urn, row)
                created += 1
            except Exception as e:
                print(f"  SKIPPED: {e}")
        print(f"\nDone. {created}/{len(rows)} created. Review them in Campaign Manager, then enable.")
        return

    required = [args.campaign_id, args.image, args.headline, args.url]
    if not all(required):
        print("ERROR: single mode needs --campaign-id, --image, --headline, and --url (or use --csv).")
        sys.exit(1)
    build_one(session, account_id, org_urn, {
        "campaign_id": args.campaign_id, "image": args.image, "headline": args.headline,
        "body": args.body, "url": args.url, "name": args.name,
        "utm_source": args.utm_source, "utm_medium": args.utm_medium, "utm_campaign": args.utm_campaign,
    })
    print("\nDone. The ad is PAUSED - review it in Campaign Manager, then enable.")


if __name__ == "__main__":
    main()

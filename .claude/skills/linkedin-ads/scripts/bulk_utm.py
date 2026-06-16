#!/usr/bin/env python3
"""
Bulk-add UTM parameters to the destination URLs of existing single-image ads.

LinkedIn won't rewrite the link on a live post, so for each creative in the
selected campaigns this builds a fresh post with the UTM-tagged URL, attaches
it as a new PAUSED creative, and pauses the old one. Nothing is deleted, and
nothing new spends until you enable it.

Examples:
    python bulk_utm.py --campaign-ids 111,222 \
        --utm-source linkedin --utm-medium paid_social --utm-campaign q2_abm

    python bulk_utm.py --campaign-ids 111 --utm-source linkedin --pause-old
"""

import argparse
import sys
import urllib.parse

from client import get_session, get_account_id, BASE_URL
from config import get_config
from create_image_ad import with_utm, create_post, create_creative

FINDER = {"X-RestLi-Method": "FINDER"}
PATCH = {"X-RestLi-Method": "PARTIAL_UPDATE"}


def creatives_in_campaign(session, account_id, campaign_id):
    enc = urllib.parse.quote(f"urn:li:sponsoredCampaign:{campaign_id}", safe="")
    r = session.get(
        f"{BASE_URL}/adAccounts/{account_id}/creatives?q=criteria&campaigns=List({enc})&pageSize=50",
        headers={**session.headers, **FINDER},
    )
    r.raise_for_status()
    return r.json().get("elements", [])


def get_post(session, post_urn):
    enc = urllib.parse.quote(post_urn, safe="")
    r = session.get(f"{BASE_URL}/posts/{enc}")
    r.raise_for_status()
    return r.json()


def pause_creative(session, account_id, creative_urn):
    enc = urllib.parse.quote(creative_urn, safe="")
    session.post(
        f"{BASE_URL}/adAccounts/{account_id}/creatives/{enc}",
        headers={**session.headers, **PATCH},
        json={"patch": {"$set": {"intendedStatus": "PAUSED"}}},
    )


def main():
    p = argparse.ArgumentParser(description="Bulk-add UTM params to existing single-image ads")
    p.add_argument("--campaign-ids", required=True, help="Comma-separated campaign IDs")
    p.add_argument("--utm-source")
    p.add_argument("--utm-medium")
    p.add_argument("--utm-campaign")
    p.add_argument("--pause-old", action="store_true", help="Pause the original creatives after creating the tagged copies")
    args = p.parse_args()

    if not any([args.utm_source, args.utm_medium, args.utm_campaign]):
        print("ERROR: pass at least one of --utm-source / --utm-medium / --utm-campaign.")
        sys.exit(1)

    org_id = get_config().get("org_id")
    if not org_id:
        print("ERROR: LINKEDIN_ORG_ID is not set in .env (needed to host the new creatives).")
        sys.exit(1)
    org_urn = f"urn:li:organization:{org_id}"

    session = get_session()
    account_id = get_account_id()
    made = 0
    for cid in [c.strip() for c in args.campaign_ids.split(",") if c.strip()]:
        for cr in creatives_in_campaign(session, account_id, cid):
            ref = cr.get("content", {}).get("reference", "")
            if not ref.startswith("urn:li:share") and not ref.startswith("urn:li:ugcPost"):
                continue
            try:
                post = get_post(session, ref)
                article = post.get("content", {}).get("article", {})
                url = article.get("source")
                if not url:
                    continue
                new_url = with_utm(url, args.utm_source, args.utm_medium, args.utm_campaign)
                new_post = create_post(
                    session, org_urn, account_id,
                    article.get("title", ""), post.get("commentary", ""), new_url, article.get("thumbnail"),
                )
                new_creative = create_creative(
                    session, account_id, cid, new_post, f"{cr.get('name', 'Creative')} [UTM]",
                )
                if args.pause_old:
                    pause_creative(session, account_id, cr.get("id"))
                made += 1
                print(f"  {cid}: tagged copy created (PAUSED) -> {new_creative}")
            except Exception as e:
                print(f"  {cid}: SKIPPED a creative ({e})")
    print(f"\nDone. {made} UTM-tagged copies created (PAUSED). Review, then enable and pause the originals.")


if __name__ == "__main__":
    main()

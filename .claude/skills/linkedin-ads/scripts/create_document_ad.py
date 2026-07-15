#!/usr/bin/env python3
"""
Create a LinkedIn document (PDF) ad.

Uploads a PDF, creates a sponsored post that hosts it, and attaches it as a
creative under a campaign. The campaign the creative lives under should be a
document-format campaign (format SPONSORED_UPDATE_NATIVE_DOCUMENT).

Usage:
    python create_document_ad.py --campaign-id 123456 \
        --file ./whitepaper.pdf --title "2026 Benchmark Report" \
        --body "What 200 teams learned about reporting." \
        --name "TOF | Document | Benchmark Report"

    # Gate the document behind a lead form CTA (UNLOCK_FULL_DOCUMENT):
    python create_document_ad.py --campaign-id 123456 --file ./guide.pdf \
        --title "The Playbook" --body "Free download." --name "Gated Doc" \
        --lead-form-id 987654 --cta UNLOCK_FULL_DOCUMENT

The creative is created PAUSED so nothing serves until you review and enable it.
"""

import argparse
import sys
import time
import urllib.parse

from client import get_session, get_account_id, BASE_URL
from config import get_config


def upload_document(session, org_urn, pdf_path):
    init = session.post(
        f"{BASE_URL}/documents?action=initializeUpload",
        json={"initializeUploadRequest": {"owner": org_urn}},
    )
    if init.status_code != 200:
        raise RuntimeError(f"Document init failed: {init.status_code} {init.text[:300]}")
    value = init.json()["value"]
    upload_url, document_urn = value["uploadUrl"], value["document"]

    with open(pdf_path, "rb") as f:
        token = session.headers["Authorization"]
        up = session.put(upload_url, headers={"Authorization": token}, data=f.read())
    if up.status_code not in (200, 201):
        raise RuntimeError(f"Document upload failed: {up.status_code} {up.text[:300]}")

    enc = urllib.parse.quote(document_urn, safe="")
    for _ in range(30):
        status = session.get(f"{BASE_URL}/documents/{enc}").json().get("status")
        if status == "AVAILABLE":
            return document_urn
        time.sleep(2)
    raise RuntimeError("Timed out waiting for document to become AVAILABLE")


def create_post(session, org_urn, account_id, title, body, document_urn, cta, landing_page):
    payload = {
        "author": org_urn,
        "lifecycleState": "PUBLISHED",
        "visibility": "PUBLIC",
        "commentary": body,
        "isReshareDisabledByAuthor": False,
        "distribution": {"feedDistribution": "NONE", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "content": {"media": {"id": document_urn, "title": title}},
        "adContext": {"dscAdAccount": f"urn:li:sponsoredAccount:{account_id}", "dscStatus": "ACTIVE"},
    }
    if cta:
        payload["contentCallToActionLabel"] = cta
    if landing_page:
        payload["contentLandingPage"] = landing_page
    r = session.post(f"{BASE_URL}/posts", json=payload)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Post creation failed: {r.status_code} {r.text[:300]}")
    return r.headers.get("x-restli-id")


def create_creative(session, account_id, campaign_id, post_urn, name, lead_form_id, cta):
    payload = {
        "campaign": f"urn:li:sponsoredCampaign:{campaign_id}",
        "content": {"reference": post_urn},
        "intendedStatus": "PAUSED",
        "name": name,
    }
    if lead_form_id:
        payload["leadgenCallToAction"] = {
            "destination": f"urn:li:adForm:{lead_form_id}",
            "label": cta or "DOWNLOAD",
        }
    r = session.post(f"{BASE_URL}/adAccounts/{account_id}/creatives", json=payload)
    if r.status_code != 201:
        raise RuntimeError(f"Creative creation failed: {r.status_code} {r.text[:300]}")
    return r.headers.get("x-restli-id")


def main():
    parser = argparse.ArgumentParser(description="Create a LinkedIn document (PDF) ad")
    parser.add_argument("--campaign-id", required=True, help="Campaign ID to attach the ad to")
    parser.add_argument("--file", required=True, help="Path to the PDF file")
    parser.add_argument("--title", required=True, help="Document title (shown on the doc card)")
    parser.add_argument("--body", default="", help="Post commentary / ad body text")
    parser.add_argument("--name", default="Document Ad", help="Creative name for reference")
    parser.add_argument("--lead-form-id", help="Lead form ID to gate the document behind (optional)")
    parser.add_argument("--cta", help="CTA label (e.g. DOWNLOAD, UNLOCK_FULL_DOCUMENT, LEARN_MORE)")
    parser.add_argument("--landing-page", help="Landing page URL (required if --cta set without a lead form)")
    parser.add_argument("--org-id", help="Override the organization (Page) ID from config/.env")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()

    org_id = args.org_id or get_config().get("org_id")
    if not org_id:
        print("ERROR: LINKEDIN_ORG_ID is not set in .env (your company Page's organization ID).")
        print("Pass --org-id or add it to .env.")
        sys.exit(1)
    org_urn = f"urn:li:organization:{org_id}"

    session = get_session()
    account_id = args.account_id or get_account_id()

    print("1. Uploading document...")
    document_urn = upload_document(session, org_urn, args.file)
    print(f"   {document_urn}")
    print("2. Creating post...")
    post_urn = create_post(session, org_urn, account_id, args.title, args.body,
                           document_urn, args.cta, args.landing_page)
    print(f"   {post_urn}")
    print("3. Creating creative (PAUSED)...")
    creative = create_creative(session, account_id, args.campaign_id, post_urn,
                               args.name, args.lead_form_id, args.cta)
    print(f"   {creative}")
    print("\nDone. The document ad is PAUSED - review it in Campaign Manager, then enable.")


if __name__ == "__main__":
    main()

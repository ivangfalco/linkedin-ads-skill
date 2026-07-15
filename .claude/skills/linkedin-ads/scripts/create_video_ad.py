#!/usr/bin/env python3
"""
Create a LinkedIn single-video ad.

Uploads a video (chunked), creates a sponsored post that hosts it, and attaches
it as a creative under a campaign. The campaign should be a video-format
campaign (format SINGLE_VIDEO).

Usage:
    python create_video_ad.py --campaign-id 123456 \
        --video ./ad.mp4 --title "See it in action" \
        --body "How teams cut reporting time to minutes." \
        --url "https://example.com/demo" --cta REQUEST_DEMO \
        --name "TOF | Video | Demo"

Video specs: MP4, 3s to 30min, 75KB to 500MB.
UTM params are appended to the destination URL when provided.
The creative is created PAUSED so nothing serves until you review and enable it.
"""

import argparse
import os
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
    if not url or not params:
        return url
    sep = "&" if "?" in url else "?"
    return url + sep + urllib.parse.urlencode(params)


def upload_video(session, org_urn, video_path):
    size = os.path.getsize(video_path)
    init = session.post(
        f"{BASE_URL}/videos?action=initializeUpload",
        json={"initializeUploadRequest": {
            "owner": org_urn, "fileSizeBytes": size,
            "uploadCaptions": False, "uploadThumbnail": False,
        }},
    )
    if init.status_code not in (200, 201):
        raise RuntimeError(f"Video init failed: {init.status_code} {init.text[:300]}")
    value = init.json()["value"]
    video_urn = value["video"]
    upload_token = value.get("uploadToken", "")
    part_ids = []

    token = session.headers["Authorization"]
    with open(video_path, "rb") as f:
        for i, ins in enumerate(value.get("uploadInstructions", [])):
            f.seek(ins["firstByte"])
            chunk = f.read(ins["lastByte"] - ins["firstByte"] + 1)
            up = session.put(
                ins["uploadUrl"],
                headers={"Authorization": token, "Content-Type": "application/octet-stream"},
                data=chunk,
            )
            if up.status_code not in (200, 201):
                raise RuntimeError(f"Video chunk {i + 1} failed: {up.status_code} {up.text[:300]}")
            etag = up.headers.get("etag") or up.headers.get("ETag")
            if etag:
                part_ids.append(etag.strip('"'))

    fin = session.post(
        f"{BASE_URL}/videos?action=finalizeUpload",
        json={"finalizeUploadRequest": {
            "video": video_urn, "uploadToken": upload_token, "uploadedPartIds": part_ids,
        }},
    )
    if fin.status_code not in (200, 201):
        raise RuntimeError(f"Video finalize failed: {fin.status_code} {fin.text[:300]}")

    enc = urllib.parse.quote(video_urn, safe="")
    for _ in range(60):
        time.sleep(3)
        status = session.get(f"{BASE_URL}/videos/{enc}").json().get("status")
        if status == "AVAILABLE":
            return video_urn
        if status == "PROCESSING_FAILED":
            raise RuntimeError("Video processing failed")
    raise RuntimeError("Timed out waiting for video to become AVAILABLE")


def create_post(session, org_urn, account_id, title, body, video_urn, cta, landing_page):
    payload = {
        "author": org_urn,
        "lifecycleState": "PUBLISHED",
        "visibility": "PUBLIC",
        "commentary": body,
        "isReshareDisabledByAuthor": True,
        "distribution": {"feedDistribution": "NONE", "thirdPartyDistributionChannels": []},
        "content": {"media": {"id": video_urn, "title": title}},
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
    parser = argparse.ArgumentParser(description="Create a LinkedIn single-video ad")
    parser.add_argument("--campaign-id", required=True, help="Campaign ID to attach the ad to")
    parser.add_argument("--video", required=True, help="Path to the MP4 file")
    parser.add_argument("--title", required=True, help="Video title (renders as the headline)")
    parser.add_argument("--body", default="", help="Post commentary / ad body text")
    parser.add_argument("--url", help="Destination landing page URL (required if --cta set)")
    parser.add_argument("--cta", help="CTA label (e.g. LEARN_MORE, REQUEST_DEMO, SIGN_UP, DOWNLOAD)")
    parser.add_argument("--name", default="Video Ad", help="Creative name for reference")
    parser.add_argument("--utm-source")
    parser.add_argument("--utm-medium")
    parser.add_argument("--utm-campaign")
    parser.add_argument("--org-id", help="Override the organization (Page) ID from config/.env")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()

    if args.cta and not args.url:
        print("ERROR: --url is required when --cta is set.")
        sys.exit(1)

    org_id = args.org_id or get_config().get("org_id")
    if not org_id:
        print("ERROR: LINKEDIN_ORG_ID is not set in .env (your company Page's organization ID).")
        print("Pass --org-id or add it to .env.")
        sys.exit(1)
    org_urn = f"urn:li:organization:{org_id}"

    session = get_session()
    account_id = args.account_id or get_account_id()
    landing = with_utm(args.url, args.utm_source, args.utm_medium, args.utm_campaign)

    print("1. Uploading video (this can take a minute)...")
    video_urn = upload_video(session, org_urn, args.video)
    print(f"   {video_urn}")
    print("2. Creating post...")
    post_urn = create_post(session, org_urn, account_id, args.title, args.body,
                           video_urn, args.cta, landing)
    print(f"   {post_urn}")
    print("3. Creating creative (PAUSED)...")
    creative = create_creative(session, account_id, args.campaign_id, post_urn, args.name)
    print(f"   {creative}")
    print("\nDone. The video ad is PAUSED - review it in Campaign Manager, then enable.")


if __name__ == "__main__":
    main()

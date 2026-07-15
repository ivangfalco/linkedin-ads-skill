#!/usr/bin/env python3
"""
Demographics breakdown for LinkedIn Ads campaigns.

Usage:
    python get_demographics.py                                           # All pivots, last 30 days
    python get_demographics.py --pivot JOB_FUNCTION                      # Single pivot
    python get_demographics.py --campaign-id 123456 --pivot MEMBER_SENIORITY
    python get_demographics.py --date-range last_7d --pivot MEMBER_INDUSTRY
    python get_demographics.py --account-id 111222333

Pivots: JOB_FUNCTION, MEMBER_SENIORITY, MEMBER_COMPANY_SIZE, MEMBER_INDUSTRY, MEMBER_COUNTRY
"""

import argparse
from datetime import date, timedelta
from client import get_session, get_account_id, BASE_URL
from tabulate import tabulate


DATE_RANGES = {"last_7d": 7, "last_14d": 14, "last_30d": 30, "last_90d": 90}

METRIC_FIELDS = "impressions,clicks,costInLocalCurrency,externalWebsiteConversions,oneClickLeads,pivotValues"

PIVOT_MAP = {
    "JOB_FUNCTION": "MEMBER_JOB_FUNCTION",
    "MEMBER_SENIORITY": "MEMBER_SENIORITY",
    "MEMBER_COMPANY_SIZE": "MEMBER_COMPANY_SIZE",
    "MEMBER_INDUSTRY": "MEMBER_INDUSTRY",
    "MEMBER_COUNTRY": "MEMBER_COUNTRY_V2",
}

ALL_PIVOTS = list(PIVOT_MAP.values())


def fetch_demographics(session, account_id, pivot, start, end, campaign_id=None):
    params = {
        "q": "analytics",
        "pivot": pivot,
        "timeGranularity": "ALL",
        "dateRange.start.year": start.year,
        "dateRange.start.month": start.month,
        "dateRange.start.day": start.day,
        "dateRange.end.year": end.year,
        "dateRange.end.month": end.month,
        "dateRange.end.day": end.day,
        "accounts[0]": f"urn:li:sponsoredAccount:{account_id}",
        "fields": METRIC_FIELDS,
    }
    if campaign_id:
        params["campaigns[0]"] = f"urn:li:sponsoredCampaign:{campaign_id}"

    resp = session.get(f"{BASE_URL}/adAccounts/{account_id}/adAnalytics", params=params)
    if resp.status_code != 200:
        print(f"  WARNING: Failed to fetch {pivot}: {resp.status_code}")
        return []

    segments = []
    for el in resp.json().get("elements", []):
        pv = el.get("pivotValues", [])
        raw = pv[0] if pv else ""
        display = raw.split(":")[-1] if ":" in raw else raw
        impressions = int(el.get("impressions", 0))
        clicks = int(el.get("clicks", 0))
        spend = float(el.get("costInLocalCurrency", 0) or 0)
        conversions = int(el.get("externalWebsiteConversions", 0)) + int(el.get("oneClickLeads", 0))
        ctr = (clicks / impressions * 100) if impressions else 0
        segments.append({"segment": display, "impressions": impressions, "clicks": clicks,
                         "spend": spend, "conversions": conversions, "ctr": ctr})

    segments.sort(key=lambda s: s["spend"], reverse=True)
    return segments


def get_demographics(args):
    session = get_session()
    account_id = args.account_id or get_account_id()
    days = DATE_RANGES.get(args.date_range, 30)
    end = date.today()
    start = end - timedelta(days=days)

    pivots = [PIVOT_MAP.get(p, p) for p in args.pivot] if args.pivot else ALL_PIVOTS

    print(f"\n{'='*60}")
    print(f"  LINKEDIN ADS DEMOGRAPHICS BREAKDOWN")
    print(f"  Account: {account_id}")
    if args.campaign_id:
        print(f"  Campaign: {args.campaign_id}")
    print(f"  Period: {start:%Y-%m-%d} to {end:%Y-%m-%d}")
    print(f"{'='*60}")

    for pivot in pivots:
        friendly = pivot.replace("MEMBER_", "").replace("_V2", "").replace("_", " ").title()
        segments = fetch_demographics(session, account_id, pivot, start, end, args.campaign_id)
        if not segments:
            print(f"\n  {friendly}: No data")
            continue
        rows = [[s["segment"][:40], f"{s['impressions']:,}", f"{s['clicks']:,}",
                 f"{s['ctr']:.2f}%", f"${s['spend']:,.2f}", f"{s['conversions']:,}"]
                for s in segments[:20]]
        print(f"\n  {friendly.upper()}")
        print(tabulate(rows, headers=["Segment", "Impr", "Clicks", "CTR", "Spend", "Conv"],
                       tablefmt="simple"))

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Ads demographics breakdown")
    parser.add_argument("--campaign-id", type=int, help="Filter by campaign ID")
    parser.add_argument("--pivot", action="append", choices=list(PIVOT_MAP.keys()),
                        help="Demographic pivot(s) to show (default: all)")
    parser.add_argument("--date-range", default="last_30d", choices=list(DATE_RANGES.keys()),
                        help="Preset date range (default: last_30d)")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    get_demographics(args)

#!/usr/bin/env python3
"""
Get performance metrics for LinkedIn Ads campaigns.

Usage:
    python get_campaign_performance.py                              # All campaigns, last 30 days
    python get_campaign_performance.py --campaign-id 123456789
    python get_campaign_performance.py --date-range last_7d
    python get_campaign_performance.py --start-date 2026-01-01 --end-date 2026-01-31
    python get_campaign_performance.py --account-id 111222333
"""

import argparse
import sys
from datetime import date, datetime, timedelta
from client import get_session, get_account_id, BASE_URL
from tabulate import tabulate


DATE_RANGES = {"last_7d": 7, "last_14d": 14, "last_30d": 30, "last_90d": 90}

METRIC_FIELDS = (
    "impressions,clicks,costInLocalCurrency,externalWebsiteConversions,"
    "oneClickLeads,pivotValues,dateRange"
)


def parse_dates(args):
    if args.start_date and args.end_date:
        s = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        e = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    else:
        days = DATE_RANGES.get(args.date_range, 30)
        e = date.today()
        s = e - timedelta(days=days)
    return s, e


def fetch_analytics(session, account_id, start, end, pivot, campaign_id=None, by_day=False):
    params = {
        "q": "analytics",
        "pivot": pivot,
        "timeGranularity": "DAILY" if by_day else "ALL",
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
        print(f"ERROR: Failed to fetch analytics: {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    return resp.json().get("elements", [])


def get_performance(args):
    session = get_session()
    account_id = args.account_id or get_account_id()
    start, end = parse_dates(args)

    elements = fetch_analytics(session, account_id, start, end, "CAMPAIGN",
                               args.campaign_id, args.by_day)
    if not elements:
        print("No data found for the specified criteria.")
        return

    rows = []
    tot = {"spend": 0.0, "conv": 0, "clicks": 0, "impr": 0}
    for el in elements:
        impressions = int(el.get("impressions", 0))
        clicks = int(el.get("clicks", 0))
        spend = float(el.get("costInLocalCurrency", 0) or 0)
        conversions = int(el.get("externalWebsiteConversions", 0)) + int(el.get("oneClickLeads", 0))
        ctr = (clicks / impressions * 100) if impressions else 0
        cpc = (spend / clicks) if clicks else 0
        cpl = (spend / conversions) if conversions else 0

        tot["spend"] += spend
        tot["conv"] += conversions
        tot["clicks"] += clicks
        tot["impr"] += impressions

        pv = el.get("pivotValues", [])
        campaign_id = pv[0].split(":")[-1] if pv else "?"

        base = [f"{impressions:,}", f"{clicks:,}", f"{ctr:.2f}%", f"${spend:,.2f}",
                f"{conversions:,}", f"${cpc:.2f}" if cpc else "-", f"${cpl:.2f}" if cpl else "-"]
        if args.by_day:
            ds = el.get("dateRange", {}).get("start", {})
            date_str = f"{ds.get('year', '')}-{ds.get('month', 1):02d}-{ds.get('day', 1):02d}"
            rows.append([date_str, campaign_id] + base)
        else:
            rows.append([campaign_id] + base)

    if args.by_day:
        rows.sort(key=lambda r: r[0], reverse=True)
        headers = ["Date", "Campaign ID", "Impr", "Clicks", "CTR", "Spend", "Conv", "CPC", "CPL"]
    else:
        rows.sort(key=lambda r: float(r[4].replace("$", "").replace(",", "")), reverse=True)
        headers = ["Campaign ID", "Impr", "Clicks", "CTR", "Spend", "Conv", "CPC", "CPL"]

    total_ctr = (tot["clicks"] / tot["impr"] * 100) if tot["impr"] else 0
    total_cpc = (tot["spend"] / tot["clicks"]) if tot["clicks"] else 0
    total_cpl = (tot["spend"] / tot["conv"]) if tot["conv"] else 0

    print(f"\n  Campaign Performance: {start:%Y-%m-%d} to {end:%Y-%m-%d}")
    print(tabulate(rows, headers=headers, tablefmt="simple"))
    print(f"\n  Totals: Spend ${tot['spend']:,.2f} | Clicks {tot['clicks']:,} | "
          f"CTR {total_ctr:.2f}% | Conv {tot['conv']:,} | "
          f"CPC ${total_cpc:.2f} | CPL ${total_cpl:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get LinkedIn Ads campaign performance")
    parser.add_argument("--campaign-id", type=int, help="Specific campaign ID")
    parser.add_argument("--date-range", default="last_30d", choices=list(DATE_RANGES.keys()),
                        help="Preset date range (default: last_30d)")
    parser.add_argument("--start-date", help="Custom start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Custom end date (YYYY-MM-DD)")
    parser.add_argument("--by-day", action="store_true", help="Show daily breakdown")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    get_performance(args)

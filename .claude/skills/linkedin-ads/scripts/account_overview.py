#!/usr/bin/env python3
"""
High-level LinkedIn Ads account performance overview.

Usage:
    python account_overview.py                  # Last 30 days
    python account_overview.py --date-range last_7d
    python account_overview.py --compare        # Compare to previous period
    python account_overview.py --account-id 111222333
"""

import argparse
from datetime import date, timedelta
from client import get_session, get_account_id, BASE_URL
from tabulate import tabulate


DATE_RANGES = {"last_7d": 7, "last_14d": 14, "last_30d": 30, "last_90d": 90}

METRIC_FIELDS = "impressions,clicks,costInLocalCurrency,externalWebsiteConversions,oneClickLeads,pivotValues"


def window(days, offset=0):
    end = date.today() - timedelta(days=offset)
    start = end - timedelta(days=days)
    return start, end


def fetch(session, account_id, start, end, pivot):
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
    resp = session.get(f"{BASE_URL}/adAccounts/{account_id}/adAnalytics", params=params)
    if resp.status_code != 200:
        print(f"ERROR: Failed to fetch analytics ({pivot}): {resp.status_code}")
        print(resp.text)
        return []
    return resp.json().get("elements", [])


def totals(elements):
    t = {"impressions": 0, "clicks": 0, "spend": 0.0, "conversions": 0, "leads": 0}
    for el in elements:
        t["impressions"] += int(el.get("impressions", 0))
        t["clicks"] += int(el.get("clicks", 0))
        t["spend"] += float(el.get("costInLocalCurrency", 0) or 0)
        t["conversions"] += int(el.get("externalWebsiteConversions", 0))
        t["leads"] += int(el.get("oneClickLeads", 0))
    t["ctr"] = (t["clicks"] / t["impressions"] * 100) if t["impressions"] else 0
    t["cpc"] = (t["spend"] / t["clicks"]) if t["clicks"] else 0
    total_conv = t["conversions"] + t["leads"]
    t["total_conversions"] = total_conv
    t["cpl"] = (t["spend"] / total_conv) if total_conv else 0
    return t


def account_overview(date_range, compare, account_id):
    session = get_session()
    account_id = account_id or get_account_id()
    days = DATE_RANGES.get(date_range, 30)
    start, end = window(days)

    print(f"\n{'='*60}")
    print(f"  LINKEDIN ADS ACCOUNT OVERVIEW")
    print(f"  Account: {account_id}")
    print(f"  Period: {start:%Y-%m-%d} to {end:%Y-%m-%d} ({date_range})")
    print(f"{'='*60}")

    current = totals(fetch(session, account_id, start, end, "ACCOUNT"))

    metrics_table = [
        ["Impressions", f"{current['impressions']:,}"],
        ["Clicks", f"{current['clicks']:,}"],
        ["CTR", f"{current['ctr']:.2f}%"],
        ["Avg CPC", f"${current['cpc']:.2f}"],
        ["Total Spend", f"${current['spend']:,.2f}"],
        ["Conversions", f"{current['total_conversions']:,}"],
        ["Lead Form Fills", f"{current['leads']:,}"],
        ["Cost per Lead", f"${current['cpl']:.2f}"],
    ]

    if compare:
        prev_start, prev_end = window(days, offset=days)
        previous = totals(fetch(session, account_id, prev_start, prev_end, "ACCOUNT"))

        def delta(curr, prev):
            if prev == 0:
                return "n/a"
            change = ((curr - prev) / prev) * 100
            return f"{'+' if change > 0 else ''}{change:.1f}%"

        keys = ["impressions", "clicks", "ctr", "cpc", "spend", "total_conversions", "leads", "cpl"]
        for i, k in enumerate(keys):
            metrics_table[i].append(delta(current[k], previous[k]))
        headers = ["Metric", "Current", f"vs Previous {days}d"]
    else:
        headers = ["Metric", "Value"]

    print(f"\n  ACCOUNT METRICS")
    print(tabulate(metrics_table, headers=headers, tablefmt="simple"))

    # Top campaigns by spend
    campaigns = []
    for el in fetch(session, account_id, start, end, "CAMPAIGN"):
        spend = float(el.get("costInLocalCurrency", 0) or 0)
        impressions = int(el.get("impressions", 0))
        clicks = int(el.get("clicks", 0))
        conversions = int(el.get("externalWebsiteConversions", 0)) + int(el.get("oneClickLeads", 0))
        pv = el.get("pivotValues", [])
        campaigns.append({
            "id": pv[0].split(":")[-1] if pv else "?",
            "impressions": impressions, "clicks": clicks, "spend": spend, "conversions": conversions,
            "ctr": (clicks / impressions * 100) if impressions else 0,
            "cpl": (spend / conversions) if conversions else 0,
        })
    campaigns.sort(key=lambda c: c["spend"], reverse=True)

    if campaigns:
        camp_rows = [[c["id"], f"{c['impressions']:,}", f"{c['clicks']:,}", f"{c['ctr']:.2f}%",
                      f"${c['spend']:,.2f}", f"{c['conversions']:,}",
                      f"${c['cpl']:.2f}" if c["cpl"] else "-"] for c in campaigns[:15]]
        print(f"\n  TOP CAMPAIGNS BY SPEND")
        print(tabulate(camp_rows,
                       headers=["Campaign ID", "Impr", "Clicks", "CTR", "Spend", "Conv", "CPL"],
                       tablefmt="simple"))

    print(f"\n{'='*60}")
    print(f"  Run 'python get_campaign_performance.py' for detailed breakdowns")
    print(f"  Run 'python get_demographics.py' for audience insights")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Ads account overview")
    parser.add_argument("--date-range", default="last_30d", choices=list(DATE_RANGES.keys()),
                        help="Preset date range (default: last_30d)")
    parser.add_argument("--compare", action="store_true", help="Compare to previous period")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    account_overview(args.date_range, args.compare, args.account_id)

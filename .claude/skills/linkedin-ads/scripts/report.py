#!/usr/bin/env python3
"""
LinkedIn Ads HTML report - 7, 30, and 90-day performance.

Pulls account-level and per-campaign analytics and writes a clean,
self-contained HTML dashboard you can open in any browser or send to a client.

Usage:
    python report.py
    python report.py --output my_report.html --brand "Your Agency"
"""

import argparse
import datetime
import sys

from client import get_session, get_account_id, BASE_URL

METRIC_FIELDS = (
    "impressions,clicks,costInLocalCurrency,externalWebsiteConversions,"
    "oneClickLeads,landingPageClicks,pivotValues"
)


def analytics(session, account_id, start, end, pivot):
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
    r = session.get(f"{BASE_URL}/adAccounts/{account_id}/adAnalytics", params=params)
    r.raise_for_status()
    return r.json().get("elements", [])


def summarize(elements):
    agg = {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0, "leads": 0}
    for e in elements:
        agg["impressions"] += int(e.get("impressions", 0))
        agg["clicks"] += int(e.get("clicks", 0))
        agg["cost"] += float(e.get("costInLocalCurrency", 0) or 0)
        agg["conversions"] += int(e.get("externalWebsiteConversions", 0))
        agg["leads"] += int(e.get("oneClickLeads", 0))
    return derive(agg)


def derive(a):
    imp, clk, cost = a["impressions"], a["clicks"], a["cost"]
    results = a["conversions"] + a["leads"]
    a.update({
        "results": results,
        "ctr": (clk / imp * 100) if imp else 0,
        "cpc": (cost / clk) if clk else 0,
        "cpm": (cost / imp * 1000) if imp else 0,
        "cpl": (cost / results) if results else 0,
    })
    return a


def campaign_names(session, account_id):
    r = session.get(
        f"{BASE_URL}/adAccounts/{account_id}/adCampaigns",
        params={"q": "search"},
    )
    if r.status_code != 200:
        return {}
    return {str(c.get("id")): c.get("name", "") for c in r.json().get("elements", [])}


def campaign_rows(session, account_id, start, end):
    names = campaign_names(session, account_id)
    rows = []
    for e in analytics(session, account_id, start, end, "CAMPAIGN"):
        pv = e.get("pivotValues", [])
        cid = pv[0].split(":")[-1] if pv else ""
        m = derive({
            "impressions": int(e.get("impressions", 0)),
            "clicks": int(e.get("clicks", 0)),
            "cost": float(e.get("costInLocalCurrency", 0) or 0),
            "conversions": int(e.get("externalWebsiteConversions", 0)),
            "leads": int(e.get("oneClickLeads", 0)),
        })
        m["name"] = names.get(cid, f"Campaign {cid}")
        rows.append(m)
    rows.sort(key=lambda x: x["cost"], reverse=True)
    return rows


def card(label, a):
    return f"""
    <div class="card">
      <div class="card-label">{label}</div>
      <div class="metrics">
        <div><span class="n">${a['cost']:,.0f}</span><span class="l">Spend</span></div>
        <div><span class="n">{a['impressions']:,}</span><span class="l">Impressions</span></div>
        <div><span class="n">{a['clicks']:,}</span><span class="l">Clicks</span></div>
        <div><span class="n">{a['ctr']:.2f}%</span><span class="l">CTR</span></div>
        <div><span class="n">${a['cpc']:,.2f}</span><span class="l">CPC</span></div>
        <div><span class="n">{a['results']:,}</span><span class="l">Results</span></div>
        <div><span class="n">${a['cpl']:,.0f}</span><span class="l">Cost / Result</span></div>
      </div>
    </div>"""


def render(brand, account_id, today, periods, rows):
    cards = "".join(card(label, a) for label, a in periods)
    trs = "".join(
        f"<tr><td>{r['name']}</td><td>${r['cost']:,.0f}</td><td>{r['impressions']:,}</td>"
        f"<td>{r['clicks']:,}</td><td>{r['ctr']:.2f}%</td><td>${r['cpc']:,.2f}</td>"
        f"<td>{r['results']:,}</td><td>${r['cpl']:,.0f}</td></tr>"
        for r in rows
    ) or "<tr><td colspan='8'>No campaign data in this window.</td></tr>"
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{brand} - LinkedIn Ads Report</title>
<style>
  body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1115;color:#e8eaed}}
  .top{{padding:28px 40px;border-bottom:1px solid #232733;display:flex;justify-content:space-between;align-items:baseline}}
  .top h1{{margin:0;font-size:20px}} .top .sub{{color:#8a909c;font-size:13px}}
  .wrap{{padding:32px 40px;max-width:1100px;margin:0 auto}}
  .cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:32px}}
  .card{{background:#171a21;border:1px solid #232733;border-radius:12px;padding:18px}}
  .card-label{{font-size:13px;color:#8a909c;margin-bottom:14px;text-transform:uppercase;letter-spacing:.04em}}
  .metrics{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}
  .metrics .n{{display:block;font-size:18px;font-weight:600}} .metrics .l{{font-size:11px;color:#8a909c}}
  table{{width:100%;border-collapse:collapse;background:#171a21;border:1px solid #232733;border-radius:12px;overflow:hidden}}
  th,td{{text-align:left;padding:11px 14px;font-size:13px;border-bottom:1px solid #232733}}
  th{{color:#8a909c;font-weight:500;text-transform:uppercase;font-size:11px;letter-spacing:.04em}}
  td:first-child{{max-width:340px}} h2{{font-size:15px;margin:0 0 14px}}
</style></head><body>
  <div class="top"><h1>{brand} - LinkedIn Ads Report</h1>
  <span class="sub">Account {account_id} - generated {today:%b %d, %Y}</span></div>
  <div class="wrap">
    <div class="cards">{cards}</div>
    <h2>Campaigns - last 30 days</h2>
    <table><thead><tr><th>Campaign</th><th>Spend</th><th>Impr.</th><th>Clicks</th>
    <th>CTR</th><th>CPC</th><th>Results</th><th>Cost/Result</th></tr></thead>
    <tbody>{trs}</tbody></table>
  </div>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate a LinkedIn Ads HTML report (7/30/90-day)")
    parser.add_argument("--output", default="linkedin_report.html", help="Output HTML file path")
    parser.add_argument("--brand", default="LinkedIn Ads", help="Brand/agency name for the header")
    args = parser.parse_args()

    session = get_session()
    account_id = get_account_id()
    today = datetime.date.today()

    windows = [("Last 7 days", 7), ("Last 30 days", 30), ("Last 90 days", 90)]
    periods = []
    for label, days in windows:
        start = today - datetime.timedelta(days=days)
        periods.append((label, summarize(analytics(session, account_id, start, today, "ACCOUNT"))))

    rows = campaign_rows(session, account_id, today - datetime.timedelta(days=30), today)

    html = render(args.brand, account_id, today, periods, rows)
    with open(args.output, "w") as f:
        f.write(html)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()

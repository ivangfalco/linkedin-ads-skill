#!/usr/bin/env python3
"""
Bulk-edit LinkedIn campaigns: pause/enable, rename, budget, bid, exclusions.

Select campaigns by id list or by current status, then apply one or more
changes to all of them in a single run.

Examples:
    # Pause several campaigns
    python bulk_edit.py --campaign-ids 111,222,333 --pause

    # Enable every paused campaign
    python bulk_edit.py --status PAUSED --enable

    # Prefix names and raise daily budget across a set
    python bulk_edit.py --campaign-ids 111,222 --rename-prefix "[Q2] " --daily-budget 7500

    # Move a set to manual CPC at $5.00
    python bulk_edit.py --campaign-ids 111,222 --bid-strategy MANUAL_CPC --bid-amount 500

    # Add an audience exclusion to a set
    python bulk_edit.py --campaign-ids 111,222 \
        --exclude-facet "urn:li:adTargetingFacet:employers" \
        --exclude-urns "urn:li:organization:123,urn:li:organization:456"

Budget and bid amounts are in CENTS (5000 = $50.00).
"""

import argparse
import sys

from client import get_session, get_account_id, BASE_URL

PATCH_HEADER = {"X-RestLi-Method": "PARTIAL_UPDATE"}


def select_campaigns(session, account_id, ids, status):
    if ids:
        return [c.strip() for c in ids.split(",") if c.strip()]
    params = {"q": "search"}
    if status:
        params["search"] = f"(status:(values:List({status})))"
    r = session.get(f"{BASE_URL}/adAccounts/{account_id}/adCampaigns", params=params)
    r.raise_for_status()
    return [str(c["id"]) for c in r.json().get("elements", [])]


def get_campaign(session, account_id, cid):
    r = session.get(f"{BASE_URL}/adAccounts/{account_id}/adCampaigns/{cid}")
    r.raise_for_status()
    return r.json()


def patch_campaign(session, account_id, cid, changes):
    r = session.post(
        f"{BASE_URL}/adAccounts/{account_id}/adCampaigns/{cid}",
        headers={**session.headers, **PATCH_HEADER},
        json={"patch": {"$set": changes}},
    )
    return r.status_code in (200, 204), r


def build_changes(args, current):
    changes = {}
    if args.pause:
        changes["status"] = "PAUSED"
    if args.enable:
        changes["status"] = "ACTIVE"
    if args.set_name:
        changes["name"] = args.set_name
    if args.rename_prefix:
        changes["name"] = f"{args.rename_prefix}{current.get('name', '')}"
    if args.daily_budget is not None:
        changes["dailyBudget"] = {"amount": str(args.daily_budget), "currencyCode": "USD"}
    if args.bid_amount is not None:
        changes["unitCost"] = {"amount": str(args.bid_amount), "currencyCode": "USD"}
    if args.bid_strategy:
        if args.bid_strategy == "AUTO":
            changes["bidStrategy"] = "MAXIMUM_DELIVERY"
        else:
            changes["bidStrategy"] = "MANUAL_BIDDING"
            changes["costType"] = "CPC" if args.bid_strategy == "MANUAL_CPC" else "CPM"
    if args.exclude_facet and args.exclude_urns:
        criteria = current.get("targetingCriteria", {}) or {}
        exclude = criteria.get("exclude", {}) or {}
        facets = exclude.get("or", {}) or {}
        existing = list(facets.get(args.exclude_facet, []))
        for urn in args.exclude_urns.split(","):
            urn = urn.strip()
            if urn and urn not in existing:
                existing.append(urn)
        facets[args.exclude_facet] = existing
        exclude["or"] = facets
        criteria["exclude"] = exclude
        changes["targetingCriteria"] = criteria
    return changes


def main():
    p = argparse.ArgumentParser(description="Bulk-edit LinkedIn campaigns")
    sel = p.add_argument_group("select")
    sel.add_argument("--campaign-ids", help="Comma-separated campaign IDs")
    sel.add_argument("--status", choices=["ACTIVE", "PAUSED", "DRAFT"], help="Select all campaigns with this status")
    act = p.add_argument_group("changes")
    act.add_argument("--pause", action="store_true")
    act.add_argument("--enable", action="store_true")
    act.add_argument("--set-name", help="Set an exact name on all selected campaigns")
    act.add_argument("--rename-prefix", help="Prepend this string to each campaign's current name")
    act.add_argument("--daily-budget", type=int, help="Daily budget in cents")
    act.add_argument("--bid-amount", type=int, help="Bid amount in cents")
    act.add_argument("--bid-strategy", choices=["AUTO", "MANUAL_CPC", "MANUAL_CPM"])
    act.add_argument("--exclude-facet", help="Targeting facet URN to exclude into")
    act.add_argument("--exclude-urns", help="Comma-separated entity URNs to exclude")
    args = p.parse_args()

    if args.pause and args.enable:
        print("ERROR: pick either --pause or --enable, not both.")
        sys.exit(1)
    if not (args.campaign_ids or args.status):
        print("ERROR: select campaigns with --campaign-ids or --status.")
        sys.exit(1)

    session = get_session()
    account_id = get_account_id()
    ids = select_campaigns(session, account_id, args.campaign_ids, args.status)
    if not ids:
        print("No campaigns matched.")
        return

    needs_current = bool(args.rename_prefix or (args.exclude_facet and args.exclude_urns))
    print(f"Editing {len(ids)} campaign(s)...")
    ok = 0
    for cid in ids:
        current = get_campaign(session, account_id, cid) if needs_current else {}
        changes = build_changes(args, current)
        if not changes:
            print("No changes specified. Use --pause/--enable/--set-name/--daily-budget/--bid-amount/--bid-strategy/--exclude-*.")
            return
        success, resp = patch_campaign(session, account_id, cid, changes)
        if success:
            ok += 1
            print(f"  {cid}: updated ({', '.join(changes.keys())})")
        else:
            print(f"  {cid}: FAILED {resp.status_code} {resp.text[:200]}")
    print(f"\nDone. {ok}/{len(ids)} updated.")


if __name__ == "__main__":
    main()

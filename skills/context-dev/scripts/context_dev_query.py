#!/usr/bin/env python3
"""
Hermes helper script for Context.dev API queries.
Uses the official context.dev Python SDK (pip install context.dev).

Usage:
  python context_dev_query.py <action> <args...>

Actions:
  brand <domain> [language]       - Retrieve full brand data by domain
  brand-simple <domain>           - Retrieve simplified brand data
  brand-name <name> [language]    - Retrieve brand data by company name
  brand-email <email> [language]  - Retrieve brand data by email
  brand-ticker <ticker> [language] - Retrieve brand data by stock ticker
  brand-isin <isin> [language]    - Retrieve brand data by ISIN
  brand-txn <transaction_info> [city] [country_code] - Identify brand from transaction
  naics <input> [min] [max]       - NAICS industry classification
  scrape-html <url>               - Scrape raw HTML
  scrape-md <url> [include_images] [include_links] - Scrape to Markdown
  scrape-images <url>             - Scrape images from page
  sitemap <domain>                - Crawl sitemap
  screenshot <domain> [full] [page] - Take screenshot
  ai-query <domain> <datapoints_json> - AI-powered data extraction
  ai-products <domain> [max_products] - Extract products from brand website
  ai-product <url>                - Extract single product from URL
"""
import sys
import os
import json

from context.dev import ContextDev


def get_client():
    key = os.environ.get("CONTEXT_DEV_API_KEY", "").strip()
    if not key:
        print(json.dumps({"error": "CONTEXT_DEV_API_KEY not set"}))
        sys.exit(1)
    return ContextDev(api_key=key)


def dump(obj):
    """Recursively convert SDK/pydantic objects to JSON-serializable dicts."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [dump(item) for item in obj]
    if isinstance(obj, dict):
        return {k: dump(v) for k, v in obj.items()}
    if hasattr(obj, "model_dump"):
        try:
            return dump(obj.model_dump())
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return dump(obj.__dict__)
    return str(obj)


def output(data):
    print(json.dumps(dump(data), indent=2, ensure_ascii=False))


# ─── Brand Retrieval ─────────────────────────────────────────────────────────

def cmd_brand(args):
    client = get_client()
    kwargs = {"domain": args[0]}
    if len(args) > 1:
        kwargs["force_language"] = args[1]
    output(client.brand.retrieve(**kwargs))


def cmd_brand_simple(args):
    client = get_client()
    output(client.brand.retrieve_simplified(domain=args[0]))


def cmd_brand_name(args):
    client = get_client()
    kwargs = {"name": args[0]}
    if len(args) > 1:
        kwargs["force_language"] = args[1]
    output(client.brand.retrieve_by_name(**kwargs))


def cmd_brand_email(args):
    client = get_client()
    kwargs = {"email": args[0]}
    if len(args) > 1:
        kwargs["force_language"] = args[1]
    output(client.brand.retrieve_by_email(**kwargs))


def cmd_brand_ticker(args):
    client = get_client()
    kwargs = {"ticker": args[0]}
    if len(args) > 1:
        kwargs["force_language"] = args[1]
    output(client.brand.retrieve_by_ticker(**kwargs))


def cmd_brand_isin(args):
    client = get_client()
    kwargs = {"isin": args[0]}
    if len(args) > 1:
        kwargs["force_language"] = args[1]
    output(client.brand.retrieve_by_isin(**kwargs))


def cmd_brand_txn(args):
    client = get_client()
    kwargs = {"transaction_info": args[0]}
    if len(args) > 1:
        kwargs["city"] = args[1]
    if len(args) > 2:
        kwargs["country_gl"] = args[2]
    output(client.brand.identify_from_transaction(**kwargs))


# ─── Industry Classification ─────────────────────────────────────────────────

def cmd_naics(args):
    client = get_client()
    kwargs = {"input": args[0]}
    if len(args) > 1:
        kwargs["min_results"] = int(args[1])
    if len(args) > 2:
        kwargs["max_results"] = int(args[2])
    output(client.industry.retrieve_naics(**kwargs))


# ─── Web Scraping ────────────────────────────────────────────────────────────

def cmd_scrape_html(args):
    client = get_client()
    output(client.web.web_scrape_html(url=args[0]))


def cmd_scrape_md(args):
    client = get_client()
    kwargs = {"url": args[0]}
    if len(args) > 1:
        kwargs["include_images"] = args[1].lower() == "true"
    if len(args) > 2:
        kwargs["include_links"] = args[2].lower() == "true"
    output(client.web.web_scrape_md(**kwargs))


def cmd_scrape_images(args):
    client = get_client()
    output(client.web.web_scrape_images(url=args[0]))


def cmd_sitemap(args):
    client = get_client()
    output(client.web.web_scrape_sitemap(domain=args[0]))


# ─── Screenshot ──────────────────────────────────────────────────────────────

def cmd_screenshot(args):
    client = get_client()
    kwargs = {"domain": args[0]}
    if len(args) > 1 and args[1] == "true":
        kwargs["full_screenshot"] = "true"
    if len(args) > 2:
        kwargs["page"] = args[2]
    output(client.web.screenshot(**kwargs))


# ─── AI Data Extraction ──────────────────────────────────────────────────────

def cmd_ai_query(args):
    client = get_client()
    datapoints = json.loads(args[1])
    output(client.ai.ai_query(
        domain=args[0],
        data_to_extract=datapoints,
        timeout_ms=120000,
    ))


def cmd_ai_products(args):
    client = get_client()
    kwargs = {"domain": args[0], "timeout_ms": 120000}
    if len(args) > 1:
        kwargs["max_products"] = int(args[1])
    output(client.ai.extract_products(**kwargs))


def cmd_ai_product(args):
    client = get_client()
    output(client.ai.extract_product(url=args[0], timeout_ms=120000))


# ─── Dispatch ────────────────────────────────────────────────────────────────

ACTIONS = {
    "brand": cmd_brand,
    "brand-simple": cmd_brand_simple,
    "brand-name": cmd_brand_name,
    "brand-email": cmd_brand_email,
    "brand-ticker": cmd_brand_ticker,
    "brand-isin": cmd_brand_isin,
    "brand-txn": cmd_brand_txn,
    "naics": cmd_naics,
    "scrape-html": cmd_scrape_html,
    "scrape-md": cmd_scrape_md,
    "scrape-images": cmd_scrape_images,
    "sitemap": cmd_sitemap,
    "screenshot": cmd_screenshot,
    "ai-query": cmd_ai_query,
    "ai-products": cmd_ai_products,
    "ai-product": cmd_ai_product,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ACTIONS:
        print(f"Usage: {sys.argv[0]} <action> <args...>")
        print(f"Actions: {', '.join(ACTIONS.keys())}")
        sys.exit(1)
    ACTIONS[sys.argv[1]](sys.argv[2:])

---
name: context-dev
description: Query Context.dev API for brand data, web scraping, AI extraction, screenshots, and industry classification from any domain.
version: 1.1.0
triggers:
  - brand data
  - company info
  - logo
  - brand colors
  - industry classification
  - NAICS
  - web scraping
  - context.dev
  - brand enrichment
requires:
  - CONTEXT_DEV_API_KEY
  - pip: context.dev
---

# Context.dev Skill

Use the Context.dev API to extract structured brand data, scrape web pages, classify industries, take screenshots, and AI-extract data from any domain.

## Prerequisites

- **API Key**: Set `CONTEXT_DEV_API_KEY` environment variable.
  - Format: `brand_` prefix + 32-char hex (e.g., `brand_c9de62f606c04c02a0149397b85542fe`)
  - Get yours at: https://context.dev/dashboard → API Keys section
- **Quota**: **500 API calls/month** on free tier. Each call costs 1-10 credits.
- **SDK dependency**: `pip install context.dev` (already installed system-wide)

## Quick Reference

Script path: `~/.hermes/skills/research/context-dev/scripts/context_dev_query.py`

### Brand Data Retrieval (10 credits each)

| Action | Command |
|--------|---------|
| By domain | `python3 <script> brand <domain> [language]` |
| Simplified | `python3 <script> brand-simple <domain>` |
| By company name | `python3 <script> brand-name <name> [language]` |
| By email | `python3 <script> brand-email <email> [language]` |
| By stock ticker | `python3 <script> brand-ticker <ticker> [language]` |
| By ISIN | `python3 <script> brand-isin <isin> [language]` |
| From transaction | `python3 <script> brand-txn <transaction_info> [city] [country_code]` |

### Web Scraping (1 credit each)

| Action | Command |
|--------|---------|
| Scrape HTML | `python3 <script> scrape-html <url>` |
| Scrape Markdown | `python3 <script> scrape-md <url> [include_images] [include_links]` |
| Scrape images | `python3 <script> scrape-images <url>` |
| Crawl sitemap | `python3 <script> sitemap <domain>` |

### Screenshot (10 credits)

| Action | Command |
|--------|---------|
| Screenshot | `python3 <script> screenshot <domain> [full=true] [page=login\|signup\|blog\|careers\|pricing\|terms\|privacy\|contact]` |

### AI Data Extraction (10 credits each)

| Action | Command |
|--------|---------|
| AI query | `python3 <script> ai-query <domain> <datapoints_json>` |
| Extract products | `python3 <script> ai-products <domain> [max_products]` |
| Single product | `python3 <script> ai-product <url>` |

### Industry Classification (10 credits)

| Action | Command |
|--------|---------|
| NAICS codes | `python3 <script> naics <input> [min] [max]` |

## Brand Data Response Structure

A successful `brand` call returns a rich JSON object:

```json
{
  "brand": {
    "domain": "example.com",
    "title": "Example Corp",
    "description": "...",
    "slogan": "...",
    "colors": [{"hex": "#FF5733", "name": "Vibrant Orange"}],
    "logos": [{
      "url": "https://media.brand.dev/...",
      "mode": "light|dark|has_opaque_background",
      "type": "icon|logo",
      "resolution": {"width": 512, "height": 512, "aspect_ratio": 1.0},
      "colors": [{"hex": "#000", "name": "Black"}]
    }],
    "backdrops": [{"url": "https://media.brand.dev/...", "resolution": {...}}],
    "socials": [{"type": "x|linkedin|facebook|youtube|github|instagram", "url": "https://..."}],
    "address": {"street": "", "city": "", "country": "", "country_code": "", "state_province": "", "postal_code": ""},
    "stock": {"ticker": "EXMP", "exchange": "NASDAQ"},
    "is_nsfw": false,
    "email": "info@example.com",
    "phone": "+1-555-...",
    "industries": {"eic": [{"industry": "...", "subindustry": "..."}]},
    "links": {"careers": "", "privacy": "", "terms": "", "contact": "", "blog": "", "pricing": ""},
    "primary_language": "english"
  }
}
```

## Step-by-Step Usage

### 1. Retrieve Brand Data for a Domain

```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py brand stripe.com
```

Lighter response (fewer fields):
```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py brand-simple stripe.com
```

### 2. Scrape a Web Page to Markdown

```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py scrape-md https://example.com
```

With images and links:
```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py scrape-md https://example.com true true
```

### 3. Take a Website Screenshot

```bash
# Viewport screenshot (default)
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py screenshot stripe.com

# Full-page screenshot
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py screenshot stripe.com true

# Screenshot a specific page type
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py screenshot stripe.com false pricing
```

### 4. AI-Powered Custom Data Extraction

```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py ai-query stripe.com \
  '[{"datapoint_name":"founding_year","datapoint_type":"text","datapoint_description":"Year the company was founded","datapoint_example":"2010"},{"datapoint_name":"employee_count","datapoint_type":"text","datapoint_description":"Approximate number of employees","datapoint_example":"5000"}]'
```

### 5. Extract Products from a Brand Website

```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py ai-products stripe.com
```

### 6. Industry Classification (NAICS)

```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py naics stripe.com 1 3
```

### 7. Identify Brand from Transaction Data

```bash
python3 ~/.hermes/skills/research/context-dev/scripts/context_dev_query.py brand-txn "AMZN MKTP US*1234567" "Seattle" "us"
```

## Logo Types

- **Type**: `icon` (square/favicon-style) vs `logo` (full wordmark)
- **Mode**: `light` (for light backgrounds) vs `dark` (for dark backgrounds) vs `has_opaque_background`
- Formats include PNG, JPG, and SVG (transparent)

## Languages

The `force_language` parameter supports: `chinese`, `english`, `japanese`, `korean`, `french`, `german`, `spanish`, `portuguese`, `arabic`, `hindi`, `russian`, and 40+ more.

## Common Use Cases

1. **Auto-brand dashboards**: Fetch logos/colors to style your app per-tenant
2. **Lead enrichment**: Enrich CRM records with company info from email/domain
3. **Transaction categorization**: Identify merchants from bank transaction descriptions
4. **Competitive analysis**: Extract product listings and pricing from competitor sites
5. **Web scraping**: Get clean Markdown from any URL (cheaper than Firecrawl at 1 credit)

## Pitfalls

- **Quota limit**: Only 500 calls/month on free tier — use sparingly, prefer `brand-simple` (same cost but lighter) and `scrape-html/md` (1 credit each)
- **API key format**: Keys start with `brand_` prefix, not `sk-`
- **Credits per call**: Brand/AI/screenshot/NAICS = 10 credits; basic scraping = 1 credit
- **Missing data**: Not all fields are available for every brand; handle null gracefully
- **AI query timeout**: AI extraction can take up to 2 minutes
- **Screenshot domain-only**: SDK screenshot only accepts `domain`, not direct URL
- **Transaction identification**: Use `transaction_info` (not `description`), `country_gl` uses 2-letter country codes (e.g., `us`, `cn`, `jp`)
- **Rate limits**: Handle 429 responses with exponential backoff
- **Python urllib blocked**: Cloudflare bans Python's default User-Agent on api.context.dev — always use the official SDK (`context.dev` pip package) or set a proper User-Agent header if using raw HTTP
- **SDK method names differ from docs**: The API docs show endpoint names like `/brand/retrieve` but SDK methods are different: `web_scrape_md()` not `scrape_markdown()`, `identify_from_transaction()` not `identify()`, `transaction_info` param not `description`, `web_scrape_html()` not `scrape_html()`, `web_scrape_sitemap()` not `crawl_sitemap()`, `extract_products()` not `ai_products()`. Always `inspect.signature()` the SDK methods before using them.
- **Docs-only endpoints**: The docs show `styleguide` and `fonts` endpoints, but the Python SDK (v0.2.0) does not expose them. Use curl directly if needed: `GET /v1/brand/styleguide?domain=...` and `GET /v1/brand/fonts?domain=...`
- **Base URL**: The API base URL is `https://api.context.dev/v1` (with `/v1` prefix), not `https://api.context.dev`. The SDK handles this automatically.

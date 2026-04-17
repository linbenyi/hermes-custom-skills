---
name: openrouter-balance
description: Query OpenRouter API key usage and display balance summary. Use when user asks about OpenRouter balance, usage, or spending.
trigger: openrouter, balance, usage, 余额, 消费, 查询key
---

# OpenRouter Key Usage & Balance Checker

Quickly query all OpenRouter API keys and display usage + estimated remaining balance.

## Key Registry

Both keys are **Management Keys** on **separate OpenRouter accounts**.

| Label | Key Prefix | Account | Top-up |
|-------|-----------|---------|--------|
| OPENROUTER_API_KEY | sk-or-v1-af5...3745 | Account A | $20 |
| 10Dollar | sk-or-v1-8dc...3dd0 | Account B | $10 |

If the user mentions new keys or top-ups, update this table and patch the skill.

## Steps

1. Read keys from `~/.hermes/auth.json` → `credential_pool.openrouter`
2. For each key, call: `curl -s -H "Authorization: Bearer <key>" https://openrouter.ai/api/v1/auth/key`
3. Calculate estimated remaining balance: `top_up_balance - usage`
4. Display formatted summary

### One-liner query script

```bash
python3 -c "
import json, subprocess
TOP_UPS = {
    'sk-or-v1-af5...3745': 20.0,
    'sk-or-v1-8dc...3dd0': 10.0,
}
with open('/home/lin/.hermes/auth.json') as f:
    d = json.load(f)
for cred in d.get('credential_pool', {}).get('openrouter', []):
    key = cred['access_token']
    label = cred['label']
    result = subprocess.run(
        ['curl', '-s', '-H', f'Authorization: Bearer {key}', 'https://openrouter.ai/api/v1/auth/key'],
        capture_output=True, text=True, timeout=15
    )
    try:
        r = json.loads(result.stdout)['data']
        usage = r.get('usage', 0)
        top_up = TOP_UPS.get(f'{key[:12]}...{key[-4:]}', '?')
        remaining = f'{top_up - usage:.4f}' if isinstance(top_up, float) else '?'
        print(f'Key: {label} ({key[:12]}...{key[-4:]})')
        print(f'  Top-up: \${top_up}  |  Used: \${usage:.4f}  |  Est. Remaining: \${remaining}')
        print(f'  Today: \${r.get(\"usage_daily\",0):.4f}  |  Week: \${r.get(\"usage_weekly\",0):.4f}  |  Month: \${r.get(\"usage_monthly\",0):.4f}')
        print(f'  Free tier: {r.get(\"is_free_tier\")}  |  Limit: {r.get(\"limit\")}')
        print()
    except Exception as e:
        print(f'Key: {label} — Error: {e}')
        print(result.stdout[:200])
        print()
"
```

## Output Format (Chinese)

```
=== OpenRouter 余额查询 ===

Key 1: <label> (<prefix>...<suffix>)
  充值额度: $XX  |  已用: $X.XXXX  |  预估剩余: $XX.XXXX
  今日: $X.XXXX  |  本周: $X.XXXX  |  本月: $X.XXXX
  免费层级: No   |  消费限额: 无

Key 2: ...
```

## Method 2: Credits API (Management Key Required)

OpenRouter provides a dedicated credits endpoint that returns **actual total credits purchased and total usage**, eliminating the need for manual top-up tracking.

**Endpoint:** `GET https://openrouter.ai/api/v1/credits`
**Auth:** Requires a **Management key**. Both our keys are Management Keys on separate accounts — each returns its own account's credits.
**Response:**
```json
{
  "data": {
    "total_credits": 100.50,
    "total_usage": 25.75
  }
}
```

### One-liner credits query (Management key)

```bash
python3 -c "
import json, subprocess
with open('/home/lin/.hermes/auth.json') as f:
    d = json.load(f)
for cred in d.get('credential_pool', {}).get('openrouter', []):
    key = cred['access_token']
    label = cred['label']
    # Query credits (Management Key endpoint — returns actual balance)
    result = subprocess.run(
        ['curl', '-s', '-H', f'Authorization: Bearer {key}', 'https://openrouter.ai/api/v1/credits'],
        capture_output=True, text=True, timeout=15
    )
    try:
        r = json.loads(result.stdout)['data']
        remaining = r['total_credits'] - r['total_usage']
        print(f'Key: {label} ({key[:12]}...{key[-4:]})')
        print(f'  总充值: \${r[\"total_credits\"]:.2f}  |  已用: \${r[\"total_usage\"]:.4f}  |  剩余: \${remaining:.4f}')
        print()
    except Exception as e:
        print(f'Key: {label} — Error: {e}')
        print(result.stdout[:300])
        print()
"
```

### Preferred Query Order

1. **Credits API** (`/api/v1/credits`) — exact balance, returns `total_credits` and `total_usage` per account. Our keys are Management Keys so this works directly.
2. **Fallback** → `/api/v1/auth/key` + manual top-up table (if credits endpoint fails)

## Notes

- OpenRouter `/auth/key` API only returns **usage** (money spent), NOT account balance.
- "Est. Remaining" (Method 1) is calculated from our manually recorded top-up amounts minus usage.
- `/api/v1/credits` (Method 2) returns actual `total_credits` and `total_usage` — gives true remaining balance.
- Method 2 uses a **Management key** — both our keys are Management Keys on separate accounts, so credits are per-account.
- Each key's `/api/v1/credits` returns that account's own `total_credits` and `total_usage`.
- To check account credits in browser: https://openrouter.ai/settings/credits

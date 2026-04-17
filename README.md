# Hermes Custom Skills ⭐

> My personal collection of custom skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

These are the skills I've created and customized while using Hermes in my WSL2 + Windows workflow. Each one solves a specific problem or fills a gap in the official skill library.

## 📦 Quick Install

### Method 1: Clone and symlink

```bash
# Clone
git clone https://github.com/linbenyi/hermes-custom-skills.git ~/hermes-custom-skills

# Install (symlink each skill into Hermes)
for dir in ~/hermes-custom-skills/skills/*/; do
    name=$(basename "$dir")
    ln -sf "$dir" ~/.hermes/skills/custom-$name
done

# Verify
hermes skills list
```

### Method 2: Copy directly

```bash
git clone https://github.com/linbenyi/hermes-custom-skills.git ~/hermes-custom-skills

# Copy skills into Hermes
cp -r ~/hermes-custom-skills/skills/* ~/.hermes/skills/
```

### Method 3: Tap via Hermes Hub

```bash
hermes skills tap add https://github.com/linbenyi/hermes-custom-skills.git
hermes skills browse  # then install individually
```

## 📋 Skills Overview

| Skill | Category | Size | Description |
|-------|----------|------|-------------|
| [**telegram-winwhisper-tts**](#1-telegram-winwhisper-tts-) | Voice / Messaging | ~13KB | Complete Telegram voice pipeline: Windows STT + Chinese TTS + voice replies |
| [**context-dev**](#2-context-dev) | Research / Brand Data | ~16KB | Context.dev API integration: brand data, web scraping, screenshots, AI extraction |
| [**v2ex-info-monitoring**](#3-v2ex-info-monitoring) | Monitoring / Alerts | ~4KB | V2EX info monitoring via GitHub dataset, anomaly alerts |
| [**openrouter-balance**](#4-openrouter-balance) | API Management | ~5KB | OpenRouter API key balance and usage checker |
| [**skill-audit-and-recovery**](#5-skill-audit-and-recovery) | Development / Maintenance | ~5KB | Audit and classify local skills: keep / fix / archive |
| [**wsl2-web-service-windows-access**](#6-wsl2-web-service-windows-access) | DevOps | ~2KB | Access WSL2 web services from Windows browser |

---

## 1. telegram-winwhisper-tts ⭐

**The most complex and useful skill in this repo.**

Set up and troubleshoot a complete **Telegram voice message pipeline** where:

- Incoming voice messages arrive in WSL/Linux via Hermes Telegram gateway
- Speech-to-Text (STT) runs on **Windows-side faster-whisper** (GPU/CUDA)
- Replies are generated with **Edge TTS in Chinese** (`zh-CN-XiaoxiaoNeural`)
- Output is sent back as a **Telegram voice message** (OGG/Opus format)

### Architecture

```
Telegram Voice
     │
     ▼ (cached as .ogg)
WSL ~/.hermes/audio_cache/
     │
     ▼ (shared /mnt/c/ path)
Windows C:\faster-whisper\stt_run.bat
     │
     ▼ (faster-whisper STT)
Text transcript
     │
     ▼ (Edge TTS zh-CN-XiaoxiaoNeural)
Chinese reply audio (.mp3)
     │
     ▼ (ffmpeg → OGG/Opus)
Telegram sendVoice 💬
```

### Key Features

- **Path handoff rules**: Uses `/mnt/c/...` shared paths mapped to `C:\...` for reliable Windows invocation from WSL
- **GPU/CPU fallback**: Automatically falls back to CPU mode if CUDA libraries mismatch
- **Chinese TTS**: Explicit `zh-CN-XiaoxiaoNeural` voice for natural Chinese replies
- **Full troubleshooting guide**: 4 detailed diagnostic checklists for every failure mode

### Requirements

| Component | Location | Notes |
|-----------|----------|-------|
| faster-whisper | `C:\faster-whisper\` | Windows-side, GPU or CPU |
| ffmpeg | `C:\FFMPEG\bin\ffmpeg.exe` | Audio conversion |
| cmd.exe | `/mnt/c/Windows/System32/cmd.exe` | WSL→Windows shell invocation |

### Environment Variables

```bash
# Windows STT command wrapper
HERMES_WINDOWS_STT_COMMAND='C:\faster-whisper\stt_run.bat {input_path} {language}'
```

### References

- `references/local-setup.md` — Current verified local paths and command wiring (machine-specific, update when environment changes)

---

## 2. context-dev

Query the **Context.dev API** for structured brand data, web scraping, AI data extraction, screenshots, and industry classification — all from the terminal.

### Capabilities (16 actions)

| Category | Actions | Cost |
|----------|---------|------|
| **Brand Data** | by domain, name, email, stock ticker, ISIN, or transaction | 10 credits each |
| **Web Scraping** | HTML, Markdown, images, sitemap crawl | 1 credit each |
| **Screenshot** | viewport or full-page, specific page types (login, pricing, etc.) | 10 credits |
| **AI Extraction** | custom datapoints, product lists, single product lookup | 10 credits each |
| **Industry Classification** | NAICS codes by domain or input | 10 credits |

### Quick Examples

```bash
export CONTEXT_DEV_API_KEY="brand_xxxxxxxxx"

# Get brand data
python3 scripts/context_dev_query.py brand stripe.com

# Simplified brand lookup
python3 scripts/context_dev_query.py brand-simple example.com

# Scrape to Markdown
python3 scripts/context_dev_query.py scrape-md https://example.com true true

# Screenshot
python3 scripts/context_dev_query.py screenshot stripe.com true pricing

# Transaction identification
python3 scripts/context_dev_query.py brand-txn "AMZN MKTP US*1234567" "Seattle" "us"
```

### Requirements

```bash
pip install context.dev
```

Free tier: 500 API calls/month. Keys start with `brand_` prefix.

---

## 3. v2ex-info-monitoring

Monitor **[info.v2ex.pro](https://info.v2ex.pro/)** price, AAM inventory, and `livid` holdings using the underlying **GitHub daily dataset** instead of page scraping.

### Smart Design

Instead of fragile HTML scraping, this skill uses:
```
https://raw.githubusercontent.com/GrabCoffee/v2ex-info-newsletter-data/master/daily/{date}/
├── hodl_snapshots.json          → daily price & AAM snapshots
└── top50_address_changes.json   → holder address changes (detect livid)
```

### Anomaly Alert Rules

| Signal | Threshold |
|--------|-----------|
| Price change | ≥ ±8% day-over-day |
| AAM change | ≥ ±4% day-over-day |
| Livid amount change | ≥ $50,000 |
| Livid rank change | ≥ 5 positions |

### Usage Patterns

- Run weekly via cron job with pre-computed JSON output
- Only alerts when anomalies detected (quiet mode, no daily spam)
- Marks all-zero latest-day data as 采集异常 (collection error), not market crash
- Outputs compact summary with 📈📉⚠️💤 emojis

### Why This Skill?

The site has an RSS feed, but for structured numeric anomaly detection, the GitHub raw JSON source is:
- **More stable** — consistent JSON structure vs HTML rendering changes
- **Script-friendly** — parse-ready data, no DOM parsing needed
- **Historical** — daily snapshots allow trend analysis

---

## 4. openrouter-balance

Query **OpenRouter API key usage** and display balance summaries in Chinese.

### Features

- Reads keys automatically from `~/.hermes/auth.json` credential pool
- **Method 1** (exact): `/api/v1/credits` endpoint — returns actual `total_credits` and `total_usage`
- **Method 2** (fallback): `/api/v1/auth/key` endpoint + manual top-up tracking table

### Output Example

```
=== OpenRouter 余额查询 ===

Key 1: OPENROUTER_API_KEY (sk-or-v1-af5...3745)
  总充值: $20.00  |  已用: $3.2500  |  剩余: $16.7500
  今日: $0.1200  |  本周: $1.5000  |  本月: $3.2500
  免费层级: No   |  消费限额: 无

Key 2: 10Dollar (sk-or-v1-8dc...3dd0)
  总充值: $10.00  |  已用: $1.8000  |  剩余: $8.2000
  今日: $0.0500  |  本周: $0.8000  |  本月: $1.8000
  免费层级: No   |  消费限额: 无
```

### Notes

- Requires **Management Keys** — both configured keys are on separate OpenRouter accounts
- Each key's `/credits` endpoint returns that account's credits independently
- Update the key registry table when adding new keys or topping up

---

## 5. skill-audit-and-recovery

Audit a local skills directory and classify each skill as **keep**, **keep but fix**, or **archive/remove**.

### Use Cases

- Inherited an external skill library and need to clean it up
- Migrating skills from one agent system to another
- Periodic maintenance check — find stale or broken skills

### Workflow

1. **Inventory** each skill folder (SKILL.md, scripts, metadata files)
2. **Structural validation** — check file existence, path correctness, API compatibility
3. **Environment validation** — verify required binaries are actually installed
4. **Classification** — keep / fix / archive with reasons
5. **Generate todo list** — actionable cleanup items

### Common Stale Patterns Detected

- Documentation references scripts that no longer exist
- Skills built for obsolete tool APIs (old browser relay commands, legacy `message(...)` etc.)
- Wrapper scripts calling missing entrypoints while only helper files remain
- Metadata names that don't match folder structure

### Output

Concise report per skill:
- Status (keep / fix / archive)
- Reason for classification
- Recommended action

---

## 6. wsl2-web-service-windows-access

Access WSL2 web services (Flask, FastAPI, dashboards) from the Windows host browser.

### The Problem

WSL2 uses a virtual network adapter. `localhost` in WSL2 ≠ `localhost` on Windows. Flask starts on `0.0.0.0:5000` inside WSL2, but Windows can't reach it via `127.0.0.1`.

### Solutions

#### Quick: Use WSL2 IP
```bash
# Get the IP
hostname -I | awk '{print $1}'
# Example output: 172.19.154.123

# Access from Windows browser
http://172.19.154.123:5000
```

#### Permanent: Port Proxy
```powershell
# Run in Windows CMD/PowerShell as Administrator
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=127.0.0.1 connectport=5000 connectaddress=172.19.154.123
# Now access via http://localhost:5000
```

### Flask Code Snippet
```python
import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(f"Starting at http://{ip}:5000")
app.run(host='0.0.0.0', port=5000)
```

---

## 🗂️ Repository Structure

```
hermes-custom-skills/
├── README.md                              # This file
└── skills/
    ├── telegram-winwhisper-tts/
    │   ├── SKILL.md                       # Main skill documentation (9.4KB)
    │   └── references/
    │       └── local-setup.md             # Machine-specific path configuration (4.0KB)
    ├── context-dev/
    │   ├── SKILL.md                       # API usage guide (8.5KB)
    │   └── scripts/
    │       └── context_dev_query.py       # CLI wrapper script (7.4KB)
    ├── v2ex-info-monitoring/
    │   └── SKILL.md                       # Monitoring workflow (3.6KB)
    ├── openrouter-balance/
    │   └── SKILL.md                       # Balance checker guide (5.0KB)
    ├── skill-audit-and-recovery/
    │   └── SKILL.md                       # Audit workflow (4.6KB)
    └── wsl2-web-service-windows-access/
        └── SKILL.md                       # WSL2 networking guide (1.7KB)
```

## 💾 Total Size

~44KB across 8 files. Very lightweight!

## 📝 Updating

When you modify a skill locally:

```bash
cd ~/hermes-custom-skills
git add .
git commit -m "update: [skill-name] description"
git push
```

When updating the local Hermes skills after pulling changes:

```bash
cd ~/hermes-custom-skills
git pull

# Reinstall (if using symlinks)
for dir in ~/hermes-custom-skills/skills/*/; do
    name=$(basename "$dir")
    ln -sf "$dir" ~/.hermes/skills/custom-$name
done
```

## 🏷️ Tags

`hermes` `skills` `telegram` `stt` `tts` `faster-whisper` `context-dev` `openrouter` `v2ex` `wsl2` `voice`

# Hermes 自定义 Skills 合集 ⭐

> 我在 WSL2 + Windows 工作流中使用 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 时创建和定制的 Skills 集合。

每个 skill 都解决了一个特定问题，或者填补了官方 skill 库中的一个空白。

## 📦 快速安装

### 方法一：克隆并建立软链接

```bash
# 克隆仓库
git clone https://github.com/linbenyi/hermes-custom-skills.git ~/hermes-custom-skills

# 安装（将每个 skill 软链接到 Hermes）
for dir in ~/hermes-custom-skills/skills/*/; do
    name=$(basename "$dir")
    ln -sf "$dir" ~/.hermes/skills/custom-$name
done

# 验证
hermes skills list
```

### 方法二：直接复制

```bash
git clone https://github.com/linbenyi/hermes-custom-skills.git ~/hermes-custom-skills

# 直接复制到 Hermes 的 skills 目录
cp -r ~/hermes-custom-skills/skills/* ~/.hermes/skills/
```

### 方法三：通过 Hermes Hub 添加源

```bash
hermes skills tap add https://github.com/linbenyi/hermes-custom-skills.git
hermes skills browse  # 然后逐个安装
```

## 📋 Skills 一览

| Skill | 分类 | 大小 | 简介 |
|-------|------|------|------|
| [**telegram-winwhisper-tts**](#1-telegram-winwhisper-tts-) | 语音 / 消息 | ~13KB | 完整的 Telegram 语音管道：Windows STT + 中文 TTS + 语音回复 |
| [**context-dev**](#2-context-dev) | 研究 / 品牌数据 | ~16KB | Context.dev API 集成：品牌数据、网页抓取、截图、AI 提取 |
| [**v2ex-info-monitoring**](#3-v2ex-info-monitoring) | 监控 / 告警 | ~4KB | V2EX 信息监控（基于 GitHub 数据集），异常告警 |
| [**openrouter-balance**](#4-openrouter-balance) | API 管理 | ~5KB | OpenRouter API key 余额和用量查询器 |
| [**skill-audit-and-recovery**](#5-skill-audit-and-recovery) | 开发 / 维护 | ~5KB | 审计和分类本地 skills：保留 / 修复 / 归档 |
| [**wsl2-web-service-windows-access**](#6-wsl2-web-service-windows-access) | DevOps | ~2KB | Windows 浏览器访问 WSL2 Web 服务 |

---

## 1. telegram-winwhisper-tts ⭐

**本仓库中最复杂、最实用的 skill！**

搭建并排查一个完整的 **Telegram 语音消息管道** 的问题，流程如下：

- 语音消息通过 Hermes Telegram 网关到达 WSL/Linux
- 语音识别（STT）在 **Windows 侧的 faster-whisper** 上运行（GPU/CUDA）
- 回复内容通过 **Edge TTS 以中文生成**（`zh-CN-XiaoxiaoNeural`）
- 输出经转码后作为 **Telegram 语音消息**（OGG/Opus 格式）发回

### 架构流程

```
Telegram 语音消息
     │
     ▼（缓存为 .ogg 文件）
WSL ~/.hermes/audio_cache/
     │
     ▼（通过 /mnt/c/ 共享路径）
Windows C:\faster-whisper\stt_run.bat
     │
     ▼（faster-whisper 语音识别）
文本转录结果
     │
     ▼（Edge TTS zh-CN-XiaoxiaoNeural）
中文回复音频 (.mp3)
     │
     ▼（ffmpeg → OGG/Opus）
Telegram sendVoice 发回 💬
```

### 核心特性

- **路径传递规则**：使用 `/mnt/c/...` 共享路径映射到 `C:\...`，从 WSL 可靠调用 Windows 工具
- **GPU/CPU 降级**：CUDA 库不匹配时自动降级到 CPU 模式
- **中文 TTS**：明确使用 `zh-CN-XiaoxiaoNeural` 语音，确保中文回复自然流畅
- **完整的排查指南**：4 个详细的诊断检查清单，涵盖所有常见故障

### 环境要求

| 组件 | 位置 | 说明 |
|------|------|------|
| faster-whisper | `C:\faster-whisper\` | Windows 端，GPU 或 CPU |
| ffmpeg | `C:\FFMPEG\bin\ffmpeg.exe` | 音频格式转换 |
| cmd.exe | `/mnt/c/Windows/System32/cmd.exe` | WSL→Windows 外壳调用 |

### 环境变量

```bash
# Windows STT 命令封装
HERMES_WINDOWS_STT_COMMAND='C:\faster-whisper\stt_run.bat {input_path} {language}'
```

### 参考文件

- `references/local-setup.md` — 当前验证的本地路径和命令配置（机器相关，环境变化时需更新）

---

## 2. context-dev

从终端查询 **Context.dev API**，获取结构化品牌数据、网页抓取、AI 数据提取、截图、行业分类等功能。

### 功能一览（16 种操作）

| 类别 | 操作 | 费用 |
|------|------|------|
| **品牌数据** | 通过域名、名称、邮箱、股票代码、ISIN、交易记录查询 | 各 10 credits |
| **网页抓取** | HTML、Markdown、图片、sitemap 爬取 | 各 1 credit |
| **截图** | 视口截图、全页截图、指定页面类型（登录、定价等） | 10 credits |
| **AI 提取** | 自定义数据点、产品列表、单品信息提取 | 各 10 credits |
| **行业分类** | 通过域名或输入获取 NAICS 编码分类 | 10 credits |

### 快速示例

```bash
export CONTEXT_DEV_API_KEY="brand_xxxxxxxxx"

# 获取品牌数据
python3 scripts/context_dev_query.py brand stripe.com

# 简化版品牌查询
python3 scripts/context_dev_query.py brand-simple example.com

# 抓取页面为 Markdown（包含图片和链接）
python3 scripts/context_dev_query.py scrape-md https://example.com true true

# 网站截图（指定定价页面）
python3 scripts/context_dev_query.py screenshot stripe.com true pricing

# 交易记录商户识别
python3 scripts/context_dev_query.py brand-txn "AMZN MKTP US*1234567" "Seattle" "us"
```

### 安装要求

```bash
pip install context.dev
```

免费额度：每月 500 次 API 调用。Key 以 `brand_` 为前缀。

---

## 3. v2ex-info-monitoring

监控 **[info.v2ex.pro](https://info.v2ex.pro/)** 的价格、AAM 库存量和 `livid` 持有量，使用底层的 **GitHub 每日数据集** 而非页面抓取。

### 设计理念

避免脆弱的 HTML 抓取，直接读取 GitHub 数据源的原始 JSON：
```
https://raw.githubusercontent.com/GrabCoffee/v2ex-info-newsletter-data/master/daily/{date}/
├── hodl_snapshots.json          ← 每日价格 & AAM 快照
└── top55_address_changes.json   ← 持有人地址变化（用于检测 livid）
```

### 异常告警规则

| 信号 | 阈值 |
|------|------|
| 价格变化 | ≥ ±8%（日环比） |
| AAM 变化 | ≥ ±4%（日环比） |
| livid 金额变化 | ≥ $50,000 |
| livid 排名变化 | ≥ 5 位 |

### 使用方式

- 通过 cron 定时任务每周运行，附带预计算的 JSON 输出
- 仅在检测到异常时才推送告警（安静模式，无每日刷屏）
- 最新日数据全零时会标记为 **采集异常**，而非市场暴跌
- 输出简洁中文摘要，带有 📈📉⚠️💤 emoji 标记

### 为什么选择这个方案？

网站有 RSS 订阅，但对于结构化的数值异常检测，GitHub 原始 JSON 数据源：
- **更稳定** — JSON 结构一致，不怕页面渲染变化
- **脚本友好** — 直接解析，无需 DOM 处理
- **历史可追溯** — 每日快照支持趋势分析

---

## 4. openrouter-balance

查询 **OpenRouter API key 用量**，并以中文显示余额摘要。

### 功能

- 自动从 `~/.hermes/auth.json` 凭证池读取 key
- **方法一**（精确）：`/api/v1/credits` 端点 — 返回实际的 `total_credits` 和 `total_usage`
- **方法二**（备用）：`/api/v1/auth/key` 端点 + 手动记录的充值金额表

### 输出示例

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

### 注意事项

- 需要 **Management Keys** — 两个已配置的 key 分别属于不同的 OpenRouter 账户
- 每个 key 的 `/credits` 端点独立返回对应账户的额度
- 添加新 key 或充值时，请更新 skill 中的 key 登记表

---

## 5. skill-audit-and-recovery

审计本地 skills 目录，将每个 skill 分类为 **保留**、**保留但需修复** 或 **归档/删除**。

### 适用场景

- 从外部继承了一个 skill 库，需要清理
- 从一个 agent 系统迁移 skills 到另一个
- 定期检查 — 发现过期或损坏的 skills

### 工作流程

1. **盘点** 每个 skill 文件夹（SKILL.md、脚本、元数据文件）
2. **结构验证** — 检查文件是否存在、路径是否正确、API 是否兼容
3. **环境验证** — 确认所需二进制程序确实已安装
4. **分类** — 保留 / 修复 / 归档并附原因
5. **生成待办清单** — 具体的清理项目

### 常见的过期模式

- 文档引用的脚本已不存在
- 为过时工具 API 构建的 skills（旧版浏览器 relay 命令、遗留 `message(...)` 等）
- 封装脚本调用已不存在的入口点，仅剩余辅助文件
- 元数据名称与文件夹结构不匹配

### 输出

每个 skill 的简洁报告：
- 状态（保留 / 修复 / 归档）
- 分类原因
- 推荐操作

---

## 6. wsl2-web-service-windows-access

从 Windows 主机浏览器访问 WSL2 中运行的 Web 服务（Flask、FastAPI、Dashboard 等）。

### 问题背景

WSL2 使用虚拟网络适配器。WSL2 内的 `localhost` ≠ Windows 上的 `localhost`。Flask 在 WSL2 内启动于 `0.0.0.0:5000`，但 Windows 无法通过 `127.0.0.1` 访问它。

### 解决方案

#### 快速方案：使用 WSL2 IP
```bash
# 获取 WSL2 IP 地址
hostname -I | awk '{print $1}'
# 输出示例: 172.19.154.123

# Windows 浏览器访问
http://172.19.154.123:5000
```

#### 永久方案：端口代理
```powershell
# 在 Windows CMD/PowerShell 中以管理员身份运行
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=127.0.0.1 connectport=5000 connectaddress=172.19.154.123
# 之后即可通过 http://localhost:5000 访问
```

### Flask 代码示例
```python
import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(f"Starting at http://{ip}:5000")
app.run(host='0.0.0.0', port=5000)
```

---

## 🗂️ 仓库结构

```
hermes-custom-skills/
├── README.md                              # 英文说明文档
├── README_zh.md                           # 中文说明文档（本文件）
├── .gitignore
└── skills/
    ├── telegram-winwhisper-tts/
    │   ├── SKILL.md                       # 主文档说明 (9.4KB)
    │   └── references/
    │       └── local-setup.example.md     # 本地路径配置模板 (1.8KB)
    ├── context-dev/
    │   ├── SKILL.md                       # API 使用指南 (8.5KB)
    │   └── scripts/
    │       └── context_dev_query.py       # CLI 封装脚本 (7.4KB)
    ├── v2ex-info-monitoring/
    │   └── SKILL.md                       # 监控工作流 (3.6KB)
    ├── openrouter-balance/
    │   └── SKILL.md                       # 余额查询指南 (5.0KB)
    ├── skill-audit-and-recovery/
    │   └── SKILL.md                       # 审计工作流 (4.6KB)
    └── wsl2-web-service-windows-access/
        └── SKILL.md                       # WSL2 网络指南 (1.7KB)
```

## 💾 总计大小

**8 个文件 · ~44KB**，非常轻量！

## 📝 更新方法

本地修改 skill 后同步到仓库：

```bash
cd ~/hermes-custom-skills
git add .
git commit -m "update: [skill名称] 说明"
git push
```

拉取更新后重新安装：

```bash
cd ~/hermes-custom-skills
git pull

# 重新安装（软链接方式）
for dir in ~/hermes-custom-skills/skills/*/; do
    name=$(basename "$dir")
    ln -sf "$dir" ~/.hermes/skills/custom-$name
done
```

## 🏷️ 标签

`hermes` `skills` `telegram` `stt` `tts` `faster-whisper` `context-dev` `openrouter` `v2ex` `wsl2` `语音` `中文`

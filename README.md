# 🎀 Discord Promo Checker 🎀

> *fast. silent. accurate.*

[![Telegram](https://img.shields.io/badge/channel-t.me%2Fcheaprip-blue?style=for-the-badge&logo=telegram&logoColor=white&color=7289da)](https://t.me/cheaprip)
[![Author](https://img.shields.io/badge/author-%40badykarma-pink?style=for-the-badge&logo=telegram&logoColor=white&color=ff69b4)](https://t.me/badykarma)
[![Language](https://img.shields.io/badge/python-3.10%2B-purple?style=for-the-badge&logo=python&logoColor=white&color=9b59b6)](https://python.org)
[![Async](https://img.shields.io/badge/async-aiohttp-blueviolet?style=for-the-badge&color=7d3c98)](https://docs.aiohttp.org)

---

*async discord promotion code checker with multi-token & proxy rotation*

</div>

---

## ✨ features

```
  ✅  async checking with configurable worker pool
  🔄  round-robin token rotation across all requests  
  🌍  proxy rotation — http / https / socks4 / socks5
  🔐  authenticated proxy support (user:pass@host:port)
  🕒  automatic rate limit handling with retry
  🔒  async file locking — no duplicate writes ever
  📝  timestamped error logging to error.txt
  💾  valid codes → valid.txt | claimed → claimed.txt
```

---

## 📦 installation

```bash
pip install aiohttp tasksio colorama pyfiglet python-dateutil
```

---

## 📁 file structure

```
📂 promo-checker/
 ├── 🐍 checker.py          ← main script
 ├── 🪙 tokens.txt          ← your discord tokens (one per line)
 ├── 🎟️  promotions.txt      ← promo codes or urls (one per line)
 ├── 🌐 proxies.txt         ← proxies (one per line, optional)
 │
 ├── ✅ valid.txt            ← auto-generated: working codes
 ├── 🚫 claimed.txt         ← auto-generated: fully used codes
 └── 📋 error.txt           ← auto-generated: error log
```

> `valid.txt`, `claimed.txt`, and `error.txt` are created automatically on first run.

---

## 🌐 proxy formats

all formats supported:

```
host:port
user:pass@host:port
http://host:port
http://user:pass@host:port
socks5://host:port
socks5://user:pass@host:port
socks4://host:port
```

---

## 🎟️ promo formats

paste anything into `promotions.txt` — raw codes or full urls both work:

```
https://discord.com/billing/promotions/XXXXXXXXXX
https://promos.discord.gg/XXXXXXXXXX
XXXXXXXXXX
```

---

## 🚀 usage

```bash
python checker.py
```

you'll be asked two things at startup:

| prompt | default | description |
|--------|---------|-------------|
| ⏳ delay | `0.5s` | seconds between dispatching each code |
| ⚡ workers | `50` | max concurrent requests running at once |

just hit enter to use the defaults.

---

## 📊 output

| file | what goes in it |
|------|----------------|
| `✅ valid.txt` | active, claimable promotion codes |
| `🚫 claimed.txt` | codes that exist but are fully redeemed |
| `📋 error.txt` | timestamped log of all warnings and errors |

---

## ⚙️ how it works

```
promotions.txt
      │
      ▼
  [task pool] ── up to N workers running at once
      │
      ├─ picks next token  (round-robin)
      ├─ picks next proxy  (round-robin)
      └─ fires GET request to discord api
            │
            ├─ 200 → valid!    → saved to valid.txt
            ├─ max uses hit    → saved to claimed.txt  
            ├─ 429 rate limit  → sleeps, retries same code
            └─ anything else   → logged to error.txt
```

---

## ⚠️ notes

- tokens and proxies cycle **round-robin** — every code gets a fresh token + proxy
- on `429` rate limit the script sleeps for the exact `retry_after` time then retries
- running without `proxies.txt` is fine — requests just go direct
- file writes are protected by an async lock so no duplicates even at high concurrency

---

<div align="center">

---

```
made with 🤍 by @badykarma
```

### 🔗 [t.me/cheaprip](https://t.me/cheaprip)
*join for more tools, promos, tokens*

---

</div>

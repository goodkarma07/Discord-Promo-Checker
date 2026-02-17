# promo-checker

**by [@badykarma](https://t.me/badykarma) | [t.me/cheaprip](https://t.me/cheaprip)**

fast async discord promotion code checker with multi-token + proxy rotation support.

---

## features

- async checking via `aiohttp` + `tasksio` task pool
- multi-token rotation (round-robin)
- proxy rotation with support for `http`, `https`, `socks4`, `socks5`
- auth proxy support (`user:pass@host:port`)
- rate limit handling with auto-retry
- duplicate-safe output writing with async file lock
- logs warnings/errors to `error.txt` with timestamps
- valid codes saved to `valid.txt`, fully claimed to `claimed.txt`

---

## setup

```
pip install aiohttp tasksio colorama pyfiglet python-dateutil
```

---

## files

before running, place the following files in the same directory as `main.py`:

| file | contents |
|------|----------|
| `tokens.txt` | one discord token per line |
| `promotions.txt` | one promo code or full url per line |
| `proxies.txt` | one proxy per line (optional) |

`valid.txt`, `claimed.txt`, and `error.txt` are created automatically on first run.

---

## proxy formats

all of the following formats are supported:

```
host:port
user:pass@host:port
http://host:port
http://user:pass@host:port
socks5://host:port
socks5://user:pass@host:port
```

---

## promo formats

both raw codes and full urls work in `promotions.txt`:

```
https://discord.com/billing/promotions/XXXXXXXXXX
https://promos.discord.gg/XXXXXXXXXX
XXXXXXXXXX
```

---

## usage

```
python checker.py
```

you'll be prompted for:
- **delay** — seconds between dispatching each code (default `0.5`)
- **workers** — max concurrent requests (default `50`)

---

## output

| file | description |
|------|-------------|
| `valid.txt` | codes that are valid and still active |
| `claimed.txt` | codes that exist but are fully used |
| `error.txt` | timestamped log of warnings and errors |

---

## notes

- tokens and proxies are cycled round-robin across all codes
- on rate limit (`429`), the checker sleeps for the `retry_after` duration then retries the same code
- if no `proxies.txt` is found or it's empty, requests go through without a proxy

---

made by **@badykarma** — join **[t.me/cheaprip](https://t.me/cheaprip)** for more tools

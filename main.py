import asyncio
import aiohttp
import datetime
import random
import sys
import os
import itertools
import urllib.parse
import re
from dateutil import parser
import tasksio
from colorama import Fore, Style, init as colorama_init
import pyfiglet
from datetime import datetime as dt

colorama_init(autoreset=True)

# =============================== LOGGING ===============================

LOG_FILE = "error.txt"

def log_to_file(msg: str):
    with open(LOG_FILE, "a", encoding="utf-8", errors="ignore") as f:
        f.write(f"[{dt.utcnow().isoformat()} UTC] {msg}\n")

def format_section(emoji, color, text):
    return f"{color}{emoji} {text}{Fore.RESET}{Style.NORMAL}"

def LOG_SUCCESS(text): print(format_section("✅", Fore.GREEN, text))
def LOG_WARN(text):
    print(format_section("⚠️", Fore.LIGHTYELLOW_EX, text))
    log_to_file(f"[WARN] {text}")
def LOG_ERROR(text):
    print(format_section("❌", Fore.RED, text))
    log_to_file(f"[ERROR] {text}")
def LOG_INFO(text): print(format_section("🌀", Fore.LIGHTMAGENTA_EX, text))
def LOG_DEBUG(text): print(format_section("🧠", Fore.LIGHTBLUE_EX, text))

# =============================== FILE PREP ===============================

for path in ("promotions.txt", "tokens.txt", "valid.txt", "claimed.txt", LOG_FILE):
    if not os.path.exists(path):
        open(path, "w", encoding="utf-8").close()

# =============================== BANNER ===============================

os.system("cls" if os.name == "nt" else "clear")
if os.name == "nt":
    os.system("title Promo Checker @badykarma t.me/cheaprip")

banner = pyfiglet.figlet_format("UwU")
print(f"{Fore.LIGHTMAGENTA_EX}{banner}{Fore.RESET}")
LOG_INFO("Multi-Token + Proxy Rotation | @badykarma | t.me/cheaprip")

# =============================== CONFIG ===============================

def input_float(prompt, default: float):
    LOG_INFO(f"{prompt} (default {default})")
    raw = input("> ").strip()
    try:
        return float(raw) if raw else default
    except Exception:
        return default

def input_int(prompt, default: int):
    LOG_INFO(f"{prompt} (default {default})")
    raw = input("> ").strip()
    try:
        return int(raw) if raw else default
    except Exception:
        return default

delay = input_float("Delay between requests (seconds)", 0.5)
workers = input_int("Workers (concurrency)", 50)

# =============================== LOAD ===============================

def load_list_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [l.strip() for l in f.read().splitlines() if l.strip()]

tokens = load_list_file("tokens.txt")
if not tokens:
    LOG_ERROR("No tokens found in tokens.txt")
    sys.exit(1)

proxies_raw = load_list_file("proxies.txt")
LOG_SUCCESS(f"Loaded {len(tokens)} token(s)")
LOG_INFO(f"Loaded {len(proxies_raw)} proxy line(s)")

# =============================== PROXY PARSER ===============================

def parse_proxy_line(line: str):
    if not line:
        return None, None
    s = line.strip()
    scheme = "http"
    m = re.match(r"^(?P<scheme>https?|socks5?|socks4?)://(?P<rest>.+)$", s, flags=re.IGNORECASE)
    rest = m.group("rest") if m else s
    if m:
        scheme = m.group("scheme").lower()
    user = password = None
    if "@" in rest:
        userinfo, hostport = rest.rsplit("@", 1)
        if ":" in userinfo:
            user, password = userinfo.split(":", 1)
        else:
            user, password = userinfo, ""
    else:
        hostport = rest
    m2 = re.match(r"^(?P<scheme>https?|socks5?|socks4?)://(?P<hp>.+)$", hostport, flags=re.IGNORECASE)
    if m2:
        scheme = m2.group("scheme").lower()
        hostport = m2.group("hp")
    proxy_url = f"{scheme}://{hostport}"
    proxy_auth = None
    if user is not None:
        proxy_auth = aiohttp.BasicAuth(user, password or "")
    return proxy_url, proxy_auth

parsed_proxies = [(p, *parse_proxy_line(p)) for p in proxies_raw]

# =============================== FILE HELPERS ===============================

file_lock = asyncio.Lock()

async def file_contains(path, item):
    def _check():
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return any(line.strip() == item for line in f)
    return await asyncio.to_thread(_check)

async def append_unique(path, item):
    async with file_lock:
        if not await file_contains(path, item):
            def _write():
                with open(path, "a+", encoding="utf-8", errors="ignore") as f:
                    f.write(item + "\n")
            await asyncio.to_thread(_write)
        else:
            LOG_WARN(f"Duplicate Found -> {item}")

# =============================== ROTATION ===============================

token_cycle = itertools.cycle(tokens)
proxy_cycle = itertools.cycle(parsed_proxies) if parsed_proxies else None

def pick_token():
    return next(token_cycle)

def pick_proxy_triplet():
    return next(proxy_cycle) if proxy_cycle else (None, None, None)

# =============================== CHECK ===============================

async def check(promocode: str):
    token = pick_token()
    raw_proxy_line, proxy_url, proxy_auth = pick_proxy_triplet()
    headers = {"Authorization": token}
    url = f"https://ptb.discord.com/api/v10/entitlements/gift-codes/{promocode}"
    timeout = aiohttp.ClientTimeout(total=30)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, proxy=proxy_url, proxy_auth=proxy_auth) as rs:
                status = rs.status

                if status in (200, 201, 204):
                    data = None
                    try:
                        data = await rs.json()
                    except Exception:
                        pass

                    if data and "uses" in data and "max_uses" in data and data["uses"] == data["max_uses"]:
                        LOG_WARN(f"Claimed {promocode}")
                        await append_unique("claimed.txt", f"https://discord.com/billing/promotions/{promocode}")
                        return

                    try:
                        now = datetime.datetime.utcnow()
                        exp_at = data.get("expires_at") if data else None
                        if exp_at:
                            exp_at_parsed = parser.parse(exp_at.split(".")[0])
                            days = abs((now - exp_at_parsed).days)
                        else:
                            exp_at, days = "Unknown", "?"
                        title_txt = (data.get("promotion") or {}).get("inbound_header_text", "Unknown Title") if data else "Unknown Title"
                    except Exception:
                        exp_at, days, title_txt = "Failed", "?", "Failed"

                    LOG_SUCCESS(f"Valid {promocode} | {days}d | {title_txt}")
                    await append_unique("valid.txt", f"https://discord.com/billing/promotions/{promocode}")
                    return

                if status == 429:
                    try:
                        det = await rs.json()
                        retry_after = float(det.get("retry_after", 3))
                    except Exception:
                        retry_after = 3.0
                    LOG_WARN(f"Rate Limited {retry_after:.1f}s | token ...{token[-4:]}")
                    await asyncio.sleep(retry_after)
                    await check(promocode)
                    return

                LOG_ERROR(f"Invalid Code {promocode} (status {status})")

    except aiohttp.ClientProxyConnectionError as e:
        LOG_ERROR(f"Proxy failed [{raw_proxy_line}] {e}")
    except aiohttp.ClientHttpProxyError as e:
        LOG_ERROR(f"HTTP Proxy error [{raw_proxy_line}] {e}")
    except aiohttp.ClientConnectorError as e:
        LOG_ERROR(f"Connection error [{raw_proxy_line or 'no-proxy'}] {e}")
    except asyncio.TimeoutError:
        LOG_ERROR(f"Timeout {promocode} via [{raw_proxy_line or 'no-proxy'}]")
    except Exception as e:
        LOG_ERROR(f"Unexpected {promocode} via [{raw_proxy_line or 'no-proxy'}]: {e}")

# =============================== MAIN ===============================

async def start():
    with open("promotions.txt", "r", encoding="utf-8", errors="ignore") as f:
        codes_raw = [line.strip() for line in f.read().splitlines() if line.strip()]

    codes = [
        s.replace('https://discord.com/billing/promotions/', '')
         .replace('https://promos.discord.gg/', '')
         .strip().strip('/')
        for s in codes_raw
    ]

    LOG_INFO(f"Starting with {len(codes)} codes | {len(tokens)} tokens | {len(parsed_proxies)} proxies")

    async with tasksio.TaskPool(workers=workers) as pool:
        for promo in codes:
            await pool.put(check(promo))
            if delay > 0:
                await asyncio.sleep(delay)

if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        LOG_WARN("Interrupted by user")
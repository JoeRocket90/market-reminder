#!/usr/bin/env python3
"""
JoeRocketPortfolio — Market Scan Reminder
==========================================
Sendet täglich um 09:30 und 16:30 MEZ eine Telegram-Erinnerung,
im Claude-Chat "Screening" einzugeben und den 8-Punkte-Megatrend-Scan auszuführen.

Self-adjusting für Sommer-/Winterzeit:
  - GitHub Actions Cron läuft in UTC
  - Python prüft lokale MEZ/MESZ-Zeit
  - Sendet nur, wenn aktuell ±15 Min um 09:30 oder 16:30 MEZ
"""

import os
import sys
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# ────────────────────────────────────────────────────────────────────────────
# Konfiguration via GitHub Secrets
# ────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlt")
    print("   → Repository Settings → Secrets → Actions → Neues Secret")
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# Zeitfenster-Check (DST-resilient)
# ────────────────────────────────────────────────────────────────────────────
now_mez = datetime.now(ZoneInfo("Europe/Berlin"))
hour, minute = now_mez.hour, now_mez.minute

# Morgen-Scan: 09:15 – 09:45 MEZ
is_morning = (hour == 9 and 15 <= minute <= 45)
# Nachmittag-Scan: 16:15 – 16:45 MEZ
is_afternoon = (hour == 16 and 15 <= minute <= 45)

if not (is_morning or is_afternoon):
    print(f"⏸  Außerhalb Scan-Fenster ({now_mez.strftime('%H:%M')} MEZ) — übersprungen.")
    sys.exit(0)

# ────────────────────────────────────────────────────────────────────────────
# Session-spezifische Nachricht
# ────────────────────────────────────────────────────────────────────────────
if is_morning:
    session_emoji = "🌅"
    session_name = "MORGEN-SCAN"
    session_focus = "EU Pre-Open + US Pre-Market Setup"
    session_hint = "Fokus: Übernacht-News, Asia-Schluss, EU-Eröffnung"
else:
    session_emoji = "☀️"
    session_name = "NACHMITTAG-SCAN"
    session_focus = "US Post-Open + Intraday-Momentum"
    session_hint = "Fokus: 1h nach US-Open, echte Volumen-Confirmation"

message = f"""{session_emoji} {session_name} — JoeRocketPortfolio

⏰ {now_mez.strftime('%A, %d.%m.%Y · %H:%M')} MEZ
📊 {session_focus}
💡 {session_hint}

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TO-DO

1️⃣  Claude.ai öffnen
2️⃣  "Screening" eingeben
3️⃣  8-Punkte-Scan abwarten (~2 Min)
4️⃣  Top-Signale mit WKNs prüfen
5️⃣  Bei Entry: WKN + Kurs + Stückzahl zurück an Claude
━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Megatrend-Watchlist (14 Ticker)
🤖 NVDA · ASML      AI & Halbleiter
🚀 RKLB · ASTS      Space
🦾 ISRG · AXON      Robotik
₿  MSTR · MARA      Krypto
⚡ XOM  · MPC       Energie
💊 LLY  · NVO       Healthcare GLP-1
🥇 GLD  · GDXJ      Gold
🛡 RHM  · AIR       Rüstung EU

🔭 Emerging Trends Radar: Quantum · Nuclear SMR · Custom AI Silicon · Drohnen-Abwehr

Let's rocket! 🚀"""

# ────────────────────────────────────────────────────────────────────────────
# Telegram API Call
# ────────────────────────────────────────────────────────────────────────────
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message,
    # Kein parse_mode — verhindert schwarze Balken (aus Scanner-V9-Learnings)
}

try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print(f"✅ Reminder gesendet — {now_mez.strftime('%Y-%m-%d %H:%M:%S')} MEZ")
    print(f"   Session: {session_name}")
except requests.exceptions.RequestException as e:
    print(f"❌ Telegram-API Fehler: {e}")
    if hasattr(e, "response") and e.response is not None:
        print(f"   Status: {e.response.status_code}")
        print(f"   Body: {e.response.text}")
    sys.exit(1)

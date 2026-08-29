# -*- coding: utf-8 -*-
"""بناء رسالة تليجرام (بتصميم عربي منظم) وإرسالها."""
from __future__ import annotations

import datetime as dt
import time

import requests

from . import config
from .content import HASHTAGS_AR, HASHTAGS_EN
from .fetchers import NewsItem

MAX_LEN = 4096  # حد تليجرام للرسالة الواحدة


def _fmt_items(items: list[NewsItem], limit: int = 5) -> str:
    lines = []
    for it in items[:limit]:
        lines.append(f"• <b>{_esc(it.title)}</b>\n  🔗 {it.link}  <i>({_esc(it.source)})</i>")
    return "\n".join(lines) if lines else "— لا يوجد جديد اليوم"


def _esc(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_message(
    buckets: dict[str, list[NewsItem]],
    story: NewsItem | None,
    script: dict[str, str],
    ideas: list[str],
) -> str:
    today = dt.date.today().strftime("%Y-%m-%d")
    parts = [
        f"🤖 <b>نشرة الذكاء الاصطناعي اليومية</b> — {today}",
        "═══════════════════",
    ]

    if buckets.get("saudi"):
        parts += ["\n🇸🇦 <b>السوق السعودي والخليجي</b>", _fmt_items(buckets["saudi"])]
    if buckets.get("global"):
        parts += ["\n🌍 <b>أمريكا والعالم</b>", _fmt_items(buckets["global"])]
    if buckets.get("arabic"):
        parts += ["\n📰 <b>مصادر عربية</b>", _fmt_items(buckets["arabic"], 3)]
    if buckets.get("github"):
        parts += ["\n⭐ <b>مشاريع GitHub صاعدة</b>", _fmt_items(buckets["github"], config.MAX_GITHUB_REPOS)]

    if story:
        parts += [
            "\n═══════════════════",
            "🎬 <b>ريل اليوم — جاهز للتصوير</b>",
            f"\n📌 <b>الخبر المختار:</b> {_esc(story.title)}",
            f"\n🪝 <b>الهوك (أول ٣ ثواني):</b>\n{_esc(script['hook'])}",
            f"\n🗣 <b>وش تقول بالضبط:</b>\n{_esc(script['body'])}",
            f"\n📢 <b>الختام (CTA):</b>\n{_esc(script['cta'])}",
        ]

    if ideas:
        parts += ["\n💡 <b>أفكار محتوى إضافية:</b>"]
        parts += [f"{i+1}. {_esc(idea)}" for i, idea in enumerate(ideas)]

    parts += [f"\n#️⃣ <b>الهاشتاقات:</b>\n{HASHTAGS_AR}\n{HASHTAGS_EN}"]

    return "\n".join(parts)


def _split(text: str) -> list[str]:
    """تقسيم الرسالة لو تجاوزت حد تليجرام."""
    chunks, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX_LEN:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


def _post_chunk(url: str, chunk: str, retries: int = 3) -> bool:
    """يرسل جزء واحد مع احترام حد تليجرام (429 Too Many Requests)."""
    for attempt in range(retries):
        try:
            r = requests.post(
                url,
                json={
                    "chat_id": config.TELEGRAM_CHAT_ID,
                    "text": chunk,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )
            if r.status_code == 429:
                wait = int(r.json().get("parameters", {}).get("retry_after", 5)) + 1
                print(f"[…] تليجرام يطلب انتظار {wait} ثانية — بننتظر")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return True
        except Exception as e:
            if attempt == retries - 1:
                print(f"[!] فشل إرسال جزء من الرسالة: {e}")
                return False
            time.sleep(2 * (attempt + 1))
    return False


def send_message(text: str) -> bool:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[!] رجاءً عبّي TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID في ملف .env")
        return False

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    # نرسل كل الأجزاء حتى لو فشل جزء (list مو generator — عشان ما يوقف short-circuit)
    return all([_post_chunk(url, chunk) for chunk in _split(text)])

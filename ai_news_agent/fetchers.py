# -*- coding: utf-8 -*-
"""جلب الأخبار من مصادر متعددة:
- مصادر عالمية/أمريكية (مدونات الشركات الكبرى + مواقع تقنية)
- مصادر عربية/سعودية
- GitHub Trending (مشاريع AI)
كلها مصادر مجانية (RSS + GitHub API) بدون أي مفاتيح مدفوعة.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import feedparser
import requests

from .filters import is_ai_related
from .sources import ARABIC_SOURCES, DEFAULT_REGIONS, sources_for

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

# المصادر كلها انتقلت إلى ai_news_agent/sources.py — عدّلها من هناك.

# كلمات مفتاحية لتصنيف الخبر (سعودي/خليجي)
SAUDI_KEYWORDS = [
    "سعود", "السعودية", "الرياض", "جدة", "نيوم", "سدايا", "أرامكو", "هيوماين",
    "saudi", "riyadh", "neom", "sdaia", "aramco", "humain", "gulf", "uae", "خليج",
]



@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published: str = ""
    summary: str = ""
    category: str = "global"  # المنطقة: usa | china | saudi | tools ...
    score: int = 0  # درجة قابلية الانتشار (viral.py)
    tags: list[str] = field(default_factory=list)


def _clean(text: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(text.split())


def _is_recent(entry, hours: int = 48) -> bool:
    """نأخذ فقط أخبار آخر 48 ساعة (عشان المحتوى يكون يومي وجديد)."""
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            published = dt.datetime(*t[:6])
            return (dt.datetime.utcnow() - published) <= dt.timedelta(hours=hours)
    return True  # لو ما فيه تاريخ، نعرضه احتياطًا


def _matches(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return any(k in low for k in keywords)


def fetch_feed(name: str, url: str, arabic: bool = False) -> list[NewsItem]:
    items: list[NewsItem] = []
    try:
        parsed = feedparser.parse(url, request_headers=HEADERS)
        for entry in parsed.entries[:15]:
            if not _is_recent(entry):
                continue
            title = _clean(entry.get("title", ""))
            summary = _clean(entry.get("summary", ""))[:400]
            text = f"{title} {summary}"

            # المصادر العامة (غير المتخصصة): نمرر فقط أخبار الـ AI
            if arabic and not is_ai_related(text):
                continue

            category = "arabic" if arabic else "global"
            if _matches(text, SAUDI_KEYWORDS):
                category = "saudi"

            items.append(
                NewsItem(
                    title=title,
                    link=entry.get("link", ""),
                    source=name,
                    published=entry.get("published", entry.get("updated", "")),
                    summary=summary,
                    category=category,
                )
            )
    except Exception as e:  # مصدر واحد يفشل ما يوقف الباقي
        print(f"[!] فشل جلب {name}: {e}")
    return items


def fetch_github_trending_ai(max_repos: int = 5) -> list[NewsItem]:
    """أكثر مشاريع AI الجديدة نجومًا خلال آخر 7 أيام (GitHub Search API — مجاني)."""
    since = (dt.date.today() - dt.timedelta(days=7)).isoformat()
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"topic:ai created:>{since}",
        "sort": "stars",
        "order": "desc",
        "per_page": max_repos,
    }
    items: list[NewsItem] = []
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        r.raise_for_status()
        for repo in r.json().get("items", []):
            items.append(
                NewsItem(
                    title=f"{repo['full_name']} ⭐ {repo['stargazers_count']}",
                    link=repo["html_url"],
                    source="GitHub Trending",
                    summary=_clean(repo.get("description") or ""),
                    category="github",
                )
            )
    except Exception as e:
        print(f"[!] فشل جلب GitHub Trending: {e}")
    return items


def fetch_all(max_items: int, max_repos: int) -> dict[str, list[NewsItem]]:
    """يرجع الأخبار مصنفة: saudi / arabic / global / github

    يقرأ المصادر من ai_news_agent/sources.py (نفس كتالوج المراقبة اللحظية).
    """
    arabic_urls = {src.url for src in ARABIC_SOURCES}

    all_items: list[NewsItem] = []
    for src in sources_for(DEFAULT_REGIONS):
        is_arabic_general = src.url in arabic_urls
        for item in fetch_feed(src.name, src.url, arabic=is_arabic_general):
            # منطقة المصدر تحدد التصنيف، إلا لو الخبر نفسه ذكر السعودية
            if item.category != "saudi":
                item.category = src.region
            all_items.append(item)

    # إزالة التكرار حسب العنوان
    seen: set[str] = set()
    unique: list[NewsItem] = []
    for it in all_items:
        key = it.title.lower()[:80]
        if key and key not in seen:
            seen.add(key)
            unique.append(it)

    # ندمج المناطق في ثلاث سلال للنشرة اليومية
    buckets: dict[str, list[NewsItem]] = {"saudi": [], "arabic": [], "global": []}
    for it in unique:
        if it.category in ("saudi", "gulf"):
            buckets["saudi"].append(it)
        elif it.category == "arabic":
            buckets["arabic"].append(it)
        else:
            buckets["global"].append(it)

    return {
        "saudi": buckets["saudi"][:max_items],
        "arabic": buckets["arabic"][:max_items],
        "global": buckets["global"][:max_items],
        "github": fetch_github_trending_ai(max_repos),
    }

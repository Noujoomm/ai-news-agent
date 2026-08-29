# -*- coding: utf-8 -*-
"""🔴 المراقبة اللحظية — يتابع كل المصادر ويرسل أي خبر AI جديد فور نزوله.

الفكرة:
    كل X ثانية → يفحص كل المصادر بالتوازي → يقارن مع ذاكرة الأخبار المرسلة
    → أي خبر جديد يرسله لك على تليجرام فورًا كرسالة مستقلة.

التشغيل:  python watch.py
"""
from __future__ import annotations

import concurrent.futures as futures
import datetime as dt
import time

import feedparser

from . import config
from . import viral
from .content import pick_hook
from .filters import (
    clean,
    is_ai_related,
    is_noise,
    normalize_link,
    normalize_title,
    strip_source_suffix,
)
from .fetchers import HEADERS, NewsItem
from .sources import DEFAULT_REGIONS, Source, sources_for
from .store import SeenStore
from .telegram_bot import _esc, send_message

UTC = dt.timezone.utc


# ---------------------------------------------------------------------------
# جلب مصدر واحد
# ---------------------------------------------------------------------------
def _entry_time(entry) -> dt.datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return dt.datetime(*parsed[:6], tzinfo=UTC)
            except Exception:
                continue
    return None


def _publisher(entry, fallback: str) -> str:
    """اسم الناشر الحقيقي — Google News يحطه داخل الخبر نفسه."""
    src = entry.get("source")
    if isinstance(src, dict) and src.get("title"):
        return clean(src["title"])
    return fallback


def poll_source(source: Source, max_age_hours: int) -> list[NewsItem]:
    """يجيب أخبار مصدر واحد ويرجع فقط الجديد زمنيًا. أي فشل ما يوقف الباقي."""
    items: list[NewsItem] = []
    try:
        parsed = feedparser.parse(source.url, request_headers=HEADERS)
    except Exception as e:
        print(f"   [!] {source.name}: {e}")
        return items

    cutoff = dt.datetime.now(UTC) - dt.timedelta(hours=max_age_hours)

    for entry in parsed.entries[:60]:
        published = _entry_time(entry)
        # لو ما فيه تاريخ نقبله (الذاكرة بتمنع التكرار على أي حال)
        if published and published < cutoff:
            continue

        raw_title = clean(entry.get("title", ""))
        if not raw_title:
            continue
        title, gn_publisher = strip_source_suffix(raw_title)
        summary = clean(entry.get("summary", entry.get("description", "")))[:400]

        if config.WATCH_ONLY_AI and not is_ai_related(title, summary):
            continue

        if config.WATCH_FILTER_NOISE and is_noise(f"{title} {summary}", config.WATCH_BLOCK_KEYWORDS):
            continue

        if viral.score(title, summary, source.name) < config.WATCH_MIN_SCORE:
            continue

        publisher = gn_publisher or _publisher(entry, source.name)
        if publisher.lower() in config.WATCH_BLOCK_SOURCES:
            continue

        items.append(
            NewsItem(
                title=title,
                link=entry.get("link", ""),
                source=publisher,
                published=published.isoformat() if published else "",
                summary=summary,
                category=source.region,
                score=viral.score(title, summary, f"{publisher} {source.name}"),
            )
        )
    return items


def poll_all(sources: list[Source], max_age_hours: int, workers: int) -> list[NewsItem]:
    """يفحص كل المصادر بالتوازي."""
    collected: list[NewsItem] = []
    with futures.ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(poll_source, s, max_age_hours): s for s in sources}
        for job in futures.as_completed(jobs):
            try:
                collected.extend(job.result())
            except Exception as e:
                print(f"   [!] {jobs[job].name}: {e}")
    return collected


# ---------------------------------------------------------------------------
# مفاتيح الذاكرة + الترتيب
# ---------------------------------------------------------------------------
def item_keys(item: NewsItem, dedupe_titles: bool) -> list[str]:
    keys = []
    link = normalize_link(item.link)
    if link:
        keys.append(f"link:{link}")
    if dedupe_titles:
        title = normalize_title(item.title)
        if title:
            keys.append(f"title:{title}")
    return keys or [f"raw:{item.title}"]


def _sort_key(item: NewsItem) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(item.published)
    except Exception:
        return dt.datetime.min.replace(tzinfo=UTC)


def select_new(items: list[NewsItem], seen: SeenStore, dedupe_titles: bool) -> list[NewsItem]:
    """يرجع الأخبار الجديدة فقط — ويشيل التكرار داخل نفس الجولة."""
    fresh: list[NewsItem] = []
    batch_keys: set[str] = set()

    # الأقوى للمحتوى أولاً — لو انضرب سقف الجولة، الأخبار الحلوة ما تضيع
    ordered = sorted(items, key=lambda it: (it.score, _sort_key(it)), reverse=True)

    for item in ordered:
        keys = item_keys(item, dedupe_titles)
        if any(seen.has(k) or k in batch_keys for k in keys):
            continue
        batch_keys.update(keys)
        fresh.append(item)
    return fresh


# ---------------------------------------------------------------------------
# صياغة رسالة الخبر الواحد
# ---------------------------------------------------------------------------
REGION_LABELS_FALLBACK = "🌍 عالمي"


def _region_label(region: str) -> str:
    from .sources import REGION_LABELS

    return REGION_LABELS.get(region, REGION_LABELS_FALLBACK)


def _relative_time(published: str) -> str:
    try:
        when = dt.datetime.fromisoformat(published)
    except Exception:
        return "الآن"
    minutes = int((dt.datetime.now(UTC) - when).total_seconds() // 60)
    if minutes < 1:
        return "الآن"
    if minutes < 60:
        return f"قبل {minutes} دقيقة"
    hours = minutes // 60
    if hours < 24:
        return f"قبل {hours} ساعة"
    return f"قبل {hours // 24} يوم"


def format_alert(item: NewsItem) -> str:
    tag = viral.badge(item.score)
    header = tag if tag else f"🔴 <b>خبر AI جديد</b>"

    lines = [
        f"{header} · {_region_label(item.category)}",
        "",
        f"<b>{_esc(item.title)}</b>",
    ]
    if item.summary:
        lines += ["", f"📝 {_esc(item.summary[:300])}"]

    lines += ["", f"📡 {_esc(item.source)} · ⏱ {_relative_time(item.published)}"]
    if item.link:
        lines.append(f"🔗 {item.link}")

    # الأخبار القوية تاخذ هوك أداة/إطلاق، الباقي هوك عام
    if config.WATCH_INCLUDE_HOOK and viral.is_content_worthy(item.score):
        hook = pick_hook(is_tool_news=item.category == "tools" or item.score >= viral.TIER_FIRE)
        lines += ["", f"🪝 <i>هوك جاهز:</i> {_esc(hook)}"]

    return "\n".join(lines)


def format_overflow(items: list[NewsItem]) -> str:
    lines = [f"📥 <b>+{len(items)} خبر إضافي في هالجولة</b>", ""]
    for item in items[:25]:
        lines.append(f"• {_esc(item.title[:110])}\n  🔗 {item.link}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# جولة واحدة
# ---------------------------------------------------------------------------
def run_cycle(
    sources: list[Source],
    seen: SeenStore,
    first_run: bool = False,
    dry_run: bool = False,
) -> int:
    stamp = dt.datetime.now().strftime("%H:%M:%S")
    items = poll_all(sources, config.WATCH_MAX_AGE_HOURS, config.WATCH_WORKERS)
    fresh = select_new(items, seen, config.WATCH_DEDUPE_TITLES)

    if first_run and config.WATCH_SEED_ON_FIRST_RUN:
        for item in fresh:
            seen.add_many(item_keys(item, config.WATCH_DEDUPE_TITLES))
        seen.save()
        print(f"[{stamp}] 🌱 أول تشغيل — سجّلنا {len(fresh)} خبر موجود كـ«مقروء» بدون إرسال")
        return 0

    if not fresh:
        print(f"[{stamp}] لا جديد ({len(items)} خبر مفحوص)")
        return 0

    to_send = fresh[: config.WATCH_MAX_PER_CYCLE]
    overflow = fresh[config.WATCH_MAX_PER_CYCLE :]

    if dry_run:
        print(f"[{stamp}] 🧪 تجربة — {len(fresh)} خبر جديد (ما بنرسل شي):\n")
        for item in fresh:
            flame = "🔥" if viral.is_content_worthy(item.score) else "  "
            print(f"   {flame} [{item.score:>2}] {_region_label(item.category)}  {item.title[:85]}")
            print(f"      📡 {item.source} · {_relative_time(item.published)}  →  {item.link}\n")
        return len(fresh)

    hot = sum(1 for it in fresh if viral.is_content_worthy(it.score))
    print(f"[{stamp}] 🚨 {len(fresh)} خبر جديد ({hot} منها 🔥 يصلح محتوى) — جاري الإرسال...")

    sent = 0
    for item in to_send:
        if send_message(format_alert(item)):
            seen.add_many(item_keys(item, config.WATCH_DEDUPE_TITLES))
            sent += 1
            flame = "🔥" if viral.is_content_worthy(item.score) else "  "
            print(f"   ✅ {flame} [{item.score:>2}] {item.title[:65]}  ({item.source})")
        else:
            print(f"   ❌ فشل الإرسال: {item.title[:60]}")
        seen.save()
        time.sleep(config.WATCH_SEND_DELAY)

    if overflow:
        if send_message(format_overflow(overflow)):
            for item in overflow:
                seen.add_many(item_keys(item, config.WATCH_DEDUPE_TITLES))
            print(f"   📥 أرسلنا ملخّص لـ {len(overflow)} خبر إضافي")
        seen.save()

    return sent


# ---------------------------------------------------------------------------
# الحلقة الرئيسية
# ---------------------------------------------------------------------------
def run_watch(once: bool = False, dry_run: bool = False) -> None:
    regions = config.WATCH_REGIONS or DEFAULT_REGIONS
    sources = sources_for(regions)
    seen = SeenStore(config.WATCH_STATE_FILE, config.WATCH_STATE_TTL_DAYS)

    print("═══════════════════════════════════════════")
    print("🔴 المراقبة اللحظية لأخبار الذكاء الاصطناعي")
    print("═══════════════════════════════════════════")
    print(f"📡 المصادر      : {len(sources)}")
    print(f"🌍 المناطق      : {', '.join(regions)}")
    print(f"⏱  كل           : {config.WATCH_INTERVAL_SECONDS} ثانية")
    print(f"🕐 أقصى عمر خبر : {config.WATCH_MAX_AGE_HOURS} ساعة")
    print(f"🧠 الذاكرة      : {config.WATCH_STATE_FILE} ({len(seen)} خبر محفوظ)")
    if dry_run:
        print("🧪 وضع التجربة   : ما راح نرسل أي شي لتليجرام")
    print("   أوقفه بـ Ctrl+C")
    print("═══════════════════════════════════════════\n")

    first_run = seen.is_empty and not dry_run
    if first_run and config.WATCH_SEED_ON_FIRST_RUN:
        send_message(
            "🟢 <b>المراقبة اللحظية شغّالة</b>\n\n"
            f"📡 أتابع لك {len(sources)} مصدر AI حول العالم "
            "(أمريكا · الصين · أوروبا · آسيا · الخليج · السعودية)\n"
            f"⏱ أفحصها كل {config.WATCH_INTERVAL_SECONDS // 60} دقائق\n\n"
            "أي خبر جديد بيوصلك هنا فورًا 🔴"
        )

    while True:
        try:
            run_cycle(sources, seen, first_run=first_run, dry_run=dry_run)
            first_run = False
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[!] خطأ في الجولة (بنكمل عادي): {e}")

        if once:
            return
        time.sleep(config.WATCH_INTERVAL_SECONDS)

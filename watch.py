# -*- coding: utf-8 -*-
"""🔴 المراقبة اللحظية لأخبار الذكاء الاصطناعي.

يتابع عشرات المصادر حول العالم (أمريكا · الصين · أوروبا · آسيا · الخليج)
وأي خبر AI جديد يوصلك على تليجرام فورًا.

    python watch.py              # مراقبة مستمرة (هذا اللي تبيه)
    python watch.py --once       # جولة وحدة وبس
    python watch.py --dry-run    # تجربة: يطبع الأخبار بالترمنال بدون إرسال
    python watch.py --sources    # يعرض قائمة المصادر المتابَعة

كل الإعدادات في .env (المتغيرات اللي تبدأ بـ WATCH_).
"""
import argparse

from ai_news_agent.watcher import run_watch


def main() -> None:
    parser = argparse.ArgumentParser(description="مراقبة لحظية لأخبار الذكاء الاصطناعي")
    parser.add_argument("--once", action="store_true", help="جولة واحدة ثم يخرج")
    parser.add_argument("--dry-run", action="store_true", help="بدون إرسال — طباعة فقط")
    parser.add_argument("--sources", action="store_true", help="عرض المصادر المتابَعة")
    args = parser.parse_args()

    if args.sources:
        from ai_news_agent import config
        from ai_news_agent.sources import DEFAULT_REGIONS, sources_for

        sources = sources_for(config.WATCH_REGIONS or DEFAULT_REGIONS)
        print(f"📡 {len(sources)} مصدر متابَع:\n")
        for src in sources:
            print(f"  {src.label:<12} {src.name}")
        return

    run_watch(once=args.once, dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف المراقبة.")

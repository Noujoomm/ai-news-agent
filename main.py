# -*- coding: utf-8 -*-
"""تشغيل النشرة مرة واحدة الآن:
    python main.py

للجدولة اليومية التلقائية:
    python scheduler.py
"""
from ai_news_agent import config
from ai_news_agent.content import build_script, pick_content_ideas, pick_top_story
from ai_news_agent.fetchers import fetch_all
from ai_news_agent.telegram_bot import build_message, send_message


def run_once() -> None:
    print("⏳ جاري جلب أخبار الذكاء الاصطناعي...")
    buckets = fetch_all(config.MAX_NEWS_ITEMS, config.MAX_GITHUB_REPOS)

    total = sum(len(v) for v in buckets.values())
    print(f"✅ تم جلب {total} خبر/مشروع")

    story = pick_top_story(buckets)
    all_titles = [it.title for v in buckets.values() for it in v]
    script = build_script(story, all_titles) if story else {"hook": "", "body": "", "cta": ""}
    ideas = pick_content_ideas(3)

    message = build_message(buckets, story, script, ideas)

    print("📨 جاري الإرسال إلى تليجرام...")
    if send_message(message):
        print("✅ تم إرسال النشرة بنجاح!")
    else:
        print("❌ ما قدرنا نرسل — راجع الإعدادات. هذي معاينة الرسالة:\n")
        print(message[:2000])


if __name__ == "__main__":
    run_once()

# -*- coding: utf-8 -*-
"""إعدادات المشروع — كل القيم تُقرأ من ملف .env"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== Telegram =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ===== LLM (اختياري — Ollama محلي) =====
# لو USE_LLM=true بيستخدم Ollama لكتابة سكربت الريل بالعربي بشكل أذكى.
# لو false بيستخدم قوالب جاهزة بدون أي LLM (يشتغل مجانًا 100%).
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:14b")

# ===== الجدولة =====
# وقت الإرسال اليومي بتوقيتك المحلي (صيغة 24 ساعة)
DAILY_SEND_TIME = os.getenv("DAILY_SEND_TIME", "08:00")

# ===== المحتوى =====
# كم خبر بحد أقصى في الرسالة
MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", "8"))
# كم مشروع GitHub trending
MAX_GITHUB_REPOS = int(os.getenv("MAX_GITHUB_REPOS", "5"))

# ===== هوية البراند (تظهر في اقتراحات المحتوى) =====
BRAND_NAME = os.getenv("BRAND_NAME", "مازن — متخصص AI")
BRAND_CTA = os.getenv(
    "BRAND_CTA",
    "عندك فكرة تطبيق أو مشروع AI؟ تابعني وراسلني وأنا أحولها لواقع 🚀",
)


# ===========================================================================
# 🔴 وضع المراقبة اللحظية (watch.py)
# أي خبر AI جديد من أي مصدر في العالم → يوصلك فورًا
# ===========================================================================

# كل كم ثانية يفحص كل المصادر (300 = كل ٥ دقائق)
WATCH_INTERVAL_SECONDS = int(os.getenv("WATCH_INTERVAL_SECONDS", "300"))

# أقصى عمر للخبر عشان يُرسل — أي خبر أقدم من كذا ساعة يُتجاهل
WATCH_MAX_AGE_HOURS = int(os.getenv("WATCH_MAX_AGE_HOURS", "24"))

# أقصى عدد رسائل في الجولة الوحدة (حماية من الإغراق وحدود تليجرام)
WATCH_MAX_PER_CYCLE = int(os.getenv("WATCH_MAX_PER_CYCLE", "20"))

# ثواني الانتظار بين رسالة ورسالة (حدود تليجرام)
WATCH_SEND_DELAY = float(os.getenv("WATCH_SEND_DELAY", "1.5"))

# أول تشغيل: نعلّم الأخبار الموجودة كـ"مقروءة" بدل ما نرسل مئات الأخبار القديمة
WATCH_SEED_ON_FIRST_RUN = os.getenv("WATCH_SEED_ON_FIRST_RUN", "true").lower() == "true"

# يرسل هوك جاهز مع كل خبر (لمحتوى الريلز)
WATCH_INCLUDE_HOOK = os.getenv("WATCH_INCLUDE_HOOK", "true").lower() == "true"

# يمنع نفس الخبر لو جانا من مصدرين مختلفين
WATCH_DEDUPE_TITLES = os.getenv("WATCH_DEDUPE_TITLES", "true").lower() == "true"

# يرسل فقط أخبار الذكاء الاصطناعي (لو false يرسل كل شي من المصادر)
WATCH_ONLY_AI = os.getenv("WATCH_ONLY_AI", "true").lower() == "true"

# المناطق المتابَعة — مفصولة بفواصل، أو "all" لكل شي (يشمل الأبحاث)
# المتاح: saudi,gulf,arabic,usa,china,asia,europe,community,research,global
WATCH_REGIONS = [r.strip() for r in os.getenv("WATCH_REGIONS", "").split(",") if r.strip()]

# ملف ذاكرة الأخبار المرسلة + كم يوم يحتفظ فيها
WATCH_STATE_FILE = os.getenv("WATCH_STATE_FILE", ".seen_news.json")
WATCH_STATE_TTL_DAYS = int(os.getenv("WATCH_STATE_TTL_DAYS", "7"))

# عدد الخيوط المتوازية لجلب المصادر
WATCH_WORKERS = int(os.getenv("WATCH_WORKERS", "12"))

# فلتر الضجيج: يستبعد أخبار تذكر AI بس ما لها علاقة (توقعات مباريات، مقالات أسهم...)
WATCH_FILTER_NOISE = os.getenv("WATCH_FILTER_NOISE", "true").lower() == "true"

# كلمات إضافية تبغى تحجبها — مفصولة بفواصل
WATCH_BLOCK_KEYWORDS = [k.strip() for k in os.getenv("WATCH_BLOCK_KEYWORDS", "").split(",") if k.strip()]

# مصادر (ناشرين) تبغى تحجبهم — مفصولة بفواصل، مثال: The Motley Fool,365Scores
WATCH_BLOCK_SOURCES = [s.strip().lower() for s in os.getenv("WATCH_BLOCK_SOURCES", "").split(",") if s.strip()]

# 🔥 أقل درجة "قابلية انتشار" عشان الخبر يوصلك (viral.py)
#   0  = كل أخبار الـ AI
#   3  = الأخبار اللي تصلح محتوى فقط (أدوات، إطلاقات، مجاني...)
#   6  = الأقوى فقط — أخبار تستاهل ريل
WATCH_MIN_SCORE = int(os.getenv("WATCH_MIN_SCORE", "0"))

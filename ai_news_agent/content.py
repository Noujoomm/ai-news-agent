# -*- coding: utf-8 -*-
"""تحويل الأخبار إلى محتوى جاهز للنشر:
- اختيار "خبر اليوم" (الأقوى للريل)
- سكربت TikTok/Reel كامل: هوك → محتوى → CTA
- أفكار محتوى إضافية + هاشتاقات
يشتغل بوضعين: قوالب جاهزة (بدون LLM) أو Ollama محلي لصياغة أذكى.
"""
from __future__ import annotations

import random

import requests

from . import config
from .fetchers import NewsItem

HOOKS = [
    "وقّف كل شي وشوف وش صار في عالم الذكاء الاصطناعي اليوم 👇",
    "لو تشتغل في التقنية ولا تعرف هالخبر… أنت متأخر سنة كاملة!",
    "خبر اليوم في الـ AI ممكن يغيّر شغلك بالكامل 🤯",
    "هذي التقنية الجديدة بتخلي نص شغلك يخلص لحاله…",
    "الكل يتكلم عن هالموديل الجديد… بس أنا بقولك الزبدة في ٦٠ ثانية",
    "السعودية والذكاء الاصطناعي… القصة أكبر مما تتخيل 🇸🇦",
]

HASHTAGS_AR = "#الذكاء_الاصطناعي #تقنية #الذكاء_الاصطناعي_بالعربي #تعلم_الذكاء_الاصطناعي #السعودية"
HASHTAGS_EN = "#AI #ArtificialIntelligence #TechNews #GenAI #MachineLearning"

CONTENT_IDEAS = [
    "قارن بين أقوى موديلين حاليًا في مهمة عملية (مثلاً: كتابة كود أو تلخيص) وورّي النتيجة على الشاشة",
    "اشرح خبر اليوم بأسلوب 'وش يعني لي أنا كشخص عادي؟' — الناس تحب التبسيط",
    "سوّي سلسلة 'جربت لكم' — تجرب أداة AI جديدة كل يوم وتعطي رأيك في ٦٠ ثانية",
    "خذ مشروع GitHub trending وورّي كيف تشغّله خطوة بخطوة في دقيقة",
    "اربط الخبر بخدماتك: 'هالموديل الجديد يقدر يسوي X… وأنا أقدر أبني لك تطبيق يستخدمه'",
    "رد على سؤال شائع من التعليقات بفيديو — يرفع التفاعل بشكل كبير",
    "قارن وضع الـ AI في السعودية مع أمريكا — المحتوى المحلي المقارن ينتشر بسرعة",
    "ورّي كواليس بناء مشروعك (الحجازي الآلي مثلاً) وكيف تستخدم أدوات اليوم فيه",
]


def pick_top_story(buckets: dict[str, list[NewsItem]]) -> NewsItem | None:
    """أولوية خبر اليوم: سعودي → عالمي كبير → عربي → GitHub"""
    for key in ("saudi", "global", "arabic", "github"):
        if buckets.get(key):
            return buckets[key][0]
    return None


# ---------------------------------------------------------------------------
# الوضع الأول: قوالب جاهزة (بدون أي LLM)
# ---------------------------------------------------------------------------
def build_script_template(story: NewsItem) -> dict[str, str]:
    hook = random.choice(HOOKS)
    body = (
        f"اليوم طلع خبر مهم من {story.source}:\n"
        f"«{story.title}»\n\n"
        f"باختصار: {story.summary[:220] if story.summary else 'تفاصيل الخبر في الرابط المرفق.'}\n\n"
        "ليش يهمك؟ لأن هالنوع من التطورات يعني أدوات أقوى وأرخص وأسرع، "
        "وكل ما فهمتها بدري كل ما سبقت غيرك في الشغل أو مشاريعك."
    )
    cta = config.BRAND_CTA
    return {"hook": hook, "body": body, "cta": cta}


# ---------------------------------------------------------------------------
# الوضع الثاني: Ollama محلي (اختياري)
# ---------------------------------------------------------------------------
def build_script_llm(story: NewsItem, all_titles: list[str]) -> dict[str, str] | None:
    prompt = f"""أنت كاتب محتوى تيك توك سعودي محترف متخصص في الذكاء الاصطناعي.
اكتب سكربت ريل مدته 45-60 ثانية باللهجة السعودية البيضاء عن هذا الخبر:

العنوان: {story.title}
الملخص: {story.summary}
المصدر: {story.source}

سياق إضافي (أخبار اليوم الأخرى): {"، ".join(all_titles[:5])}

أرجع الرد بصيغة JSON فقط بدون أي شرح:
{{"hook": "جملة افتتاحية قوية توقف المشاهد", "body": "نص السكربت كامل بالتفصيل، ماذا أقول بالضبط", "cta": "دعوة لاتخاذ إجراء تربط الخبر بخدماتي كمتخصص AI يبني تطبيقات ومشاريع"}}"""
    try:
        r = requests.post(
            f"{config.OLLAMA_URL}/api/generate",
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=180,
        )
        r.raise_for_status()
        import json

        data = json.loads(r.json().get("response", "{}"))
        if data.get("hook") and data.get("body"):
            data.setdefault("cta", config.BRAND_CTA)
            return data
    except Exception as e:
        print(f"[!] Ollama غير متاح، بنستخدم القوالب الجاهزة: {e}")
    return None


def build_script(story: NewsItem, all_titles: list[str]) -> dict[str, str]:
    if config.USE_LLM:
        result = build_script_llm(story, all_titles)
        if result:
            return result
    return build_script_template(story)


def pick_content_ideas(n: int = 3) -> list[str]:
    return random.sample(CONTENT_IDEAS, k=min(n, len(CONTENT_IDEAS)))

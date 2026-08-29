# -*- coding: utf-8 -*-
"""🔥 تقييم قابلية الخبر للانتشار على تيك توك.

الفكرة: مو كل خبر AI يصلح محتوى. الأخبار اللي تنتشر هي:
    ✅ أداة جديدة تحل مشكلة  ✅ إطلاق منتج (Gemini، Claude Code، ChatGPT)
    ✅ شي مجاني أو مفتوح المصدر  ✅ "صار تقدر تسوي كذا"
    ❌ أرباح وأسهم  ❌ قضايا وتنظيمات  ❌ تعيينات إدارية

كل خبر ياخذ درجة، والأخبار الأعلى درجة تُرسل أول وعليها علامة 🔥
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# إشارات إيجابية — كل مجموعة ونقاطها
# ---------------------------------------------------------------------------
_POSITIVE = [
    # إطلاق منتج — أقوى إشارة
    (3, r"\b(launch(es|ed|ing)?|introduc(es|ing)|unveil(s|ed)?|debuts?|releas(es|ed)|"
        r"rolls? out|now available|available now|goes live|ships?|out now)\b"),
    (3, r"(تطلق|أطلقت|يطلق|إطلاق|تكشف|كشفت|تعلن عن|أعلنت عن|متاح الآن|صار متاح|نزل)"),

    # مجاني / مفتوح المصدر — الناس تحب هذا جدًا
    (3, r"\b(free|open[- ]source|no cost|open weights?)\b"),
    (3, r"(مجان(ي|ًا|ا)|مفتوح المصدر|بدون اشتراك|ببلاش)"),

    # أداة / تطبيق / ميزة
    (2, r"\b(tool|app|feature|extension|plugin|assistant|agent|api|integration|update)\b"),
    (2, r"(أداة|تطبيق|ميزة|إضافة|مساعد|وكيل|تحديث)"),

    # أسماء منتجات ساخنة — الجمهور يعرفها ويبحث عنها
    (3, r"\b(claude code|claude|chatgpt|gpt-?5|gpt-?4|gemini|sora|veo|midjourney|cursor|"
        r"copilot|deepseek|qwen|grok|llama|perplexity|runway|elevenlabs|heygen|suno|"
        r"stable diffusion|notion ai|canva ai|figma ai|nano banana)\b"),

    # صياغة "صار تقدر" — أعلى تفاعل
    (2, r"\b(you can now|now you can|how to|hands[- ]on|i tried|we tried|tutorial|demo)\b"),
    (2, r"(صار تقدر|تقدر الحين|كيف تستخدم|جربت|شرح)"),

    # تفوّق ومقارنات
    (2, r"\b(beats?|outperforms?|faster than|better than|world'?s first|first ever|"
        r"state[- ]of[- ]the[- ]art|breakthrough)\b"),
    (2, r"(يتفوق|تتفوق|الأول من نوعه|الأسرع|الأقوى|اختراق)"),

    # مثير للجدل / صادم — ينتشر بقوة
    (2, r"\b(shocking|insane|scary|banned|leaked|exposed|goes viral|deepfake)\b"),
    (2, r"(صادم|مرعب|مثير للجدل|تسريب|فضح|منع|حظر)"),
]

# ---------------------------------------------------------------------------
# إشارات سلبية — أخبار مالية/قانونية/إدارية ما تصلح ريل
# ---------------------------------------------------------------------------
_NEGATIVE = [
    (3, r"\b(earnings|quarterly|q[1-4] results?|revenue|profit|stock|shares|"
        r"market cap|ipo|dividend|analyst|investors?|valuation)\b"),
    (3, r"(أرباح|إيرادات|أسهم|توزيعات|الاكتتاب|القيمة السوقية|المحللين|تقييم الشركة)"),

    (2, r"\b(lawsuit|sues?|sued|court|settlement|antitrust|regulation|regulatory|"
        r"compliance|policy|senate|congress|parliament)\b"),
    (2, r"(دعوى|قضائي|محكمة|تسوية|تنظيمات|لائحة|قانون|البرلمان|مجلس الشيوخ)"),

    (2, r"\b(appoints?|names? .{0,20}(ceo|cto|cfo)|hires?|resigns?|steps down|"
        r"layoffs?|restructuring|partnership agreement|memorandum)\b"),
    (2, r"(تعيين|يستقيل|استقالة|تسريح|إعادة هيكلة|مذكرة تفاهم|اتفاقية شراكة)"),

    (2, r"\b(conference|summit|webinar|award|finalist|press release|report finds|survey)\b"),
    (2, r"(مؤتمر|قمة|ندوة|جائزة|بيان صحفي|تقرير يكشف|استطلاع)"),
]

_POSITIVE_RE = [(pts, re.compile(pat, re.IGNORECASE)) for pts, pat in _POSITIVE]
_NEGATIVE_RE = [(pts, re.compile(pat, re.IGNORECASE)) for pts, pat in _NEGATIVE]

# مصادر الأدوات — أي شي منها يبدأ بنقطة إضافية
_TOOL_SOURCES = ("product hunt", "producthunt", "show hn", "tldr", "github")


def score(title: str, summary: str = "", source: str = "") -> int:
    """درجة قابلية الانتشار. أعلى = محتوى تيك توك أقوى."""
    blob = f"{title} {summary}"
    total = 0

    for points, pattern in _POSITIVE_RE:
        if pattern.search(blob):
            total += points
    for points, pattern in _NEGATIVE_RE:
        if pattern.search(blob):
            total -= points

    if any(s in (source or "").lower() for s in _TOOL_SOURCES):
        total += 2

    return total


# ---------------------------------------------------------------------------
# التصنيف والعرض
# ---------------------------------------------------------------------------
TIER_FIRE = 6      # 🔥🔥 صوّر ريل الحين
TIER_GOOD = 3      # 🔥 يصلح محتوى


def badge(value: int) -> str:
    if value >= TIER_FIRE:
        return "🔥🔥 <b>محتوى قوي — صوّر ريل</b>"
    if value >= TIER_GOOD:
        return "🔥 <b>يصلح محتوى</b>"
    return ""


def is_content_worthy(value: int) -> bool:
    return value >= TIER_GOOD

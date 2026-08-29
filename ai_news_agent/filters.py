# -*- coding: utf-8 -*-
"""فلترة وتنظيف الأخبار:
- هل الخبر يخص الذكاء الاصطناعي فعلاً؟
- تنظيف HTML وتوحيد العناوين لكشف التكرار بين المصادر
"""
from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# كلمات الذكاء الاصطناعي — إنجليزي بحدود كلمات (\b) عشان "ai" ما تطابق "said"
# ---------------------------------------------------------------------------
_EN_TERMS = [
    r"a\.?i\.?",
    r"artificial intelligence",
    r"machine learning",
    r"deep learning",
    r"neural networks?",
    r"large language models?",
    r"llms?",
    r"gpt-?\d*",
    r"chatgpt",
    r"openai",
    r"anthropic",
    r"claude",
    r"gemini",
    r"llama",
    r"mistral",
    r"qwen",
    r"deepseek",
    r"grok",
    r"copilot",
    r"midjourney",
    r"stable diffusion",
    r"hugging ?face",
    r"nvidia",
    r"transformers?",
    r"diffusion models?",
    r"multimodal",
    r"agentic",
    r"ai agents?",
    r"chatbots?",
    r"humanoids?",
    r"robotics?",
    r"self-?driving",
    r"autonomous vehicles?",
    r"generative",
    r"genai",
    r"agi",
    r"inference",
    r"fine-?tun\w*",
    r"benchmarks?",
    r"data ?centers?",
    r"gpus?",
    r"tpus?",
    r"prompt engineering",
    r"computer vision",
    r"speech recognition",
]

# عربي — من غير حدود كلمات (اللغة العربية ما تحتاجها)
_AR_TERMS = [
    "ذكاء اصطناعي",
    "الذكاء الاصطناعي",
    "ذكاءً اصطناعي",
    "التعلم الآلي",
    "تعلم الآلة",
    "التعلم العميق",
    "الشبكات العصبية",
    "نموذج لغوي",
    "النماذج اللغوية",
    "نماذج توليدية",
    "الذكاء التوليدي",
    "روبوت",
    "الروبوتات",
    "وكيل ذكي",
    "وكلاء أذكياء",
    "شات جي بي تي",
    "أوبن إيه آي",
    "جيميناي",
    "خوارزمي",
    "تعلّم آلي",
    "أشباه الموصلات",
    "معالجات رسومية",
]

_EN_RE = re.compile(r"\b(?:" + "|".join(_EN_TERMS) + r")\b", re.IGNORECASE)
_AR_RE = re.compile("|".join(re.escape(t) for t in _AR_TERMS))

_TAG_RE = re.compile(r"<[^>]+>")
_PUNCT_RE = re.compile(r"[^\w؀-ۿ ]+", re.UNICODE)

# لواحق Google News في العنوان: "العنوان - اسم الموقع"
_GN_SUFFIX_RE = re.compile(r"\s+[-–—]\s+[^-–—]{2,40}$")


def clean(text: str) -> str:
    """يشيل وسوم HTML ويوحّد المسافات."""
    import html

    text = _TAG_RE.sub(" ", text or "")
    text = html.unescape(text)
    return " ".join(text.split())


def is_ai_related(*texts: str) -> bool:
    """هل هذا الخبر عن الذكاء الاصطناعي؟"""
    blob = " ".join(t for t in texts if t)
    if not blob:
        return False
    return bool(_EN_RE.search(blob) or _AR_RE.search(blob))


def strip_source_suffix(title: str) -> tuple[str, str]:
    """يفصل عنوان Google News عن اسم الناشر: ('العنوان', 'الناشر')."""
    match = _GN_SUFFIX_RE.search(title or "")
    if match:
        publisher = match.group(0).lstrip(" -–—").strip()
        return title[: match.start()].strip(), publisher
    return (title or "").strip(), ""


def normalize_title(title: str) -> str:
    """مفتاح موحّد للعنوان — يستخدم لكشف نفس الخبر لو جانا من مصادر مختلفة."""
    title, _ = strip_source_suffix(title or "")
    title = unicodedata.normalize("NFKD", title).lower()
    title = _PUNCT_RE.sub(" ", title)
    words = [w for w in title.split() if len(w) > 2]
    return " ".join(words)[:90]


def normalize_link(link: str) -> str:
    """يشيل باراميترات التتبّع من الرابط عشان الروابط المكررة تنكشف."""
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    if not link:
        return ""
    try:
        parts = urlsplit(link)
        query = [
            (k, v)
            for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith(("utm_", "fbclid", "gclid", "ref"))
        ]
        return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(query), ""))
    except Exception:
        return link


# ---------------------------------------------------------------------------
# فلتر الضجيج — أخبار تذكر "الذكاء الاصطناعي" بس ما لها علاقة فعلية
# (توقعات مباريات، مقالات الأسهم التسويقية، الأبراج...)
# تقدر تزيد كلماتك في .env عبر WATCH_BLOCK_KEYWORDS
# ---------------------------------------------------------------------------
_NOISE_PATTERNS = [
    r"توقعات .{0,30}مباراة",
    r"مباراة .{0,40}(اليوم|ضد|أمام)",
    r"تشكيل(ة)? .{0,30}(المباراة|الفريق)",
    r"\bhoroscope\b",
    r"\bتوقعات الأبراج\b",
    r"\blottery\b",
    r"should you buy .{0,40}stock",
    r"\d+ (top|best) .{0,30}stocks? to buy",
    r"prediction: .{0,40}(stock|shares)",
    r"\bcoupon\b|\bdiscount code\b|\bdeal of the day\b",
    r"\bكوبون\b|\bخصم\b",
]

_NOISE_RE = re.compile("|".join(_NOISE_PATTERNS), re.IGNORECASE)


def is_noise(text: str, extra_keywords: list[str] | None = None) -> bool:
    """هل هذا الخبر ضجيج ما يستاهل تنبيه؟"""
    if not text:
        return False
    if _NOISE_RE.search(text):
        return True
    if extra_keywords:
        low = text.lower()
        return any(k.lower() in low for k in extra_keywords if k)
    return False

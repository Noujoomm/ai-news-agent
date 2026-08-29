# -*- coding: utf-8 -*-
"""كتالوج مصادر الأخبار — كل المصادر مجانية (RSS) بدون مفاتيح مدفوعة.

كل مصدر له:
    name   : اسم المصدر كما يظهر في الرسالة
    url    : رابط الـ RSS
    region : المنطقة (تستخدم للتصنيف والفلترة عبر WATCH_REGIONS في .env)

المناطق المتاحة:
    saudi | gulf | arabic | usa | china | asia | europe | community | research

تبغى تزيد مصدر؟ ضيفه في القائمة المناسبة تحت — وبس.
"""
from __future__ import annotations

from dataclasses import dataclass

# علم/إيموجي لكل منطقة (يظهر في رسالة التنبيه)
REGION_LABELS = {
    "saudi": "🇸🇦 السعودية",
    "gulf": "🌴 الخليج",
    "arabic": "📰 عربي",
    "usa": "🇺🇸 أمريكا",
    "china": "🇨🇳 الصين",
    "asia": "🌏 آسيا",
    "europe": "🇪🇺 أوروبا",
    "community": "💬 مجتمع",
    "research": "🔬 أبحاث",
    "global": "🌍 عالمي",
}

# المناطق المفعّلة افتراضيًا (research مطفّية لأنها مئات الأوراق البحثية يوميًا)
DEFAULT_REGIONS = ["saudi", "gulf", "arabic", "usa", "china", "asia", "europe", "community", "global"]


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    region: str = "global"

    @property
    def label(self) -> str:
        return REGION_LABELS.get(self.region, REGION_LABELS["global"])


# ---------------------------------------------------------------------------
# 🇺🇸 أمريكا / شركات الـ AI الكبرى + مواقع تقنية عالمية
# ---------------------------------------------------------------------------
USA_SOURCES = [
    Source("OpenAI", "https://openai.com/news/rss.xml", "usa"),
    Source("Google AI Blog", "https://blog.google/technology/ai/rss/", "usa"),
    Source("Google DeepMind", "https://deepmind.google/blog/rss.xml", "usa"),
    Source("Hugging Face", "https://huggingface.co/blog/feed.xml", "usa"),
    Source("Microsoft AI", "https://blogs.microsoft.com/feed/", "usa"),
    Source("Meta Engineering", "https://engineering.fb.com/feed/", "usa"),
    Source("AWS Machine Learning", "https://aws.amazon.com/blogs/machine-learning/feed/", "usa"),
    Source("NVIDIA", "https://blogs.nvidia.com/feed/", "usa"),
    Source("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "usa"),
    Source("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "usa"),
    Source("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "usa"),
    Source("WIRED AI", "https://www.wired.com/feed/tag/ai/latest/rss", "usa"),
    Source("The Register AI", "https://www.theregister.com/software/ai_ml/headlines.atom", "usa"),
    Source("ZDNet AI", "https://www.zdnet.com/topic/artificial-intelligence/rss.xml", "usa"),
    Source("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed", "usa"),
    Source("IEEE Spectrum AI", "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss", "usa"),
    Source("MarkTechPost", "https://www.marktechpost.com/feed/", "usa"),
    Source("AI News", "https://www.artificialintelligence-news.com/feed/", "usa"),
    Source("The Next Web", "https://thenextweb.com/feed", "usa"),
    Source("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "usa"),
    Source("Engadget", "https://www.engadget.com/rss.xml", "usa"),
]

# ---------------------------------------------------------------------------
# 🇨🇳 الصين
# ---------------------------------------------------------------------------
CHINA_SOURCES = [
    Source("TechNode", "https://technode.com/feed/", "china"),
    Source("SCMP Tech", "https://www.scmp.com/rss/36/feed", "china"),
    Source("Synced Review", "https://syncedreview.com/feed/", "china"),
    Source("Pandaily", "https://pandaily.com/feed/", "china"),
]

# ---------------------------------------------------------------------------
# 📰 عربي / سعودي
# ---------------------------------------------------------------------------
ARABIC_SOURCES = [
    Source("البوابة العربية للأخبار التقنية", "https://aitnews.com/feed/", "arabic"),
    Source("عالم التقنية", "https://www.tech-wd.com/wd/feed/", "arabic"),
]

# ---------------------------------------------------------------------------
# 💬 مجتمعات (نقاشات المطورين — غالبًا تسبق الأخبار الرسمية)
# ---------------------------------------------------------------------------
COMMUNITY_SOURCES = [
    Source("Hacker News", "https://hnrss.org/newest?q=AI+OR+LLM+OR+OpenAI+OR+Anthropic&points=50", "community"),
    Source("r/LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/new/.rss", "community"),
    Source("r/artificial", "https://www.reddit.com/r/artificial/new/.rss", "community"),
]

# ---------------------------------------------------------------------------
# 🔬 أبحاث (مطفّية افتراضيًا — حجمها كبير جدًا)
# ---------------------------------------------------------------------------
RESEARCH_SOURCES = [
    Source("arXiv cs.AI", "http://export.arxiv.org/rss/cs.AI", "research"),
]

# ---------------------------------------------------------------------------
# 🌐 Google News — الشبكة اللي تصطاد أي خبر AI من أي مكان في العالم
# هذي أهم قائمة: تغطي آلاف المواقع (الصين، أمريكا، أوروبا، آسيا، العرب)
# ---------------------------------------------------------------------------
def _gn(query: str, lang: str = "en-US", country: str = "US") -> str:
    from urllib.parse import quote_plus

    ceid = f"{country}:{lang.split('-')[0]}"
    return (
        f"https://news.google.com/rss/search?q={quote_plus(query)}"
        f"&hl={lang}&gl={country}&ceid={ceid}"
    )


GOOGLE_NEWS_SOURCES = [
    # عالمي شامل — أي خبر AI من أي مصدر
    Source("Google News · AI", _gn("artificial intelligence when:1d"), "global"),
    Source("Google News · GenAI", _gn("generative AI OR LLM OR AI model when:1d"), "global"),
    # أمريكا / شركات
    Source("Google News · OpenAI", _gn("OpenAI when:1d"), "usa"),
    Source("Google News · Anthropic", _gn("Anthropic Claude when:2d"), "usa"),
    Source("Google News · Meta AI", _gn("Meta AI OR Llama model when:2d"), "usa"),
    Source("Google News · Mistral", _gn("Mistral AI when:2d"), "europe"),
    Source("Google News · NVIDIA", _gn("Nvidia AI chips when:1d"), "usa"),
    # الصين
    Source("Google News · الصين AI", _gn("China AI artificial intelligence when:1d"), "china"),
    Source("Google News · موديلات صينية", _gn("DeepSeek OR Qwen OR Alibaba AI OR Baidu Ernie when:2d"), "china"),
    # آسيا / أوروبا
    Source("Google News · آسيا AI", _gn("Japan OR South Korea OR India AI when:2d"), "asia"),
    Source("Google News · أوروبا AI", _gn("Europe AI regulation OR European AI startup when:2d"), "europe"),
    # عربي / سعودي / خليجي
    Source("Google News · الذكاء الاصطناعي", _gn("الذكاء الاصطناعي when:1d", "ar", "SA"), "arabic"),
    Source("Google News · السعودية AI", _gn("السعودية الذكاء الاصطناعي", "ar", "SA"), "saudi"),
    Source("Google News · سدايا وهيوماين", _gn("سدايا OR هيوماين OR نيوم الذكاء الاصطناعي", "ar", "SA"), "saudi"),
    Source("Google News · الخليج AI", _gn("الإمارات OR قطر OR الكويت الذكاء الاصطناعي", "ar", "AE"), "gulf"),
]


# ---------------------------------------------------------------------------
ALL_SOURCES: list[Source] = (
    USA_SOURCES
    + CHINA_SOURCES
    + ARABIC_SOURCES
    + COMMUNITY_SOURCES
    + RESEARCH_SOURCES
    + GOOGLE_NEWS_SOURCES
)


def sources_for(regions: list[str] | None = None) -> list[Source]:
    """يرجع المصادر المفعّلة حسب المناطق المطلوبة."""
    if not regions or "all" in regions:
        return [s for s in ALL_SOURCES if s.region != "research"] if not regions else list(ALL_SOURCES)
    allowed = set(regions)
    return [s for s in ALL_SOURCES if s.region in allowed]

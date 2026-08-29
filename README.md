# 🤖 AI News Agent — مراقبة لحظية لأخبار الذكاء الاصطناعي

وكيل Python يتابع **٤٥ مصدر AI حول العالم** (🇺🇸 أمريكا · 🇨🇳 الصين · 🇪🇺 أوروبا · 🌏 آسيا · 🇸🇦 السعودية · 🌴 الخليج) وأي خبر جديد يوصلك على تليجرام **فورًا**.

مجاني ١٠٠٪ — كل المصادر RSS و GitHub API بدون أي مفاتيح مدفوعة.

## وضعان للتشغيل

| الوضع | الملف | وش يسوي |
|---|---|---|
| 🔴 **مراقبة لحظية** | `watch.py` | يفحص المصادر كل ٥ دقائق، وأي خبر جديد يرسله لحاله فورًا |
| 📰 **نشرة يومية** | `main.py` | تقرير يومي كامل + سكربت ريل جاهز + أفكار محتوى + هاشتاقات |

---

## ⚡ التشغيل السريع

```bash
pip install -r requirements.txt
cp .env.example .env          # وعبّي التوكن ورقم الشات
python watch.py               # 🔴 المراقبة اللحظية
```

### إنشاء بوت تليجرام
1. كلّم `@BotFather` وأرسل `/newbot` → بيعطيك **TOKEN**
2. كلّم بوتك الجديد وأرسل له أي رسالة
3. افتح `https://api.telegram.org/bot<TOKEN>/getUpdates` وخذ `"chat":{"id": ...}` → هذا **CHAT_ID**

### أوامر مفيدة
```bash
python watch.py --dry-run     # تجربة: يطبع الأخبار بالترمنال بدون إرسال
python watch.py --once        # جولة وحدة وبس
python watch.py --sources     # يعرض كل المصادر المتابَعة
python main.py                # النشرة اليومية الكاملة مرة وحدة
```

---

## ☁️ التشغيل ٢٤/٧ بدون لابتوب (GitHub Actions — مجاني)

البوت يشتغل على سيرفرات GitHub، فحتى لو جهازك مطفي يستمر يرسل لك.

### 1. ارفع المشروع على GitHub
```bash
git init && git add . && git commit -m "AI news agent"
gh repo create ai-news-agent --private --source=. --push
```

### 2. ضيف الأسرار
في صفحة الريبو → **Settings → Secrets and variables → Actions → New repository secret**:

| الاسم | القيمة |
|---|---|
| `TELEGRAM_BOT_TOKEN` | توكن البوت |
| `TELEGRAM_CHAT_ID` | رقم الشات |

وفي تبويب **Variables** (اختياري): `BRAND_NAME` و `BRAND_CTA`.

> أو بأمر واحد:
> ```bash
> gh secret set TELEGRAM_BOT_TOKEN
> gh secret set TELEGRAM_CHAT_ID
> ```

### 3. خلاص — يشتغل لحاله
| الـ Workflow | متى يشتغل |
|---|---|
| `AI News Watch` | كل ١٥ دقيقة — يرسل أي خبر جديد |
| `AI News Daily Digest` | يوميًا ٨ صباحًا بتوقيت السعودية |
| `Keepalive` | أسبوعيًا — يمنع GitHub من إيقاف الجدولة |

تبغى تجربه الحين؟ تبويب **Actions** → `AI News Watch` → **Run workflow**.

**ملاحظات:**
- أقل فترة تسمح فيها GitHub Actions هي ١٥ دقيقة، وأحيانًا يتأخر التشغيل شوي وقت الذروة. لو تبغى لحظي فعلاً كل ٥ دقائق، تحتاج سيرفر دائم (Fly.io / Railway / VPS).
- ذاكرة الأخبار المرسلة تنحفظ في cache الـ Actions — فما يتكرر عليك خبر.

---

## ⚙️ الإعدادات

كل الإعدادات في `.env` — الشرح الكامل داخل [.env.example](.env.example).

أهمها:

```bash
WATCH_INTERVAL_SECONDS=300    # كل كم ثانية يفحص
WATCH_MAX_AGE_HOURS=24        # يتجاهل الأخبار الأقدم من كذا
WATCH_MAX_PER_CYCLE=20        # سقف الرسائل في الجولة الوحدة
WATCH_REGIONS=                # فاضي = كل المناطق (ما عدا الأبحاث)
WATCH_FILTER_NOISE=true       # يستبعد توقعات المباريات ومقالات الأسهم
```

### متابعة مناطق محددة فقط
```bash
WATCH_REGIONS=saudi,gulf,arabic     # الأخبار العربية والخليجية فقط
WATCH_REGIONS=usa,china             # أمريكا والصين فقط
WATCH_REGIONS=all                   # كل شي + الأوراق البحثية (arXiv)
```

المناطق المتاحة: `saudi` `gulf` `arabic` `usa` `china` `asia` `europe` `community` `research` `global`

---

## 🧠 وضع الذكاء (اختياري)
لو عندك [Ollama](https://ollama.com) شغال محليًا، فعّل في `.env`:
```bash
USE_LLM=true
OLLAMA_MODEL=qwen3:14b
```
بيكتب سكربت الريل باللهجة السعودية بصياغة أذكى بدل القوالب الجاهزة. لو Ollama مو شغال يرجع للقوالب تلقائيًا — ما يطيح أبدًا.

---

## 🗂 بنية المشروع

```
ai-news-agent/
├── watch.py                    # 🔴 المراقبة اللحظية
├── main.py                     # 📰 النشرة اليومية (مرة وحدة)
├── scheduler.py                # جدولة يومية محلية
├── .env.example                # انسخه إلى .env
├── .github/workflows/          # التشغيل التلقائي ٢٤/٧
└── ai_news_agent/
    ├── sources.py              # 📡 كل المصادر — زد وعدّل من هنا
    ├── watcher.py              # حلقة المراقبة والتنبيهات
    ├── fetchers.py             # جلب وتصنيف الأخبار
    ├── filters.py              # فلترة أخبار AI + استبعاد الضجيج
    ├── store.py                # ذاكرة الأخبار المرسلة (منع التكرار)
    ├── content.py              # سكربت الريل وأفكار المحتوى
    ├── telegram_bot.py         # بناء وإرسال رسائل تليجرام
    └── config.py               # قراءة الإعدادات من .env
```

## ➕ إضافة مصدر جديد

افتح [`ai_news_agent/sources.py`](ai_news_agent/sources.py) وضيف سطر في القائمة المناسبة:

```python
Source("اسم المصدر", "https://example.com/feed/", "usa"),
```

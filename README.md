# 🤖 AI News Agent — مراقبة لحظية لأخبار الذكاء الاصطناعي

وكيل Python يتابع **٥٤ مصدر AI حول العالم** (🇺🇸 أمريكا · 🇨🇳 الصين · 🇪🇺 أوروبا · 🌏 آسيا · 🇸🇦 السعودية · 🌴 الخليج) وأي خبر جديد يوصلك على تليجرام **فورًا**.

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
- **أول تشغيل ما يرسل أخبار** — يسجّل الموجود كـ«مقروء» عشان ما تنصدم بـ٤٠٠ رسالة دفعة وحدة. من الجولة الثانية يبدأ يرسل الجديد فقط.
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
WATCH_MIN_SCORE=0             # 🔥 0=الكل، 3=يصلح محتوى، 6=الأقوى فقط
```

### متابعة مناطق محددة فقط
```bash
WATCH_REGIONS=saudi,gulf,arabic     # الأخبار العربية والخليجية فقط
WATCH_REGIONS=usa,china             # أمريكا والصين فقط
WATCH_REGIONS=all                   # كل شي + الأوراق البحثية (arXiv)
```

المناطق المتاحة: `tools` `saudi` `gulf` `arabic` `usa` `china` `asia` `europe` `community` `research` `global`

---

## 🔥 ترتيب المحتوى حسب قوته للتيك توك

مو كل خبر AI يصلح ريل. البوت يعطي كل خبر **درجة** ويرسل الأقوى أول، وعليه علامة:

| العلامة | الدرجة | نوع الخبر |
|---|---|---|
| 🔥🔥 **صوّر ريل** | ٦+ | إطلاق أداة، ميزة جديدة، شي مجاني أو مفتوح المصدر |
| 🔥 **يصلح محتوى** | ٣+ | تحديث منتج، مقارنة، تجربة عملية |
| — عادي | أقل | أرباح، أسهم، قضايا، تعيينات إدارية |

**أمثلة من التشغيل الفعلي:**
```
🔥 [ 8] Google Launches Gemini Omni 1.1 Flash with 4K AI Video
🔥 [ 8] OpenAI Launches Apple Messages Integration for ChatGPT
🔥 [ 7] Show HN: AI Harness that lets Codex and Claude intercommunicate
   [-1] Nvidia Q3 earnings beat analyst estimates, stock jumps 8%
```

تبغى الأخبار القوية بس؟ في `.env`:
```bash
WATCH_MIN_SCORE=3     # اللي يصلح محتوى فقط
WATCH_MIN_SCORE=6     # الأقوى فقط — أخبار تستاهل ريل
```

قواعد التقييم كلها في [`ai_news_agent/viral.py`](ai_news_agent/viral.py) — تقدر تعدّلها وتزيد كلماتك.

### مصادر الأدوات والإطلاقات
عشان محتوى تيك توك، البوت يتابع مصادر مخصصة للأدوات الجديدة:
Product Hunt · Show HN · TLDR AI · r/ChatGPT، وتنبيهات مخصصة لـ **Gemini** و **Claude Code** و **ChatGPT** وأدوات فيديو AI (Sora، Veo، Runway، Midjourney).

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

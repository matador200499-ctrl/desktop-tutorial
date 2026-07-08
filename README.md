# أتمتة قناة اللقطة (Al Laqta) — Claude + YouTube API + GitHub Actions

نظام بسيط بيعمل الآتي أوتوماتيك:
1. Claude (Anthropic API) يولّد **عنوان + وصف + تاجز + سكريبت مختصر** لأي موضوع تحدده.
2. GitHub Actions يرفع فيديو جاهز (حطيته إنت) على يوتيوب بالبيانات دي، تلقائيًا.

---

## 1) هيكل المشروع

```
al-laqta-automation/
├── .github/workflows/publish_video.yml   ← الأتمتة نفسها (تشتغل من تبويب Actions)
├── videos/
│   ├── pending/     ← حط الفيديو الجاهز هنا (mp4) قبل ما تشغّل الأتمتة
│   └── uploaded/     ← الفيديوهات اللي اترفعت بتتنقل هنا تلقائي
├── scripts/
│   ├── generate_content.py   ← بيكلم Claude API
│   └── upload_youtube.py     ← بيرفع على يوتيوب
├── get_refresh_token.py      ← تشغّله مرة واحدة بس على جهازك (مش على GitHub)
├── requirements.txt
└── .gitignore
```

---

## 2) الإعداد لأول مرة (خطوة بخطوة)

### أ) اعمل ريبو على GitHub
ارفع المجلد ده كامل على ريبو جديد (خليه **Private** عشان فيه بيانات حساسة).

### ب) جهّز مفاتيح Google (YouTube Data API v3)
1. روح على [Google Cloud Console](https://console.cloud.google.com/) → اعمل مشروع جديد.
2. فعّل **YouTube Data API v3** من مكتبة الـ APIs.
3. روح **OAuth consent screen** → اختار External → املا البيانات الأساسية → ضيف حسابك كـ Test User.
4. روح **Credentials** → Create Credentials → OAuth client ID → نوعه **Desktop app**.
5. نزّل ملف الـ JSON ده، وسمّيه `client_secrets.json` — ده نفس نوع الملف اللي عندك بالظبط.

### ج) اعمل Refresh Token مرة واحدة (على جهازك، مش على GitHub)
عشان GitHub Actions يقدر يرفع فيديوهات من غير ما حد يفتح متصفح كل مرة، لازم نولّد **refresh token** مرة واحدة يدويًا:

```bash
pip install -r requirements.txt
python get_refresh_token.py
```

هيفتحلك متصفح، سجّل دخول بحساب يوتيوب بتاع القناة، ووافق. هيطلع لك في الترمينال:
```
YOUR REFRESH TOKEN: 1//0abc...xyz
```
احتفظ بيه، هتحتاجه في الخطوة الجاية.

### د) ضيف الـ Secrets في GitHub
في الريبو: **Settings → Secrets and variables → Actions → New repository secret**، وضيف الآتي:

| اسم الـ Secret | القيمة |
|---|---|
| `ANTHROPIC_API_KEY` | مفتاح Claude API بتاعك |
| `YT_CLIENT_ID` | من client_secrets.json (client_id) |
| `YT_CLIENT_SECRET` | من client_secrets.json (client_secret) |
| `YT_REFRESH_TOKEN` | الناتج من خطوة (ج) |

**متحطش الملفات دي في الريبو نفسه أبدًا** — هي دلوقتي في `.gitignore` عشان محدش يشوفها لو الريبو اتسرب.

---

## 3) الاستخدام اليومي

1. حط ملف الفيديو الجاهز في `videos/pending/` وارفعه (commit + push) — أو ارفعه مباشرة من واجهة GitHub.
2. روح تبويب **Actions** في الريبو → اختار workflow اسمه **"Publish Video"** → **Run workflow**.
3. هيطلب منك تدخل:
   - **video_topic**: وصف موضوع الفيديو (Claude هيستخدمه يكتب العنوان/الوصف/التاجز)
   - **video_filename**: اسم ملف الفيديو بالظبط في `videos/pending/`
   - **privacy_status**: `private` أو `unlisted` أو `public`
4. الأتمتة تشتغل: تولّد المحتوى بـ Claude → ترفع الفيديو بيوتيوب بالبيانات دي → تنقل الفيديو لمجلد `uploaded/`.

هتلاقي العنوان والوصف والتاجز والسكريبت المستخدم محفوظين كـ "Artifact" في نتيجة الـ Run نفسه (تقدر تنزلهم من هناك).

---

## 4) ملاحظات مهمة

- الحد الافتراضي لـ YouTube Data API هو **6 رفعات فيديو يوميًا** تقريبًا (quota-based)، كافي جدًا لقناة بتنزل بانتظام.
- لو عايز تشغيل مجدول تلقائي (زي كل يوم الساعة كذا) بدل التشغيل اليدوي، ممكن نضيف `schedule:` trigger بسهولة — قولي وهضيفه.
- الأتمتة دي بترفع الفيديو بس، مش بتعمل مونتاج أو صوت أو صورة مصغرة (Thumbnail) — لو حابب نضيف توليد Thumbnail بالـ AI كمان ممكن نتكلم فيه في خطوة تانية.

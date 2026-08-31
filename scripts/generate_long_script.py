import os
import sys
from groq import Groq

# 1. إعداد العميل
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("FATAL ERROR: GROQ_API_KEY مش موجود في الـ Secrets")
    sys.exit(1)

client = Groq(api_key=api_key)

# 2. قراءة موضوع الفيديو
# بيحاول يقرأه من المتغير اللي بابعته الـ workflow أو من ملف topic.txt
topic = os.environ.get("VIDEO_TOPIC", "").strip()

if not topic:
    try:
        # لو الـ workflow بيكتب الموضوع في ملف مؤقت
        if os.path.exists("topic.txt"):
            with open("topic.txt", "r", encoding="utf-8") as f:
                topic = f.read().strip()
        elif os.path.exists("scripts/topic.txt"):
            with open("scripts/topic.txt", "r", encoding="utf-8") as f:
                topic = f.read().strip()
    except Exception as e:
        print(f"Warning: مقدرتش اقرا topic.txt: {e}")

if not topic:
    # لو لسه فاضي خد اول سطر من topics.txt
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            if lines:
                topic = lines[0]
    except:
        pass

if not topic:
    topic = "كيف تغيرت حياتنا اليومية بسبب الخوارزميات"

print(f"Generating script for topic: {topic}")

# 3. الموديلات اللي شغالة حاليا في Groq - بنجربهم بالترتيب
MODELS_TO_TRY = [
    "llama3-70b-8192",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-maverick-17b-128e-instruct"
]

def generate_script(topic_text):
    prompt = f"""
    اكتب سكريبت فيديو يوتيوب طويل ومشوق باللهجة المصرية العامية البسيطة عن موضوع: "{topic_text}"

    الشروط:
    - يبدأ بمقدمة قوية تخطف الانتباه (Hook)
    - مقسم لـ 4-5 فصول
    - مدة القراءة حوالي 8-10 دقائق (حوالي 1200-1500 كلمة)
    - لغة عربية بسيطة ومفهومة
    - في النهاية اطلب من المشاهد الاشتراك
    - لا تكتب تعليمات للمونتاج، اكتب النص المنطوق فقط
    """

    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            print(f"Trying model: {model_name}")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "انت كاتب سكريبتات يوتيوب محترف، تكتب بالعربي بطريقة مشوقة."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_error = e
            continue

    # لو كل الموديلات فشلت
    raise last_error

try:
    script_content = generate_script(topic)

    # 4. حفظ السكريبت
    os.makedirs("output", exist_ok=True)
    with open("output/script.txt", "w", encoding="utf-8") as f:
        f.write(script_content)

    # نحفظه برضه في المكان اللي باقي الخطوات بتقرا منه
    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(script_content)

    print("✅ Script generated successfully!")
    print(f"Length: {len(script_content)} chars")

except Exception as e:
    print(f"FATAL ERROR while generating script:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

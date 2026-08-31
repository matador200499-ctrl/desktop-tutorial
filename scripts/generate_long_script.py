import os, sys
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

topic = "ما الذي يحدث خلف الكواليس في صناعة الذكاء الاصطناعي"
if os.path.exists("topic.txt"):
    with open("topic.txt", "r", encoding="utf-8") as f:
        t=f.read().strip()
        if t: topic=t

print(f"Generating script for topic: {topic}")

# الموديلات الشغالة حاليا - 31/08/2026
MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]

for model in MODELS:
    try:
        print(f"Trying model: {model}")
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":"انت كاتب سكريبت يوتيوب محترف بالعربي"},
                {"role":"user","content":f"اكتب سكريبت طويل 1200 كلمة مشوق عن: {topic}"}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        text = r.choices[0].message.content
        os.makedirs("output", exist_ok=True)
        open("output/script.txt","w",encoding="utf-8").write(text)
        open("script.txt","w",encoding="utf-8").write(text)
        print(f"✅ Success with {model}")
        sys.exit(0)
    except Exception as e:
        print(f"{model} failed: {e}")

print("FATAL: كل الموديلات فشلت")
sys.exit(1)

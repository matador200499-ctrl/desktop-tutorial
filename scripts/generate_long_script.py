import json
import os
from groq import Groq

# تهيئة Groq API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_script(topic, duration_minutes=15):
    word_count = duration_minutes * 150
    prompt = f"اكتب سكريبت فيديو مفصل ومدته {duration_minutes} دقيقة عن موضوع: {topic}. قسمه لثلاثة أجزاء: العلوم، الطبيعة، وعلم النفس. الحد الأدنى {word_count} كلمة. أخرج النتيجة بصيغة JSON تحتوي على title, description, tags, و scenes (كل مشهد يحتوي id, text, visual_suggestions)."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت مساعد متخصص في توليد محتوى فيديو تعليمي باللغة العربية. يجب أن يكون الرد بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    video_topic = os.getenv("VIDEO_TOPIC", "تطور الذكاء الاصطناعي")
    script_output = generate_script(video_topic)
    if script_output:
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(script_output, f, ensure_ascii=False, indent=4)
        with open("content.json", "w", encoding="utf-8") as f:
            json.dump({"title": script_output["title"], "description": script_output["description"], "tags": script_output["tags"]}, f, ensure_ascii=False, indent=4)

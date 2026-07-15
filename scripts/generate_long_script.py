import json
import os
import openai # سنستخدم OpenAI API بدلاً من Groq

# تهيئة OpenAI API
# يجب أن يكون مفتاح API متاحاً كمتغير بيئة
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script(topic, duration_minutes=15):
    # تقدير عدد الكلمات اللازمة لمدة 15 دقيقة (بمعدل 150 كلمة/دقيقة)
    word_count = duration_minutes * 150

    prompt = f"""
    أنت مساعد متخصص في توليد محتوى فيديو تعليمي باللغة العربية. 
    الموضوع الرئيسي: {topic}
    
    الرجاء كتابة سكريبت فيديو مفصل ومدته {duration_minutes} دقيقة، مقسماً إلى ثلاثة أقسام رئيسية:
    1.  **العلوم**: (حوالي 5 دقائق) - تناول الجوانب العلمية للموضوع، الاكتشافات، المفاهيم.
    2.  **الطبيعة**: (حوالي 5 دقائق) - استكشاف العلاقة بين الموضوع والعالم الطبيعي، البيئة، الكائنات الحية.
    3.  **علم النفس**: (حوالي 5 دقائق) - ربط الموضوع بالسلوك البشري، الصحة النفسية، التأثيرات الاجتماعية.
    
    يجب أن يكون السكريبت متماسكاً، جذاباً، بلغة عربية فصحى مبسطة، مع روابط منطقية بين الأقسام. 
    يجب أن يتضمن السكريبت إشارات واضحة إلى أنواع المشاهد المرئية المقترحة لكل فقرة (مثلاً: [مشهد: رسوم بيانية لتطور الذكاء الاصطناعي]، [مشهد: لقطات وثائقية لغابات الأمازون]).
    
    الحد الأدنى للكلمات: {word_count} كلمة.
    
    الرجاء إخراج السكريبت بصيغة JSON كالتالي:
    {{
        "title": "عنوان الفيديو المقترح",
        "description": "وصف موجز للفيديو",
        "tags": ["كلمة مفتاحية1", "كلمة مفتاحية2"],
        "scenes": [
            {{"id": 1, "text": "نص المشهد الأول", "visual_suggestions": "اقتراحات مرئية للمشهد الأول"}},
            {{"id": 2, "text": "نص المشهد الثاني", "visual_suggestions": "اقتراحات مرئية للمشهد الثاني"}}
        ]
    }}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o", # يمكن تغيير النموذج حسب التوفر والجودة المطلوبة
            messages=[
                {"role": "system", "content": "أنت مساعد متخصص في توليد محتوى فيديو تعليمي باللغة العربية."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000, # زيادة الحد الأقصى للتوكنات ليتناسب مع المحتوى الطويل
            response_format={ "type": "json_object" }
        )
        script_data = json.loads(response.choices[0].message.content)
        return script_data
    except Exception as e:
        print(f"Error generating script: {e}")
        return None

if __name__ == "__main__":
    # هذا الجزء سيتم استدعاؤه من GitHub Actions
    # سيقرأ الموضوع من متغير بيئة أو من topics.txt
    
    # افتراضياً، سنقرأ من topics.txt كما في المشروع السابق
    topic_file = "topics.txt"
    video_topic = ""
    if os.path.exists(topic_file):
        with open(topic_file, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
        if topics:
            video_topic = topics[0] # نأخذ أول موضوع
            # يمكننا هنا نقل الموضوع إلى used_topics.txt وحذفه من topics.txt
            # ولكن هذا سيتم إدارته بواسطة pick_topic.py لاحقاً
    
    if not video_topic:
        video_topic = os.getenv("VIDEO_TOPIC", "تطور الذكاء الاصطناعي وتأثيره على البيئة والسلوك البشري")

    print(f"Generating script for topic: {video_topic}")
    script_output = generate_script(video_topic)

    if script_output:
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(script_output, f, ensure_ascii=False, indent=4)
        print("Script generated successfully to script.json")
        
        # تحديث content.json أيضاً
        content_data = {
            "title": script_output["title"],
            "description": script_output["description"],
            "tags": script_output["tags"]
        }
        with open("content.json", "w", encoding="utf-8") as f:
            json.dump(content_data, f, ensure_ascii=False, indent=4)
        print("Content data generated successfully to content.json")
    else:
        print("Failed to generate script.")

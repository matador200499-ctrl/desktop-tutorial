import json
import os
import subprocess
import re

def generate_voice(script_file="script.json", audio_dir="audio"):
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    total_duration = 0
    durations = []

    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", i + 1)
        text = scene.get("text", "")
        output_file = os.path.join(audio_dir, f"scene_{scene_id}.mp3")

        # إزالة أي علامات Markdown أو اقتراحات مرئية من النص قبل تحويله لصوت
        clean_text = re.sub(r'\['.*?\]', '', text) # إزالة [اقتراحات مرئية]
        clean_text = re.sub(r'\*\*.*?\*\*', '', clean_text) # إزالة **نص سميك**

        print(f"جاري توليد صوت المشهد {scene_id}/{len(scenes)}...")
        
        # استخدام edge-tts لتوليد الصوت
        # يمكن تغيير الصوت (ar-EG-SalmaNeural, ar-SA-HamedNeural, ar-SA-ZariyahNeural)
        command = [
            "edge-tts",
            "--text", clean_text,
            "--voice", "ar-EG-SalmaNeural", 
            "--write-media", output_file
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            
            # الحصول على مدة الملف الصوتي
            duration_command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                output_file
            ]
            duration_output = subprocess.check_output(duration_command, text=True).strip()
            duration = float(duration_output)
            print(f"  المدة: {duration:.2f} ثانية")
            total_duration += duration
            durations.append({"scene_id": scene_id, "duration": duration})

        except subprocess.CalledProcessError as e:
            print(f"  خطأ في توليد الصوت للمشهد {scene_id}: {e.stderr}")
            durations.append({"scene_id": scene_id, "duration": 0, "error": e.stderr})
        except FileNotFoundError:
            print("  خطأ: أداة edge-tts أو ffprobe غير موجودة. يرجى التأكد من تثبيتها.")
            break

    print(f"إجمالي مدة الصوت: {total_duration:.2f} ثانية (~{total_duration/60:.1f} دقيقة)")
    
    # حفظ مدد المشاهد في ملف durations.json
    with open(os.path.join(audio_dir, "durations.json"), "w", encoding="utf-8") as f:
        json.dump(durations, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_voice()

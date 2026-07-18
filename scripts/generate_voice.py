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
        
        # طريقة تنظيف نصوص آمنة جداً
        clean_text = text
        if "[" in clean_text and "]" in clean_text:
            clean_text = re.sub(r"\[.*?\]", "", clean_text)
        if "**" in clean_text:
            clean_text = clean_text.replace("**", "")
            
        print(f"Generating voice for scene {scene_id}...")
        
        command = [
            "edge-tts", 
            "--text", clean_text, 
            "--voice", "ar-EG-SalmaNeural", 
            "--write-media", output_file
        ]
        
        try:
            subprocess.run(command, check=True)
            # قياس مدة الصوت
            duration_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", output_file
            ]
            duration_out = subprocess.check_output(duration_cmd).decode().strip()
            duration = float(duration_out)
            total_duration += duration
            durations.append({"scene_id": scene_id, "duration": duration})
        except Exception as e:
            print(f"Error in scene {scene_id}: {e}")
            durations.append({"scene_id": scene_id, "duration": 0})
            
    with open(os.path.join(audio_dir, "durations.json"), "w", encoding="utf-8") as f:
        json.dump(durations, f, ensure_ascii=False, indent=4)
    print(f"Total duration: {total_duration} seconds")

if __name__ == "__main__":
    generate_voice()

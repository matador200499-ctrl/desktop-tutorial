import json
import os
from moviepy import *
from moviepy.video.fx import Loop
from moviepy.video.tools.subtitles import SubtitlesClip

# تحديد الخط العربي (يجب أن يكون الخط مثبتاً في البيئة)
ARABIC_FONT = "Noto-Naskh/NotoNaskh-Regular.ttf"  # تأكد من وجود هذا الخط أو استبدله بخط آخر

def assemble_video(script_file="script.json", audio_dir="audio", clips_dir="clips", output_file="final_video.mp4"):
    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)
    with open(os.path.join(audio_dir, "durations.json"), "r", encoding="utf-8") as f:
        audio_durations = json.load(f)
    scenes = script_data.get("scenes", [])

    final_clips = []
    current_time = 0
    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", i + 1)
        narration_text = scene.get("text", "")
        visual_suggestions = scene.get("visual_suggestions", "")
        clip_path = scene.get("clip_path")
        audio_file = os.path.join(audio_dir, f"scene_{scene_id}.mp3")
        audio_clip = AudioFileClip(audio_file)
        audio_duration = audio_clip.duration

        # اختيار مقطع الفيديو
        video_clip = None
        if clip_path and os.path.exists(clip_path):
            video_clip = VideoFileClip(clip_path)
            # قص أو تمديد مقطع الفيديو ليتناسب مع مدة الصوت
            if video_clip.duration > audio_duration:
                video_clip = video_clip.subclipped(0, audio_duration)
            elif video_clip.duration < audio_duration:
                # إذا كان مقطع الفيديو أقصر، نكرره باستخدام تأثير Loop الجديد
                video_clip = video_clip.with_effects([Loop(duration=audio_duration)])
        else:
            print(f"تحذير: لم يتم العثور على مقطع فيديو للمشهد {scene_id}. سيتم استخدام شاشة سوداء.")
            video_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=audio_duration)

        # إضافة النص (Overlay) على الفيديو
        txt_clip = TextClip(
            font=ARABIC_FONT,
            text=narration_text,
            font_size=40,
            color='white',
            stroke_color='black',
            stroke_width=1.5,
            method='caption',
            size=(int(video_clip.w * 0.8), None),
            text_align='center',
            bg_color=None
        )
        txt_clip = txt_clip.with_duration(audio_duration).with_position(('center', 'bottom'))

        # دمج النص مع الفيديو
        final_clip_with_text = CompositeVideoClip([video_clip, txt_clip])
        final_clip_with_text = final_clip_with_text.with_audio(audio_clip)
        final_clips.append(final_clip_with_text)
        current_time += audio_duration

    # تجميع كل المشاهد في فيديو واحد
    if final_clips:
        final_video = concatenate_videoclips(final_clips)
        print(f"جاري كتابة الفيديو النهائي إلى {output_file}...")
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        print("تم الانتهاء من تجميع الفيديو بنجاح.")
    else:
        print("لا توجد مشاهد لتجميعها.")

if __name__ == "__main__":
    assemble_video()

import json
import os
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_videos(query, per_page=1, orientation="landscape"):
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY environment variable not set.")
        return []

    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation
    }
    url = "https://api.pexels.com/videos/search"

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        videos = []
        for video_entry in data.get("videos", [])[:per_page]:
            # البحث عن أعلى جودة ممكنة للفيديو
            best_quality_link = None
            for file in video_entry.get("video_files", []):
                if file.get("quality") == "hd" or file.get("quality") == "sd": # يمكن تعديل هذا لاختيار جودة أعلى مثل "uhd"
                    best_quality_link = file.get("link")
                    break
            if best_quality_link:
                videos.append({
                    "id": video_entry["id"],
                    "url": video_entry["url"],
                    "image": video_entry["image"],
                    "duration": video_entry["duration"],
                    "link": best_quality_link
                })
        return videos
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from Pexels: {e}")
        return []

def download_video(video_url, output_path):
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {video_url} to {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")
        return False

if __name__ == "__main__":
    # هذا الجزء سيتم استدعاؤه من سكربت المونتاج أو مباشرة
    # سيقرأ اقتراحات المشاهد من script.json
    
    script_file = "script.json"
    clips_dir = "clips"
    if not os.path.exists(clips_dir):
        os.makedirs(clips_dir)

    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    
    # قائمة لتتبع المقاطع التي تم تنزيلها لتجنب التكرار
    downloaded_clips = {}

    for i, scene in enumerate(scenes):
        visual_suggestions = scene.get("visual_suggestions", "")
        if visual_suggestions:
            # استخدام أول اقتراح كاستعلام للبحث
            query = visual_suggestions.split(',')[0].strip()
            if query not in downloaded_clips:
                print(f"البحث عن مقطع فيديو لـ: {query}")
                videos = fetch_videos(query, per_page=1)
                if videos:
                    video_info = videos[0]
                    output_path = os.path.join(clips_dir, f"clip_{i}.mp4")
                    if download_video(video_info["link"], output_path):
                        downloaded_clips[query] = output_path
                        scene["clip_path"] = output_path # إضافة مسار المقطع للسكريبت
                else:
                    print(f"لم يتم العثور على مقاطع فيديو لـ: {query}")
            else:
                scene["clip_path"] = downloaded_clips[query] # استخدام مقطع تم تنزيله بالفعل
        else:
            print(f"لا توجد اقتراحات مرئية للمشهد {i+1}")

    # حفظ السكريبت المحدث بمسارات المقاطع
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=4)
    print("تم تحديث script.json بمسارات المقاطع.")

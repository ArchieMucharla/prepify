# Proof of concept 

# Tools: pip install openai-whisper easyocr opencv-python yt-dlp

import os
import subprocess
import whisper
import cv2
import easyocr
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Step 1: Download tiktok video
def download_video(tiktok_url, output_path = "video/tiktok.mp4"):
    
    cmd = f'yt-dlp -o "{output_path}" "{tiktok_url}"' # output_path becomes the new file name, and tiktok_url becomes the actual URL passed
    subprocess.run(cmd, shell=True) # runs the command 
    print("✅ Video downloaded.")

def extract_caption(tiktok_url):
    cmd = ["yt-dlp", "-j", tiktok_url] # to get video metadata in JSON format
    result = subprocess.run(cmd, capture_output=True, text=True)    

    if result.returncode != 0:
        print("Error running yt-dlp for extract_caption")
        print(result.stderr)
        return None

    data = json.loads(result.stdout) 
    caption = data.get("description", "")
    print(caption)
    return caption.strip()

# Step 2: Extract frames from the video
def extract_frames(video_path, output_folder = "frames", fps = 1):
    import subprocess

    os.makedirs(output_folder, exist_ok=True) # creatres a folder to hold the extracted images

    cmd = f'ffmpeg -i "{video_path}" -vf "fps={fps}" {output_folder}/frame_%03d.png' # extracts still images from the video
    subprocess.run(cmd, shell=True)
    print(f"✅ Frames extracted to '{output_folder}' folder.")
 
# Step 3: Transcribe audi o(Using OpenAI Whisper)
def transcribe_audio(video_path, model_size = "medium"):
    import whisper
    model = whisper.load_model(model_size) # loads the whisper model
    result = model.transcribe(video_path)
    print("✅ Transcription complete.")

    return result["text"] # returns only the text 

# Step 4: Extract on screen text using OCR (Optical Character Recognition)
def ocr_frames(frame_folder = "frames", num_frames = 5):
    import easyocr # The OCR tool that reads text from images.
    import os # Used to list and access files in the frames/ folder.

    reader = easyocr.Reader(["en"])
    texts = []

    for filenmae in sorted(os.listdir(frame_folder))[:num_frames]: # loops through the first few image files (5 in our case)
        if filenmae.endswith(".png"): # safety check 
            frame_path = os.path.join(frame_folder, filenmae) # Builds the full path to each frame file
            results = reader.readtext(frame_path) # Runs OCR on the image using EasyOCR. Results is a list of results for each text box detected on the image.

            for box in results: # Collecting the raw text 
                text = box[1] # contains the actual text 
                texts.append(text)

    print("✅ OCR complete.")
    return texts

#Step 5 : Parse content extracted to standard9ze format
def create_recipe(caption, transcript, ocr_text):
    full_text = "caption: " + caption + " , transcript: "+ transcript + " , ocr text : " + " ".join(ocr_text)


    response = client.chat.completions.create(
        model="o4-mini", 
            messages=[{ "role": "user","content": f"""
I have extracted all possible data from a TikTok recipe video: the caption, transcription of audio, and OCR text from frames. Please use reasonable assumptions/inferences about cooking to fill in gaps where content may be missing.
Please parse this and output a structured recipe in JSON format with:
- Ingredients (with name, amount, and units)
- Steps (ordered list)
- If possible, estimated macros (calories, protein, fat, carbs)
Here is the content:
{full_text}
"""}
        ] )               

    return response.choices[0].message.content

    
def run_tiktok_parser(tiktok_url):
    video_path = "video/tiktok.mp4"
    frames_folder = "frames"

    download_video(tiktok_url)
    caption = extract_caption(tiktok_url) 
    extract_frames(video_path, output_folder=frames_folder)
    transcript = transcribe_audio(video_path)
    ocr_text = ocr_frames(frame_folder=frames_folder)

    print("\nCAPTION:\n", caption)
    print("\nTRANSCRIPTION:\n", transcript)
    print("\nOCR TEXT:\n", ocr_text)
    result_json = create_recipe(caption, transcript, ocr_text)
    print("\nPARSED RECIPE:\n", result_json)
    if os.path.exists("video/tiktok.mp4"):
        os.remove("video/tiktok.mp4")
        os.rmdir("video")
    if os.path.exists("frames"):
        for file in os.listdir("frames"):
            os.remove(os.path.join("frames", file))
        os.rmdir("frames")



# Entry point
if __name__ == "__main__":
    url = input("Paste TikTok Video URL: ").strip()
    run_tiktok_parser(url)

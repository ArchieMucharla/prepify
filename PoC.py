# Proof of concept 

# Tools: pip install openai-whisper easyocr opencv-python yt-dlp

import os
import subprocess
import whisper
import cv2
import easyocr

# Step 1: Download tiktok video
def download_video(tiktok_url, output_path = "tiktok_video.mp4"):
    
    import subprocess # gives access to Python's ability to run shell/terminal commands like you are typing in PowerShell

    cmd = f'yt-dlp -o "{output_path}" "{tiktok_url}"' # output_path becomes the new file name, and tiktok_url becomes the actual URL passed
    subprocess.run(cmd, shell=True) # runs the command 
    print("✅ Video downloaded.")

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
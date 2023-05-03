import os
import cv2
import time
import random
import tempfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import face_recognition

def download_tiktok_video(url, output_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-dev-shm-usage")

    # Update the path to your ChromeDriver location
    driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
    driver.get("https://snaptik.app/")
    driver.find_element(By.ID, "url").send_keys(url)
    driver.find_element(By.CSS_SELECTOR, "#hero > div > form > button").click()

    
    # Wait for the download link to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#download > div > div.video-links > a:nth-child(1)"))
    )

    # 4: download the video at the selector: #download > div > div.video-links > a:nth-child(1)
    download_button = driver.find_elements(By.CSS_SELECTOR, "#download > div > div.video-links > a:nth-child(1)")
    download_url = download_button[0].get_attribute("href")

    response = requests.get(download_url)

    with open(output_path, "wb") as f:
        f.write(response.content)

    driver.quit()

def extract_faces_from_face_frames(face_frames):
    face_images = {}
    for person_id, frame_numbers in face_frames.items():
        person_faces = []
        for frame_number in frame_numbers:
            face_file = f"faces/person{person_id}/person{person_id}_frame{frame_number}.jpg"
            face_image = cv2.imread(face_file)
            person_faces.append(face_image)
        face_images[person_id] = person_faces
    return face_images

def save_faces_to_folders(face_images, output_folder):
    for person_id, person_faces in face_images.items():
        person_folder = os.path.join(output_folder, f"person{person_id}")
        os.makedirs(person_folder, exist_ok=True)
        for idx, face_image in enumerate(person_faces):
            if not face_image is None:
                face_file = os.path.join(person_folder, f"person{person_id}_face{idx}.jpg")
                cv2.imwrite(face_file, face_image)


def extract_faces_from_video(video_path, output_folder):
    video_capture = cv2.VideoCapture(video_path)

    frame_number = 0
    face_frames = {}

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_number += 1

        if frame_number % 20 == 0:  # Process every 20th frame
            face_locations = face_recognition.face_locations(frame)

            for index, face_location in enumerate(face_locations):
                top, right, bottom, left = face_location
                face_image = frame[top:bottom, left:right]
                output_person_folder = os.path.join(output_folder, f"person{index}")
                os.makedirs(output_person_folder, exist_ok=True)

                # Crop to head and shoulders
                height, width = face_image.shape[:2]
                top_crop = int(top - 0.5 * height)
                bottom_crop = int(bottom + 0.5 * height)
                left_crop = int(left - 0.4 * width)
                right_crop = int(right + 0.4 * width)

                cropped_image = frame[top_crop:bottom_crop, left_crop:right_crop]
                if not cropped_image.shape[0] or not cropped_image.shape[1]:
                    continue  # Skip empty frames

                resized_image = cv2.resize(cropped_image, (768, 768))

                output_path = os.path.join(output_person_folder, f"person{index}_frame{frame_number}.jpg")
                cv2.imwrite(output_path, resized_image)

                if index not in face_frames:
                    face_frames[index] = []
                face_frames[index].append(frame_number)

    video_capture.release()

    return face_frames
def main():
    # Ask user if they have multiple videos to process
    has_multiple_videos = input("Do you have multiple videos to process? (Yes/No): ").lower() in ["yes", "y"]

    if has_multiple_videos:
        # Ask user for path to file containing multiple TikTok URLs
        urls_file = input("Please enter the path to the file containing TikTok URLs: ")

        # Create output folder for all videos
        output_folder = "output"

        # Read URLs from file
        with open(urls_file) as f:
            urls = [line.strip() for line in f]

        # Process each video
        for url in urls:
            print("Processing video:", url)
            # Create output folder for this video
            video_folder = os.path.join(output_folder, os.path.splitext(os.path.basename(url))[0])
            os.makedirs(video_folder, exist_ok=True)

            with tempfile.TemporaryDirectory() as tmpdir:
                temp_video_file = os.path.join(tmpdir, f"{random.randint(1000, 9999)}_temp_video.mp4")
                download_tiktok_video(url, temp_video_file)
                face_frames = extract_faces_from_video(temp_video_file, os.path.join(video_folder, "Faces"))
                face_images = extract_faces_from_face_frames(face_frames)
                save_faces_to_folders(face_images, os.path.join(video_folder, "Faces"))

        print("All videos processed.")
    else:
        # Ask user for TikTok URL
        tiktok_url = input("Enter TikTok URL: ")
        output_folder = "output"

        # Process single video
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_video_file = os.path.join(tmpdir, f"{random.randint(1000, 9999)}_temp_video.mp4")
            download_tiktok_video(tiktok_url, temp_video_file)
            face_frames = extract_faces_from_video(temp_video_file, os.path.join(output_folder, "Faces"))
            face_images = extract_faces_from_face_frames(face_frames)
            save_faces_to_folders(face_images, os.path.join(output_folder, "Faces"))
            print("Face images saved to:", os.path.abspath(os.path.join(output_folder, "Faces")))

        print("Video processed.")




if __name__ == "__main__":
    main()

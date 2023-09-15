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
from urllib.parse import urlsplit
import shutil
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def download_tiktok_video(url, output_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Add this line

    # Update the path to your ChromeDriver location
    service = Service(executable_path='./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://snaptik.app/")
    driver.find_element(By.ID, "url").send_keys(url)
    driver.find_element(By.CSS_SELECTOR, "#hero > div > form > button").click()

    # Wait for the download link to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#download > div > div.video-links > a:nth-child(2)"))
    )

    # Download the video at the selector: #download > div > div.video-links > a:nth-child(1)
    download_button = driver.find_elements(By.CSS_SELECTOR, "#download > div > div.video-links > a:nth-child(2)")
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

def extract_faces_from_video(video_path, output_folder, save_all_frames=False):
    video_capture = cv2.VideoCapture(video_path)

    frame_number = 0
    face_frames = {}

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_number += 1
        if save_all_frames:
            all_frames_folder = os.path.join(output_folder, "frames")
            os.makedirs(all_frames_folder, exist_ok=True)
            frame_output_path = os.path.join(all_frames_folder, f"frame{frame_number}.jpg")
            cv2.imwrite(frame_output_path, frame)

        if frame_number % 20 == 0:  # Process every 20th frame
            face_locations = face_recognition.face_locations(frame)

            if len(face_locations) == 0:  # Skip frame if no faces detected
                continue

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

                # Check if there is a face in the resized and cropped image
                face_locations_resized = face_recognition.face_locations(resized_image)
                if len(face_locations_resized) == 0:  # Skip if no face detected
                    continue

                output_path = os.path.join(output_person_folder, f"person{index}_frame{frame_number}.jpg")
                cv2.imwrite(output_path, resized_image)

                if index not in face_frames:
                    face_frames[index] = []
                face_frames[index].append(frame_number)

    video_capture.release()

    return face_frames


def get_video_links_from_profile(profile_url, num_videos):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Add this line

    service = Service(executable_path='./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(profile_url)
    print(profile_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[2]/div[2]/div/div/div[2]/a'))
    )

    video_cards = driver.find_elements(By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[2]/div[2]/div/div/div[2]/a')

    video_links = []

    for i in range(min(num_videos, len(video_cards))):
        video_link = video_cards[i].get_attribute("href")
        video_links.append(video_link)

    driver.quit()
    return video_links
def get_face_encodings(face_images):
    face_encodings = {}
    for person_id, person_faces in face_images.items():
        encodings = []
        for face_image in person_faces:
            if face_image is not None:
                encoding = face_recognition.face_encodings(face_image)
                if len(encoding) > 0:
                    encodings.append(encoding[0])
        face_encodings[person_id] = encodings
    return face_encodings


def group_similar_faces(face_images, threshold=0.6):
    face_encodings = get_face_encodings(face_images)
    grouped_faces = []
    ungrouped_faces = list(face_images.keys())

    while ungrouped_faces:
        current_face = ungrouped_faces.pop(0)
        current_face_encodings = face_encodings[current_face]

        similar_faces = [current_face]
        remaining_faces = []

        for other_face in ungrouped_faces:
            other_face_encodings = face_encodings[other_face]

            if not other_face_encodings:
                continue

            distances = face_recognition.face_distance(current_face_encodings, other_face_encodings[0])
            if np.any(distances < threshold):
                similar_faces.append(other_face)
            else:
                remaining_faces.append(other_face)

        grouped_faces.append(similar_faces)
        ungrouped_faces = remaining_faces

    return grouped_faces


def main():
    # Ask user for TikTok URL or profile
    tiktok_choice = input("Do you want to process a single TikTok video or a TikTok profile? (Video/Profile): ").lower()

    if tiktok_choice in ["profile", "p"]:
        # Ask user for TikTok profile username
        tiktok_username = input("Enter TikTok profile username: ")
        profile_url = f"https://www.tiktok.com/@{tiktok_username}"
        num_videos = int(input("Enter the number of videos to download: "))

        # Get video links from profile
        video_links = get_video_links_from_profile(profile_url, num_videos)

        # Create output folder for all videos
        output_folder = "output"

        # Process each video
        for url in video_links:
            print("Processing video:", url)
            # Create output folder for this video
            video_folder = os.path.join(output_folder, "@" + tiktok_username, os.path.splitext(os.path.basename(url))[0])
            os.makedirs(video_folder, exist_ok=True)

            with tempfile.TemporaryDirectory() as tmpdir:
                temp_video_file = os.path.join(tmpdir, f"{random.randint(1000, 9999)}_temp_video.mp4")
                download_tiktok_video(url, temp_video_file)
                face_frames = extract_faces_from_video(temp_video_file, os.path.join(video_folder), save_all_frames=True)
                face_images = extract_faces_from_face_frames(face_frames)
                save_faces_to_folders(face_images, os.path.join(video_folder))

        print("All videos processed.")
        # Merge face folders from different videos
        username_faces_folder = os.path.join(output_folder, "@" + tiktok_username, "Faces")
        os.makedirs(username_faces_folder, exist_ok=True)

        for person_id in range(100):  # Assuming max 100 persons in the videos
            merged_person_folder = os.path.join(username_faces_folder, f"person{person_id}")
            if not os.path.exists(merged_person_folder):
                os.makedirs(merged_person_folder)
            else:
                continue  # If folder already exists, skip to avoid duplication

            face_idx = 0
            for url in video_links:
                video_folder = os.path.join(output_folder, "@" + tiktok_username, os.path.splitext(os.path.basename(url))[0])
                person_folder = os.path.join(video_folder, f"person{person_id}")

                if os.path.exists(person_folder):
                    for face_file in os.listdir(person_folder):
                        src = os.path.join(person_folder, face_file)
                        dst = os.path.join(merged_person_folder, f"person{person_id}_face{face_idx}.jpg")
                        shutil.copyfile(src, dst)
                        face_idx += 1
    else:
        # Ask user for TikTok URL
        tiktok_url = input("Enter TikTok URL: ")
        # Extract the username from the video URL
        url_parts = urlsplit(tiktok_url)
        username = url_parts.path.split('/')[1]

        # Update the output directory to include the username
        output_folder = os.path.join("output", username, os.path.splitext(os.path.basename(tiktok_url))[0])

        # Create the directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Process single video
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_video_file = os.path.join(tmpdir, f"{random.randint(1000, 9999)}_temp_video.mp4")
            download_tiktok_video(tiktok_url, temp_video_file)
            face_frames = extract_faces_from_video(temp_video_file, os.path.join(output_folder), save_all_frames=True)
            face_images = extract_faces_from_face_frames(face_frames)
            save_faces_to_folders(face_images, os.path.join(output_folder))
            print("Face images saved to:", os.path.abspath(os.path.join(output_folder)))

        print("Video processed.")


if __name__ == "__main__":
    main()

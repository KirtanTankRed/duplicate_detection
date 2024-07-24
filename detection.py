import os
import cv2
import numpy as np
from PIL import Image, ImageStat, ImageFilter
import streamlit as st
from imagededup.methods import CNN

# Set the image folder path
img_folder = 'https://github.com/KirtanTankRed/duplicate_detection/tree/main/images'

# Initialize the CNN encoder
myencoder = CNN()

# Find duplicates
duplicates = myencoder.find_duplicates(image_dir=img_folder, min_similarity_threshold=0.70)

# Function to group duplicates into nested lists
def group_duplicates(duplicates_dict):
    seen = set()
    groups = []

    for key, values in duplicates_dict.items():
        if key not in seen:
            group = set(values) | {key}
            groups.append(list(group))
            seen.update(group)
    
    return groups

# Group duplicates
duplicate_groups = group_duplicates(duplicates)

# Function to measure parameters
def measure_parameters(image_path):
    # Open the image
    image = Image.open(image_path)
    
    # Measure brightness
    brightness = np.mean(image)
    
    # Measure contrast
    contrast = np.std(image)
    
    # Measure sharpness
    laplacian = cv2.Laplacian(np.array(image), cv2.CV_64F)
    sharpness = np.var(laplacian)
    
    # Measure noise (blurness)
    blurred_image = cv2.GaussianBlur(np.array(image), (5, 5), 0)
    difference = cv2.absdiff(np.array(image), blurred_image)
    blurness = np.std(difference)
    
    return blurness, brightness, contrast, sharpness

# Function to select the best image based on parameters
def select_best_image(images):
    best_image = None
    best_score = -1

    for img in images:
        img_path = os.path.join(img_folder, img)
        blurness, brightness, contrast, sharpness = measure_parameters(img_path)
        
        # Score calculation (weights can be adjusted)
        score = (brightness * 0.3) + (contrast * 0.3) + (sharpness * 0.3) - (blurness * 0.1)
        
        if score > best_score:
            best_score = score
            best_image = img

    return best_image

# Streamlit app for displaying and deleting images
def display_images_for_deletion(duplicate_groups):
    for group in duplicate_groups:
        st.write(f"Group: {group}")
        cols = st.columns(len(group))
        selected_images = []

        for idx, img in enumerate(group):
            img_path = os.path.join(img_folder, img)
            image = Image.open(img_path)
            cols[idx].image(image, caption=img, use_column_width=True)
            if cols[idx].button(f"Delete {img}", key=img):
                selected_images.append(img_path)
                st.write(f"Selected for deletion: {img}")

        # Move or delete the selected images
        if st.button(f"Confirm deletion for group {group}", key=str(group)):
            for img_path in selected_images:
                if os.path.exists(img_path):
                    os.remove(img_path)
                    st.write(f"Deleted: {img_path}")

# Function for auto-suggesting the best image
def auto_suggest_best_image(duplicate_groups):
    for group in duplicate_groups:
        best_image = select_best_image(group)
        st.write(f"Suggested best image: {best_image} from group {group}")

        cols = st.columns(len(group))
        for idx, img in enumerate(group):
            img_path = os.path.join(img_folder, img)
            image = Image.open(img_path)
            cols[idx].image(image, caption=img, use_column_width=True)

        if st.button(f"Confirm auto-suggestion for group {group}", key=str(group) + "auto"):
            for img in group:
                if img != best_image:
                    img_path = os.path.join(img_folder, img)
                    if os.path.exists(img_path):
                        os.remove(img_path)
                        st.write(f"Deleted: {img_path}")

# Function to clear the image folder
def clear_img_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                st.write(f"Deleted: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                st.write(f"Deleted directory: {file_path}")
        except Exception as e:
            st.write(f'Failed to delete {file_path}. Reason: {e}')

# Streamlit UI
st.title("Duplicate Image Detection and Deletion")

st.sidebar.title("Options")
option = st.sidebar.selectbox("Choose a method", ("Manual Deletion", "Auto Suggestion"))

if st.sidebar.button("Clear Image Folder"):
    clear_img_folder(img_folder)

if option == "Manual Deletion":
    display_images_for_deletion(duplicate_groups)
elif option == "Auto Suggestion":
    auto_suggest_best_image(duplicate_groups)

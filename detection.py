# import os
# import cv2
# import numpy as np
# from PIL import Image, ImageStat, ImageFilter
# import streamlit as st
# from imagededup.methods import CNN

# # Set the image folder path
# img_folder = 'https://github.com/KirtanTankRed/duplicate_detection/tree/main/images'

# # Initialize the CNN encoder
# myencoder = CNN()

# # Find duplicates
# duplicates = myencoder.find_duplicates(image_dir=img_folder, min_similarity_threshold=0.70)

# # Function to group duplicates into nested lists
# def group_duplicates(duplicates_dict):
#     seen = set()
#     groups = []

#     for key, values in duplicates_dict.items():
#         if key not in seen:
#             group = set(values) | {key}
#             groups.append(list(group))
#             seen.update(group)
    
#     return groups

# # Group duplicates
# duplicate_groups = group_duplicates(duplicates)

# # Function to measure parameters
# def measure_parameters(image_path):
#     # Open the image
#     image = Image.open(image_path)
    
#     # Measure brightness
#     brightness = np.mean(image)
    
#     # Measure contrast
#     contrast = np.std(image)
    
#     # Measure sharpness
#     laplacian = cv2.Laplacian(np.array(image), cv2.CV_64F)
#     sharpness = np.var(laplacian)
    
#     # Measure noise (blurness)
#     blurred_image = cv2.GaussianBlur(np.array(image), (5, 5), 0)
#     difference = cv2.absdiff(np.array(image), blurred_image)
#     blurness = np.std(difference)
    
#     return blurness, brightness, contrast, sharpness

# # Function to select the best image based on parameters
# def select_best_image(images):
#     best_image = None
#     best_score = -1

#     for img in images:
#         img_path = os.path.join(img_folder, img)
#         blurness, brightness, contrast, sharpness = measure_parameters(img_path)
        
#         # Score calculation (weights can be adjusted)
#         score = (brightness * 0.3) + (contrast * 0.3) + (sharpness * 0.3) - (blurness * 0.1)
        
#         if score > best_score:
#             best_score = score
#             best_image = img

#     return best_image

# # Streamlit app for displaying and deleting images
# def display_images_for_deletion(duplicate_groups):
#     for group in duplicate_groups:
#         st.write(f"Group: {group}")
#         cols = st.columns(len(group))
#         selected_images = []

#         for idx, img in enumerate(group):
#             img_path = os.path.join(img_folder, img)
#             image = Image.open(img_path)
#             cols[idx].image(image, caption=img, use_column_width=True)
#             if cols[idx].button(f"Delete {img}", key=img):
#                 selected_images.append(img_path)
#                 st.write(f"Selected for deletion: {img}")

#         # Move or delete the selected images
#         if st.button(f"Confirm deletion for group {group}", key=str(group)):
#             for img_path in selected_images:
#                 if os.path.exists(img_path):
#                     os.remove(img_path)
#                     st.write(f"Deleted: {img_path}")

# # Function for auto-suggesting the best image
# def auto_suggest_best_image(duplicate_groups):
#     for group in duplicate_groups:
#         best_image = select_best_image(group)
#         st.write(f"Suggested best image: {best_image} from group {group}")

#         cols = st.columns(len(group))
#         for idx, img in enumerate(group):
#             img_path = os.path.join(img_folder, img)
#             image = Image.open(img_path)
#             cols[idx].image(image, caption=img, use_column_width=True)

#         if st.button(f"Confirm auto-suggestion for group {group}", key=str(group) + "auto"):
#             for img in group:
#                 if img != best_image:
#                     img_path = os.path.join(img_folder, img)
#                     if os.path.exists(img_path):
#                         os.remove(img_path)
#                         st.write(f"Deleted: {img_path}")

# # Function to clear the image folder
# def clear_img_folder(folder):
#     for filename in os.listdir(folder):
#         file_path = os.path.join(folder, filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path)
#                 st.write(f"Deleted: {file_path}")
#             elif os.path.isdir(file_path):
#                 shutil.rmtree(file_path)
#                 st.write(f"Deleted directory: {file_path}")
#         except Exception as e:
#             st.write(f'Failed to delete {file_path}. Reason: {e}')

# # Streamlit UI
# st.title("Duplicate Image Detection and Deletion")

# st.sidebar.title("Options")
# option = st.sidebar.selectbox("Choose a method", ("Manual Deletion", "Auto Suggestion"))

# if st.sidebar.button("Clear Image Folder"):
#     clear_img_folder(img_folder)

# if option == "Manual Deletion":
#     display_images_for_deletion(duplicate_groups)
# elif option == "Auto Suggestion":
#     auto_suggest_best_image(duplicate_groups)


import numpy as np
from PIL import Image
import streamlit as st
from imagededup.methods import CNN
import cv2
import io

# Initialize the CNN encoder
myencoder = CNN()

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

# Function to measure parameters
def measure_parameters(image):
    np_image = np.array(image)
    
    # Measure brightness
    brightness = np.mean(np_image)
    
    # Measure contrast
    contrast = np.std(np_image)
    
    # Measure sharpness
    laplacian = cv2.Laplacian(np_image, cv2.CV_64F)
    sharpness = np.var(laplacian)
    
    # Measure noise (blurness)
    blurred_image = cv2.GaussianBlur(np_image, (5, 5), 0)
    difference = cv2.absdiff(np_image, blurred_image)
    blurness = np.std(difference)
    
    return blurness, brightness, contrast, sharpness

# Function to select the best image based on parameters
def select_best_image(images):
    best_image = None
    best_score = -1
    for img in images:
        blurness, brightness, contrast, sharpness = measure_parameters(img)
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
            cols[idx].image(img, use_column_width=True)
            if cols[idx].button(f"Delete", key=f"delete_{group}_{idx}"):
                selected_images.append(idx)
                st.write(f"Selected for deletion: {idx}")
        if st.button(f"Confirm deletion for group {group}", key=f"confirm_{group}"):
            for idx in selected_images:
                group.pop(idx)
                st.write(f"Deleted: {idx}")

# Function for auto-suggesting the best image
def auto_suggest_best_image(duplicate_groups):
    for group in duplicate_groups:
        best_image = select_best_image(group)
        st.write(f"Suggested best image from group")
        cols = st.columns(len(group))
        for idx, img in enumerate(group):
            cols[idx].image(img, use_column_width=True)
        if st.button(f"Confirm auto-suggestion for group {group}", key=f"auto_confirm_{group}"):
            for img in group:
                if img != best_image:
                    group.remove(img)
                    st.write(f"Deleted: {img}")

# Function to clear the image folder (In-memory this case)
def clear_img_folder():
    return []

# Streamlit UI
st.title("Duplicate Image Detection and Deletion")

st.sidebar.title("Options")
option = st.sidebar.selectbox("Choose a method", ("Manual Deletion", "Auto Suggestion"))

if st.sidebar.button("Clear Image Folder"):
    uploaded_images = clear_img_folder()

# File uploader
uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

uploaded_images = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        uploaded_images.append(image)
        st.success(f"Uploaded {uploaded_file.name}")

if option == "Manual Deletion":
    if uploaded_images:
        # Simulating image directory processing for duplicates detection
        virtual_img_folder = {str(idx): img for idx, img in enumerate(uploaded_images)}
        duplicates = myencoder.find_duplicates(virtual_img_folder, min_similarity_threshold=0.70)
        duplicate_groups = group_duplicates(duplicates)
        display_images_for_deletion(duplicate_groups)
    else:
        st.write("No images to process.")
elif option == "Auto Suggestion":
    if uploaded_images:
        # Simulating image directory processing for duplicates detection
        virtual_img_folder = {str(idx): img for idx, img in enumerate(uploaded_images)}
        duplicates = myencoder.find_duplicates(virtual_img_folder, min_similarity_threshold=0.70)
        duplicate_groups = group_duplicates(duplicates)
        auto_suggest_best_image(duplicate_groups)
    else:
        st.write("No images to process.")

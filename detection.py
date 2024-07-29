

# import numpy as np
# from PIL import Image
# import streamlit as st
# from imagededup.methods import CNN
# import cv2
# import os
# import tempfile
# from io import BytesIO

# # Initialize the CNN encoder
# myencoder = CNN()

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

# # Function to measure parameters
# def measure_parameters(image):
#     np_image = np.array(image)
    
#     # Measure brightness
#     brightness = np.mean(np_image)
    
#     # Measure contrast
#     contrast = np.std(np_image)
    
#     # Measure sharpness
#     laplacian = cv2.Laplacian(np_image, cv2.CV_64F)
#     sharpness = np.var(laplacian)
    
#     # Measure noise (blurness)
#     blurred_image = cv2.GaussianBlur(np_image, (5, 5), 0)
#     difference = cv2.absdiff(np_image, blurred_image)
#     blurness = np.std(difference)
    
#     return blurness, brightness, contrast, sharpness

# # Function to select the best image based on parameters
# def select_best_image(images):
#     best_image = None
#     best_score = -1
#     for img in images:
#         blurness, brightness, contrast, sharpness = measure_parameters(img)
#         score = (brightness * 0.3) + (contrast * 0.3) + (sharpness * 0.3) - (blurness * 0.1)
#         if score > best_score:
#             best_score = score
#             best_image = img
#     return best_image

# # Streamlit app for displaying and deleting images
# def display_images_for_deletion(duplicate_groups, img_dir):
#     for group in duplicate_groups:
#         st.write(f"Group: {group}")
#         cols = st.columns(len(group))
#         selected_images = []
#         for idx, img_name in enumerate(group):
#             img_path = os.path.join(img_dir, img_name)
#             image = Image.open(img_path)
#             cols[idx].image(image, use_column_width=True)
#             if cols[idx].button(f"Delete", key=f"delete_{group}_{idx}"):
#                 selected_images.append(img_name)
#                 st.write(f"Selected for deletion: {img_name}")
#         if st.button(f"Confirm deletion for group {group}", key=f"confirm_{group}"):
#             for img_name in selected_images:
#                 os.remove(os.path.join(img_dir, img_name))
#                 st.write(f"Deleted: {img_name}")

# # Function for auto-suggesting the best image
# def auto_suggest_best_image(duplicate_groups, img_dir):
#     for group in duplicate_groups:
#         images = [Image.open(os.path.join(img_dir, img_name)) for img_name in group]
#         best_image = select_best_image(images)
#         best_image_name = group[images.index(best_image)]
#         st.write(f"Suggested best image from group")
#         cols = st.columns(len(group))
#         for idx, img_name in enumerate(group):
#             img_path = os.path.join(img_dir, img_name)
#             image = Image.open(img_path)
#             cols[idx].image(image, use_column_width=True)
#         if st.button(f"Confirm auto-suggestion for group {group}", key=f"auto_confirm_{group}"):
#             for img_name in group:
#                 if img_name != best_image_name:
#                     os.remove(os.path.join(img_dir, img_name))
#                     st.write(f"Deleted: {img_name}")

# # Function to clear the image folder (In-memory this case)
# def clear_img_folder(img_dir):
#     for file in os.listdir(img_dir):
#         os.remove(os.path.join(img_dir, file))
#     st.write("Image folder cleared.")

# # Streamlit UI
# st.title("Duplicate Image Detection and Deletion")

# st.sidebar.title("Options")
# img_dir = tempfile.mkdtemp()
# if st.sidebar.button("Clear Image Folder"):
#     clear_img_folder(img_dir)

# # Step 1: File uploader and duplicate detection
# uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

# if uploaded_files:
#     for uploaded_file in uploaded_files:
#         file_path = os.path.join(img_dir, uploaded_file.name)
#         with open(file_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         st.success(f"Uploaded {uploaded_file.name}")

# # Detect duplicates
# if st.button("Detect Duplicates"):
#     if uploaded_files:
#         with st.spinner("Detecting duplicates..."):
#             duplicates = myencoder.find_duplicates(image_dir=img_dir, min_similarity_threshold=0.70)
#             duplicate_groups = group_duplicates(duplicates)
#             st.session_state['duplicate_groups'] = duplicate_groups
#         st.success("Duplicate detection completed.")
#     else:
#         st.write("No images to process.")

# # Step 2: Manual Deletion or Auto Suggestion
# if 'duplicate_groups' in st.session_state:
#     option = st.sidebar.selectbox("Choose a method", ("Manual Deletion", "Auto Suggestion"))

#     if option == "Manual Deletion":
#         display_images_for_deletion(st.session_state['duplicate_groups'], img_dir)
#     elif option == "Auto Suggestion":
#         auto_suggest_best_image(st.session_state['duplicate_groups'], img_dir)

import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from imagededup.methods import CNN
import cv2
import os
import tempfile
from io import BytesIO

# Initialize the CNN encoder
myencoder = CNN()

# Function to group duplicates into nested lists
def group_duplicates(duplicates_dict):
    seen = set()
    groups = []
    for key, values in duplicates_dict.items():
        if key not in seen:
            group = set(values) | {key}
            if len(group) > 1:  # Ignore single images with no duplicates
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
def display_images_for_deletion(duplicate_groups, img_dir):
    for group in duplicate_groups:
        st.write(f"Group: {group}")
        cols = st.columns(len(group))
        selected_images = []
        for idx, img_name in enumerate(group):
            img_path = os.path.join(img_dir, img_name)
            image = Image.open(img_path)
            cols[idx].image(image, use_column_width=True)
            if cols[idx].button(f"Delete", key=f"delete_{group}_{idx}"):
                selected_images.append(img_name)
                st.write(f"Selected for deletion: {img_name}")
        if st.button(f"Confirm deletion for group {group}", key=f"confirm_{group}"):
            for img_name in selected_images:
                img_path = os.path.join(img_dir, img_name)
                image = Image.open(img_path)
                grayscale_image = ImageOps.grayscale(image)
                grayscale_image.save(img_path)
            # Redisplay the images in the group
            for idx, img_name in enumerate(group):
                img_path = os.path.join(img_dir, img_name)
                image = Image.open(img_path)
                cols[idx].image(image, use_column_width=True)

# Function for auto-suggesting the best image
def auto_suggest_best_image(duplicate_groups, img_dir):
    for group in duplicate_groups:
        images = [Image.open(os.path.join(img_dir, img_name)) for img_name in group]
        best_image = select_best_image(images)
        best_image_name = group[images.index(best_image)]
        st.write(f"Suggested best image from group")
        cols = st.columns(len(group))
        for idx, img_name in enumerate(group):
            img_path = os.path.join(img_dir, img_name)
            image = Image.open(img_path)
            if img_name == best_image_name:
                cols[idx].image(image, use_column_width=True, caption="Best Image")
            else:
                cols[idx].image(image, use_column_width=True)
        # Button to delete non-best images
        if st.button(f"Delete non-best images in group {group}", key=f"delete_non_best_{group}"):
            for img_name in group:
                if img_name != best_image_name:
                    img_path = os.path.join(img_dir, img_name)
                    image = Image.open(img_path)
                    grayscale_image = ImageOps.grayscale(image)
                    grayscale_image.save(img_path)
            # Redisplay the images in the group
            for idx, img_name in enumerate(group):
                img_path = os.path.join(img_dir, img_name)
                image = Image.open(img_path)
                if img_name == best_image_name:
                    cols[idx].image(image, use_column_width=True, caption="Best Image")
                else:
                    cols[idx].image(image, use_column_width=True)

# Function to clear the image folder (In-memory this case)
def clear_img_folder(img_dir):
    for file in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, file))
    st.write("Image folder cleared.")
    st.session_state['uploaded_files'] = []

# Streamlit UI
st.title("Duplicate Image Detection and Deletion")

st.sidebar.title("Options")
img_dir = tempfile.mkdtemp()
if st.sidebar.button("Clear Image Folder"):
    clear_img_folder(img_dir)

# Step 1: File uploader and duplicate detection
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(img_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")
        st.session_state['uploaded_files'].append(uploaded_file)

# Detect duplicates
if st.button("Detect Duplicates"):
    if st.session_state['uploaded_files']:
        with st.spinner("Detecting duplicates..."):
            duplicates = myencoder.find_duplicates(image_dir=img_dir, min_similarity_threshold=0.70)
            duplicate_groups = group_duplicates(duplicates)
            st.session_state['duplicate_groups'] = duplicate_groups
        st.success("Duplicate detection completed.")
    else:
        st.write("No images to process.")

# Step 2: Manual Deletion or Auto Suggestion
if 'duplicate_groups' in st.session_state:
    option = st.sidebar.selectbox("Choose a method", ("Manual Deletion", "Auto Suggestion"))

    if option == "Manual Deletion":
        display_images_for_deletion(st.session_state['duplicate_groups'], img_dir)
    elif option == "Auto Suggestion":
        auto_suggest_best_image(st.session_state['duplicate_groups'], img_dir)

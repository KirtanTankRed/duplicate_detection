import streamlit as st
from imagededup.methods import CNN
import os
from PIL import Image

img_folder = r'https://github.com/KirtanTankRed/duplicate_detection/tree/main/images'
myencoder = CNN()
duplicates = myencoder.find_duplicates(image_dir=img_folder, min_similarity_threshold=0.70)

# Step 1: Group duplicates into nested lists
def group_duplicates(duplicates_dict):
    seen = set()
    groups = []

    for key, values in duplicates_dict.items():
        if key not in seen:
            group = set(values) | {key}
            groups.append(list(group))
            seen.update(group)
    
    return groups

duplicate_groups = group_duplicates(duplicates)

# Step 2: Streamlit app for displaying and deleting images
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

def auto_suggest_best_image(duplicate_groups):
    # Dummy function to simulate image selection
    def select_best_image(images):
        # Implement your logic for selecting the best image
        # For now, let's just return the first image
        return images[0]

    for group in duplicate_groups:
        best_image = select_best_image(group)
        st.write(f"Suggested best image: {best_image} from group {group}")

        cols = st.columns(len(group))
        for idx, img in enumerate(group):
            img_path = os.path.join(img_folder, img)
            image = Image.open(img_path)
            cols[idx].image(image, caption=img, use_column_width=True)

        if st.button(f"Confirm auto-suggestion for group {group}", key=str(group)+"auto"):
            for img in group:
                if img != best_image:
                    img_path = os.path.join(img_folder, img)
                    if os.path.exists(img_path):
                        os.remove(img_path)
                        st.write(f"Deleted: {img_path}")

# Streamlit UI
st.title("Duplicate Image Detection and Deletion")

st.sidebar.title("Options")
option = st.sidebar.selectbox("Choose a method", ("Manual Deletion", "Auto Suggestion"))

if option == "Manual Deletion":
    display_images_for_deletion(duplicate_groups)
elif option == "Auto Suggestion":
    auto_suggest_best_image(duplicate_groups)

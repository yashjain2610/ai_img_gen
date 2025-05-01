import streamlit as st
import base64
from PIL import Image
import io
from io import BytesIO
import google.generativeai as genai
from utils import *
import os
from dotenv import load_dotenv

from prompts import *

load_dotenv()

st.set_page_config(
    page_title="Gemini Vision Prompting",
    page_icon="💎",
    layout="wide"
)

st.title("💎 Gemini Vision Prompting with Image + Prompts")
st.markdown("Upload an image and input prompts to get generated text and visuals using Gemini 2.0 Flash Image Generation model")


PROMPT_LIST = [
    white_bgd_prompt,
    multicolor_1_prompt,
    multicolor_2_prompt,
    props_img_prompt,
    hand_prompt,
]
uploaded_images = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"],accept_multiple_files=True , key="up1")
generate = st.button("generate")

if "responses" not in st.session_state:
    st.session_state["responses"] = {}

if generate:
    if uploaded_images is not None:
        for uploaded_image in uploaded_images:
            image = Image.open(uploaded_image)
            filename = uploaded_image.name

            if filename not in st.session_state["responses"]:
                st.info(f"Generating for {filename} ...")
                responses = get_gemini_responses("analyse the image",image, PROMPT_LIST)
                st.session_state["responses"][filename] = responses



if uploaded_images is not None:
    for uploaded_image in uploaded_images:
        image = Image.open(uploaded_image)
        filename = uploaded_image.name

        st.markdown(f"## 🖼️ Uploaded Image: `{filename}`")
        st.image(image, caption=filename, use_container_width=300)

        if filename in st.session_state["responses"]:
            responses = st.session_state["responses"][filename]

            cols = st.columns(len(responses))

            for i, (col, item) in enumerate(zip(cols, responses)):
                try:
                    # There is always one image in item["images"]
                    img_bytes = item["images"][0]

                    gen_image = Image.open(io.BytesIO(img_bytes))
                    gen_image = resize_img(gen_image)

                    img_buffer = io.BytesIO()
                    gen_image.save(img_buffer, format="PNG")
                    resized_img_bytes = img_buffer.getvalue()

                    with col:
                        st.markdown(f"### Image Set {i+1}")  # title inside each column
                        st.image(resized_img_bytes, use_container_width=True)

                        download_col, regen_col = st.columns([1, 1])

                        with download_col:
                            st.download_button(
                                label="⬇️",
                                data=resized_img_bytes,
                                file_name=f"{filename}_prompt{i}.png",
                                mime="image/png",
                                key=f"download_{filename}_{i}"
                            )

                        with regen_col:
                            if st.button("🔁", key=f"regen_{filename}_{i}"):
                                new_response = get_gemini_responses("analyse the image", image, [PROMPT_LIST[i]])[0]
                                st.session_state["responses"][filename][i] = new_response
                                st.rerun()

                except Exception as e:
                    col.error(f"Error displaying image {i + 1}: {e}")
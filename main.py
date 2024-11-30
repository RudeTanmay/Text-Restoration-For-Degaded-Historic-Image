import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import json

def configure_genai():
    working_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(working_directory, "config.json")
    try:
        with open(config_file_path) as f:
            config_data = json.load(f)
        GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
    except FileNotFoundError:
        st.error("Config file not found. Please make sure config.json exists in the same directory as the script.")
    except json.JSONDecodeError:
        st.error("Error reading config file. Please make sure config.json is properly formatted.")
    except KeyError:
        st.error("GOOGLE_API_KEY not found in config file. Please make sure it's properly set in config.json.")

def gemini_flash_text_extraction(prompt, image):
    try:
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        response = gemini_model.generate_content([prompt, image])
        if response.parts:
            if response.parts[0].text:
                return response.parts[0].text
            else:
                return "No text was extracted from the image."
        else:
            return "The response was empty or blocked. Please try a different image or prompt."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def gemini_pro_missing_word(prompt):
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    configure_genai()
    st.set_page_config(page_title="Text Extraction & Analysis", page_icon="📚", layout='centered')
    
    st.title("📝 Text Extraction & Restoration")
    
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            image = Image.open(uploaded_image)
            resized_image = image.resize((400, 300))
            st.image(resized_image, caption="Uploaded Image")
        
        if st.button("Process Image"):
            with st.spinner("Processing..."):
                # Extract Text
                default_prompt = "Extract the text from the image. If the image is too blurred and very hard to read, then return 'Image is too noisy.'"
                extracted_text = gemini_flash_text_extraction(default_prompt, image)
                
                with col2:
                    st.subheader("📄 Extracted Text")
                    st.write(extracted_text)
                
                # Missing Word Analysis
                st.subheader("✨ Restored Text")
                context_prompt = f"Check the text for missing or unclear words and fix any typing mistakes. If no issues found, return 'Text is complete and clear' followed by the original text. Otherwise, identify missing/unclear words and provide the restored text with corrections highlighted in ** asterisks**.:'{extracted_text}'"
                restored_text = gemini_pro_missing_word(context_prompt)
                st.write(restored_text)
                
                st.subheader("🔄 Changes Made")
                changes_prompt = f"Compare the following two texts and list only the changes made (words corrected, added, or modified). Original text: '{extracted_text}' Modified text: '{restored_text}'"
                changes = gemini_pro_missing_word(changes_prompt)
                st.write(changes)

if __name__ == "__main__":
    main()
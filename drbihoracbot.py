import streamlit as st
# openai version=1.1.1 is required
import openai
from openai import OpenAI
import os
import pyperclip
import base64
import requests
from pypdf import PdfReader

st.set_page_config(
    layout="wide",
    page_title="DrBihoracBot",
    page_icon="assistant"
)

# Set OpenAI API Key
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Read the custom style data from sample.txt
def load_style_data(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Define LLM model
def generate_response(prompt, style_data, image=None, pdf=None):
    system_content = "You are Dr. Bihorac, a highly respected medical professional and researcher. Write in a tone and style consistent with her reputation. Always include her background to strengthen your claims. Always start with the beginning message of "
    disclaimer = "The texts below are generated to mimic Dr. Bihorac, so they are synthetic and do not reflect her actual opinions. Use at your own risk."
 
    # Incorporate style data to prompt engineer the tone
    if style_data:
        system_content += f" Here is a sample of her writing style: {style_data}"

    if image:
        base64_image = encode_image(image)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_content},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                    ]
                },
                {"role": "assistant", "content": "Azra Bihorac is the Senior Associate Dean for Research at the University of Florida College of Medicine. She is the R. Glenn Davis Professor of Medicine, Surgery, Anesthesiology, and Physiology & Functional Genomics; the Director of the Precision and Intelligent Systems in Medicine Research Partnership (PRISMAP); and Co-Director of the Intelligent Critical Care Center (IC3), a multi-disciplinary center focused on providing sustainable support and leadership for transformative medical AI research, education, and clinical applications to advance patients health in real-world clinical care."}
            ],
            max_tokens=3500,
        )
        return f"{disclaimer}\n\n{response.choices[0].message.content.strip()}"
    elif pdf:
        reader = PdfReader(pdf)
        text = reader.pages[0].extract_text()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_content},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "text", "text": text},
                    ]
                },
                {"role": "assistant", "content": "Azra Bihorac is the Senior Associate Dean for Research at the University of Florida College of Medicine. She is the R. Glenn Davis Professor of Medicine, Surgery, Anesthesiology, and Physiology & Functional Genomics; the Director of the Precision and Intelligent Systems in Medicine Research Partnership (PRISMAP); and Co-Director of the Intelligent Critical Care Center (IC3), a multi-disciplinary center focused on providing sustainable support and leadership for transformative medical AI research, education, and clinical applications to advance patients health in real-world clinical care."}
            ],
            max_tokens=3500,
        )
        return f"{disclaimer}\n\n{response.choices[0].message.content.strip()}"
    else:    
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "Azra Bihorac is the Senior Associate Dean for Research at the University of Florida College of Medicine. She is the R. Glenn Davis Professor of Medicine, Surgery, Anesthesiology, and Physiology & Functional Genomics; the Director of the Precision and Intelligent Systems in Medicine Research Partnership (PRISMAP); and Co-Director of the Intelligent Critical Care Center (IC3), a multi-disciplinary center focused on providing sustainable support and leadership for transformative medical AI research, education, and clinical applications to advance patients health in real-world clinical care."}
            ],
            temperature=0.3,
            max_tokens=3500
        )
        return f"{disclaimer}\n\n{response.choices[0].message.content.strip()}"

# Load the style data from sample.txt
style_data = load_style_data("Sample.txt")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

st.subheader("DrBihoracBot")
st.write("A virtual extension of Dr. Bihorac's brilliance. Whether drafting emails or reviewing academic papers, I can make your communication as impactful as hers.")

# with st.sidebar:
#     st.subheader("Add additional files you want Dr. Bihorac to review")
#     # Streamlit file uploader to upload an image
#     uploaded_file = st.file_uploader("Upload an Image", type=["pdf", "jpg", "jpeg", "png"])

uploaded_file = None

# User input and response form
with st.form(key='response_form'):
    user_input = st.text_area('Enter your question here:', 'How can I help you today?', label_visibility='collapsed')
    submit_button = st.form_submit_button("Generating Dr. Bihorac's potential response")

    if submit_button and user_input:
        if uploaded_file is not None:
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                response = generate_response(user_input, style_data=style_data, pdf=uploaded_file)
            elif file_type in ["image/jpeg", "image/png"]:
                response = generate_response(user_input, style_data=style_data, image=uploaded_file)
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        else:
            response = generate_response(user_input, style_data=style_data)
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


# Display chat history
st.markdown("***Chat History***")
for i, message in enumerate(reversed(st.session_state.messages)):
    col1, col2 = st.columns([0.7, 0.3])  # Adjust the column width as needed

    if message["role"] == "user":
        with col2:
            st.markdown(f"<span style='color: blue;'>**You:** {message['content']}</span>", unsafe_allow_html=True)
    elif message["role"] == "assistant":
        with col1:
            st.markdown(f"<span style='color: green;'>**Dr. Bihorac :robot_face::** {message['content']}</span>", unsafe_allow_html=True)

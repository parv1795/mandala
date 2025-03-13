import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import openai  # ✅ Fixed Import

# Set page configuration
st.set_page_config(
    page_title="Mandala Art Generator",
    page_icon="🔮",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .title {
        font-size: 42px;
        font-weight: bold;
        color: #3a3a3a;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 22px;
        color: #555555;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #ff3333;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<p class="title">Mandala Art Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform a single word into a beautiful mandala pattern</p>', unsafe_allow_html=True)

# Sidebar for API key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    st.caption("Your API key is not stored and is only used for this session")
    
    st.markdown("---")
    with st.expander("📝 How It Works"):
        st.write("""
        1. Enter your OpenAI API key in the sidebar
        2. Type a single word that represents a concept, emotion, or element
        3. Click Generate to create a unique mandala art
        4. Download your custom mandala image for personal use
        
        The mandala will have a white background and symmetrical patterns inspired by your input word.
        """)

# Initialize session state for generated image
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

def generate_mandala(prompt_word, api_key):
    """Generate mandala art using OpenAI's DALL·E 3 based on a single word"""
    
    client = openai.Client(api_key=api_key)  # ✅ Fixed OpenAI Client Initialization

    enhanced_prompt = f"Create a detailed symmetrical mandala art based on the concept of '{prompt_word}'. The mandala should have intricate patterns, be centered in the image, and have a pure white background. Make it visually striking with detailed ornamental elements."

    try:
        response = client.images.generate(  # ✅ Updated OpenAI API Call
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json"
        )

        # Debugging: Show API response on Streamlit Cloud
        st.write("OpenAI API Response:", response)

        # Decode base64 image
        image_data = base64.b64decode(response.data[0].b64_json)
        image = Image.open(BytesIO(image_data))
        return image, None
    except Exception as e:
        st.error(f"❌ OpenAI API Error: {str(e)}")  # ✅ Debugging OpenAI Errors
        return None, str(e)

def get_image_download_link(img, filename, text):
    """Generate a link to download the PIL image"""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}.png">{text}</a>'
    return href

# Input section
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt_word = st.text_input("Enter a word for your mandala:", placeholder="e.g., ocean, harmony, forest...")
    
    with col2:
        generate_button = st.button("Generate", use_container_width=True)

# Generate mandala when button is clicked
if generate_button:
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
    elif not prompt_word:
        st.warning("Please enter a word to generate a mandala")
    else:
        with st.spinner(f"Creating your '{prompt_word}' mandala..."):
            image, error = generate_mandala(prompt_word, api_key)
            
            if error:
                st.error(f"Error generating mandala: {error}")
            else:
                # Store the generated image in session state
                st.session_state.generated_image = image
                st.session_state.prompt_word = prompt_word
                
# Display the generated image if available
if st.session_state.generated_image:
    st.image(
        st.session_state.generated_image, 
        caption=f"Mandala inspired by '{st.session_state.prompt_word}'", 
        use_container_width=True
    )
    
    # Add download button
    st.markdown(
        get_image_download_link(
            st.session_state.generated_image, 
            f"mandala_{st.session_state.prompt_word}", 
            "⬇️ Download Mandala"
        ),
        unsafe_allow_html=True
    )
    
    st.success("Your mandala has been created! Click the link above to download.")

# Add a footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and DALL-E 3")

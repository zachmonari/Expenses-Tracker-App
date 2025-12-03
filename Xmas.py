import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
#from streamlit_extras.emoji import emoji
from PIL import Image

logo=Image.open("ZachTechs.jpg")
st.image(logo, width=150)

# Page settings
st.set_page_config(page_title="Merry Christmas 🎄", layout="centered")

# Background Image CSS
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://images.unsplash.com/photo-1606925797303-0c49b1e9c31d");
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Snow animation
rain(
    emoji="❄️",
    font_size=30,
    falling_speed=5,
    animation_length="infinite"
)

# Autoplay background music
st.markdown("""
<audio autoplay loop>
    <source src="https://files.freemusicarchive.org/storage-freemusicarchive-org/tracks/hXKyYVJY0F4j00Uv.mp3" type="audio/mp3">
</audio>
""", unsafe_allow_html=True)

# Header
colored_header(
    label="🎄 Merry Christmas & Happy Holidays 🎁",
    description="A little gift of love, joy and warm wishes for you ❤️",
    color_name="red-70",
)

# Personalized message
st.write("""
### Dear Candy,  
This season reminds me of how blessed I am to have you in my life.  
Thank you for your love, joy, support, and presence.  
May this Christmas fill your heart with peace and your home with warmth.  

**Wishing you endless happiness, laughter, and magical moments.**  
With love 🎅❤️  
""")

# Image gallery
st.subheader("✨ Our Beautiful Memories")
cols = st.columns(3)
images = [
    "https://images.unsplash.com/photo-1543007630-9710e4a00a20",
    "https://images.unsplash.com/photo-1519681393784-d120267933ba",
    "https://images.unsplash.com/photo-1581287053822-41dff00b7d3a"
]
for i, col in enumerate(cols):
    col.image(images[i], use_container_width=True)
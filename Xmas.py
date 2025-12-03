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
    "Nature1.jpg",
    "Nature2.jpg",
    "Nature3.jpg"

]
st.write("One of the best days in our lives ️❤️️")
for i, col in enumerate(cols):
    col.image(images[i], width="stretch")
#Song
st.audio("PerfectEd.mp3", format="audio/wav", loop=False)
# Love notes section
st.subheader("💌 Little Notes for You")
notes = [
    "You make my world brighter ✨",
    "Thank you for being you ❤️",
    "Every day with you is special 🎁",
    "You are my favourite human 💕"
]
note = st.selectbox("Choose a note:", notes)
st.success(note)

# Gift reveal
st.subheader("🎁 Your Christmas Gift")
if st.button("Click to Open Your Gift"):
    st.balloons()
    st.write("### 🎉 Surprise! You deserve all the joy in the world!")
    st.image("https://images.unsplash.com/photo-1513639725746-c5d3e861f32a")


st.markdown("---")
st.caption("© Xmas App™ | Developed in Python with ❤️ and Streamlit")
st.caption("@ Zach Techs 2025")
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
#from streamlit_extras.emoji import emoji
from PIL import Image

logo=Image.open("ZachTechs.jpg")
st.image(logo, width=300)

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
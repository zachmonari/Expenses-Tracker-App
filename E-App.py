import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import io
import os
from PIL import Image

#Logo
logo=Image.open("ZachTechs.jpg")
st.image(logo, width=150)

# Page configuration
st.set_page_config(
    page_title="Personal Expenses Tracker",
    page_icon="💰",
    layout="wide"
)
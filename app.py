import streamlit as st
import os
import io
import re
from collections import Counter
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from google.cloud import vision
from pydrive.auth import GoogleAuth
from heatmap import create_heatmap

IMAGES_TEXT_PATH = "image_text.csv"


def main():
    st.title("Gym Locker Assignment Analysis")

    heatmap_data = create_heatmap(IMAGES_TEXT_PATH)
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, cmap="YlOrRd")
    plt.title("Locker Usage Heatmap")
    plt.xlabel("Locker Number")
    plt.ylabel("Row")
    st.pyplot(plt)


if __name__ == "__main__":
    main()

import os

import requests
import streamlit as st
from starlette.status import HTTP_401_UNAUTHORIZED

st.set_page_config(
    page_title="guide-dog-poc",
    page_icon="../../images/logo_guide_dog.png",
    layout=None,
    initial_sidebar_state=None,
    menu_items=None,
)

# title and logo
title_col1, title_col2 = st.columns([1, 5])
title_col1.image("../../images/logo_guide_dog.png", width=90)
title_col2.title("Guide Dog: A vibe-coded PoC")

st.subheader("Login")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if os.getenv("DEBUG"):
    st.session_state.logged_in = True
    st.session_state.api_key = "my_debug_key"
    st.switch_page("pages/detection.py")

with st.form("Login"):
    api_key = st.text_input("Enter your API key", type="password")
    if st.form_submit_button("Submit"):
        st.session_state.api_key = api_key

        # Test that api_key works
        st.session_state["page_url"] = "http://127.0.0.1:8000"  # TODO adapt as soon as online deployment exists
        response = requests.get(f"{st.session_state.page_url}/camera", headers={"X-Api-Key": st.session_state.api_key})

        if response.status_code != HTTP_401_UNAUTHORIZED:
            st.session_state.logged_in = True
            st.switch_page("pages/detection.py")
        else:
            st.session_state.logged_in = False
            st.write(f':red[{"Wrong API key. Please try again."}]')

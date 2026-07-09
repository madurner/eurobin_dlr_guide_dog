#!/bin/bash

echo "Changing directory to application/streamlit_frontend/..."
cd ../application/streamlit_frontend/ || { echo "Failed to change directory"; exit 1; }

echo "Running Streamlit app..."
# streamlit run run_streamlit.py
DEBUG=true streamlit run run_streamlit.py

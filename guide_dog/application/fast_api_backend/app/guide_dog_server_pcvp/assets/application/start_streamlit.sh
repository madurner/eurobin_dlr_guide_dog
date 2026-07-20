#!/usr/bin/env bash

set -e

DEBUG_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        *)
            echo "Usage: $0 [--debug]"
            exit 1
            ;;
    esac
done

if [ ! -f ./conan_env/conanrun.sh ]; then
    echo "conanrun.sh script not found. Install conan env...!"
    conan2 install conanfile.txt \
        --output-folder conan_env \
        --profile:host="$DLRRM_HOST_PLATFORM" \
        --profile:build="$DLRRM_HOST_PLATFORM" \
        --build=missing
fi

source conan_env/conanrun.sh

cd streamlit_frontend/ || exit

if $DEBUG_MODE; then
    export DEBUG=true
    echo "Running Streamlit app (DEBUG mode)..."
else
    echo "Running Streamlit app..."
fi

streamlit run run_streamlit.py

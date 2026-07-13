import base64
import json
from io import BytesIO

import cv2
import numpy as np
import requests
import streamlit as st
from PIL import Image
from streamlit.elements.lib.mutable_status_container import StatusContainer

# Initialize session state
if "page_url" not in st.session_state:
    st.session_state.page_url = "http://127.0.0.1:8000"


def get_url(page):
    return f"{st.session_state.page_url}/{page}"


def set_pipeline_status(status_widget: StatusContainer, state: str):
    if state == "ready":
        st.session_state.pipeline_status = "complete"
        st.session_state.pipeline_label = ":dog: Up and ready"
        st.session_state.pipeline_starting = False
    elif state == "stopped":
        st.session_state.pipeline_status = "error"
        st.session_state.pipeline_label = ":stop_sign: Stopped"
        st.session_state.pipeline_starting = False
    elif state == "loading":
        st.session_state.pipeline_status = "running"
        st.session_state.pipeline_label = "⏳ Loading modules... "
        st.session_state.pipeline_starting = True
    elif state == "error":
        # Keep "Not started" label if we haven't explicitly started the pipeline
        # Keep loading label if we're in the process of starting
        if ":hourglass_flowing_sand: Not started" in st.session_state.pipeline_label:
            st.session_state.pipeline_status = "error"
            # Keep "Not started" label - don't change it
        elif "⏳ Loading modules..." in st.session_state.pipeline_label or st.session_state.pipeline_starting:
            st.session_state.pipeline_status = "running"
            # Keep the loading label and keep starting state
            st.session_state.pipeline_starting = True
        else:
            st.session_state.pipeline_status = "error"
            st.session_state.pipeline_label = ":stop_sign: Stopped"
            st.session_state.pipeline_starting = False
    else:
        # Fallback for other states
        st.session_state.pipeline_status = state
        st.session_state.pipeline_label = f":question: {state}"
        st.session_state.pipeline_starting = False
    # Update with expanded=False to keep the status compact
    status_widget.update(label=st.session_state.pipeline_label, expanded=False, state=st.session_state.pipeline_status)


@st.fragment
def create_camera_parameter_form():
    # camera params state
    current_camera = None
    f_x = None
    f_y = None
    pp_u = None
    pp_v = None
    width = None
    height = None
    response = requests.get(get_url("camera"), headers={"X-Api-Key": st.session_state.api_key})
    if response.ok:
        current_camera = response.json()["camera"]["camera_name"]
        f_x = response.json()["camera"]["intrinsics"]["focal_length_x"]
        f_y = response.json()["camera"]["intrinsics"]["focal_length_y"]
        pp_u = response.json()["camera"]["intrinsics"]["principal_point_x"]
        pp_v = response.json()["camera"]["intrinsics"]["principal_point_y"]
        width = response.json()["camera"]["intrinsics"]["image_width"]
        height = response.json()["camera"]["intrinsics"]["image_height"]

    page_left_form = st.form("camera params")
    camera_name = page_left_form.text_input(label=f"camera_name: {current_camera}", value=current_camera)

    col1, col2 = page_left_form.columns([1, 1])
    f_x = col1.number_input(label=f"fx: {f_x}", value=f_x, format="%.3f")
    pp_u = col1.number_input(label=f"ppu: {pp_u}", value=pp_u, step=1, format="%i")
    width = col1.number_input(label=f"width: {width}", value=width, step=1, format="%i")

    f_y = col2.number_input(label=f"fy: {f_y}", value=f_y, format="%.3f")
    pp_v = col2.number_input(label=f"ppv: {pp_v}", value=pp_v, step=1, format="%i")
    height = col2.number_input(label=f"height: {height}", value=height, step=1, format="%i")

    if page_left_form.form_submit_button("Set camera parameters", width="stretch"):
        camera_dict = {
            "principal_point_x": pp_u,
            "principal_point_y": pp_v,
            "focal_length_x": f_x,
            "focal_length_y": f_y,
            "image_width": width,
            "image_height": height,
        }
        camera_post_response = requests.post(
            get_url("camera"),
            data=json.dumps({"camera_name": camera_name, "intrinsics": camera_dict}, indent=4),
            headers={"X-Api-Key": st.session_state.api_key, "Content-Type": "application/json"}
        )

        if not camera_post_response.ok:
            st.write(f":red[{camera_post_response.json()}]")
        else:
            st.rerun()


@st.fragment
def select_pcvp_modules():
    """Radio buttons to select which PCVP pipeline to start."""

    # Available pipeline options
    pipeline_options = {
        "Empty": [],
        "Yolov7, DensePose": ["yolov7", "dense_pose"],
        "Yolov7, DensePose, M3T Refiner": ["yolov7", "dense_pose", "m3t_refiner_cpp"],
    }

    # Get current selection from session state, default to "Empty"
    current_selection = st.session_state.get("selected_pcvp_pipeline", "Empty")

    # Create radio buttons for pipeline selection
    selected_label = st.radio(
        "Choose which modules to load:",
        options=list(pipeline_options.keys()),
        index=list(pipeline_options.keys()).index(current_selection) if current_selection in pipeline_options else 0,
        key="pcvp_module_selection",
    )

    # Store the selected modules in session state
    st.session_state.selected_pcvp_pipeline = selected_label
    st.session_state.pcvp_modules = pipeline_options[selected_label]


@st.fragment
def manage_pcvp_pipeline():
    # Check if fragment needs initialization (key doesn't exist or is False)
    state_init = st.session_state.get("pipeline_state_initialized", False)
    if not state_init:
        st.session_state.pipeline_status = "error"
        st.session_state.pipeline_label = ":hourglass_flowing_sand: Not started"
        st.session_state.pipeline_state_initialized = True
        st.session_state.pipeline_starting = False
    # Use default expanded state so label is visible
    with st.status(st.session_state.pipeline_label, state=st.session_state.pipeline_status) as status:
        r = requests.get(get_url("pipeline"), headers={"X-Api-Key": st.session_state.api_key})
        if r.ok:
            set_pipeline_status(status_widget=status, state=r.json()["state"])

        # create start/stop controls based on current state
        col1, col2 = st.columns([1, 1])

        # Check if we're in the process of starting (loading state)
        # Use pipeline_starting flag to detect loading state
        is_starting = st.session_state.pipeline_starting

        # Disable Start button if we're starting or already running/ready
        if not is_starting and st.session_state.pipeline_status not in ["running", "complete"]:
            button_key = "start_pipeline_button"
            if col1.button("Start pipeline!", key=button_key, width="content"):
                # Button was clicked - set state to prevent re-clicks during loading
                st.session_state.pipeline_starting = True
                set_pipeline_status(status_widget=status, state="loading")
                # Update the status widget immediately to show loading state
                status.update(label=st.session_state.pipeline_label, state=st.session_state.pipeline_status)
                # Include selected pcvp_modules in the request body
                modules_to_load = st.session_state.get("pcvp_modules", [])
                r = requests.post(
                    get_url("pipeline"),
                    headers={"X-Api-Key": st.session_state.api_key, "Content-Type": "application/json"},
                    json={"pcvp_modules": modules_to_load},
                )
                if r.ok:
                    set_pipeline_status(status_widget=status, state=r.json()["state"])
                    # Force immediate re-run to update UI and show detection page
                    st.rerun()
                else:
                    # Show error message from API
                    error_msg = "Pipeline startup failed"
                    try:
                        error_detail = r.json().get("detail", {})
                        if isinstance(error_detail, dict):
                            error_msg = error_detail.get("message", error_msg)
                        else:
                            error_msg = str(error_detail)
                    except (ValueError, AttributeError):
                        pass
                    st.error(f"⚠️ {error_msg}")
                    set_pipeline_status(status_widget=status, state="error")
        else:
            # Only show Stop button if pipeline is running or ready
            if st.session_state.pipeline_status in ["running", "complete"]:
                if col2.button("Stop pipeline!", width="content"):
                    r = requests.delete(get_url("pipeline"), headers={"X-Api-Key": st.session_state.api_key})
                    if r.ok:
                        set_pipeline_status(status_widget=status, state=r.json()["state"])
                        # Force immediate re-run to update UI
                        st.rerun()
                    else:
                        st.error("⚠️ Failed to stop pipeline")
                        set_pipeline_status(status_widget=status, state="error")
                        # Force immediate re-run to update UI
                        st.rerun()


@st.fragment
def draw_image():
    r = requests.get(get_url("image"), headers={"X-Api-Key": st.session_state.api_key})
    if r.ok:
        load_bytes = BytesIO(base64.b64decode(r.json()["image_base64"]))
        loaded_np = np.load(load_bytes, allow_pickle=True)
        st.image(Image.fromarray(loaded_np), width="content")


# if not logged in - redirect to login page
if "logged_in" not in st.session_state:
    st.error("Please log in first")
    st.switch_page("run_streamlit.py")
    st.stop()
elif not st.session_state.logged_in:
    st.error("Please log in first")
    st.switch_page("run_streamlit.py")
    st.stop()

# Initialize pipeline state if not set
# Use "error" to indicate not started (different from "complete" which indicates running)
if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = "error"
if "pipeline_label" not in st.session_state:
    st.session_state.pipeline_label = ":hourglass_flowing_sand: Not started"
if "pipeline_state_initialized" not in st.session_state:
    st.session_state.pipeline_state_initialized = True
# Track if we're in the middle of starting the pipeline
if "pipeline_starting" not in st.session_state:
    st.session_state.pipeline_starting = False
# PCVP module selection
if "selected_pcvp_pipeline" not in st.session_state:
    st.session_state.selected_pcvp_pipeline = "Empty"
if "pcvp_modules" not in st.session_state:
    st.session_state.pcvp_modules = []

# Generate detection page
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

# PCVP Pipeline Management
st.subheader("PCVP pipeline")
# select_pcvp_modules()
manage_pcvp_pipeline()

## Start generating the page
page_left, page_right = st.columns([4, 4])

## Camera initialization
page_left.subheader("Setup camera")

page_left.write("Please enter your camera parameters:")
# intrinsics
with page_left:
    create_camera_parameter_form()

## Image setup
page_right.subheader("Image upload")
uploaded_image = page_right.file_uploader("Upload an image", type=["jpg", "png"], accept_multiple_files=False)

page_right_col1, page_right_col2 = page_right.columns([1, 1])

if page_right_col1.button(":red[Delete image]", width="stretch"):
    r = requests.delete(get_url("image"), headers={"X-Api-Key": st.session_state.api_key})
if page_right_col2.button(":blue[Upload image]", width="stretch"):
    if uploaded_image is not None:
        # To read file as bytes as complex as possible :D
        # Convert uploaded file to OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        debug_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        debug_image = cv2.cvtColor(debug_image, cv2.COLOR_BGR2RGB)

        # Save to BytesIO
        bytes_data = BytesIO()
        np.save(bytes_data, debug_image, allow_pickle=True)
        r = requests.post(
            get_url("image"),
            data={"msg": "Uploaded image with streamlit.", "content_type": "multipart/form-data"},
            files={"file": bytes_data.getvalue()},
            headers={"X-Api-Key": st.session_state.api_key},
        )
        if not r.ok:
            page_right.write(f":red[{r.text}]")

# Fetch current image from server
container_image = page_right.container()
container_image.empty()
with container_image:
    draw_image()

## Detection
st.subheader("PCVP Detection")
if st.button("Detect!", width="stretch"):
    r = requests.get(get_url("pipeline"), headers={"X-Api-Key": st.session_state.api_key})
    with st.spinner(text="Running detection...", show_time=False, width="content"):
        r = requests.get(get_url("detection"), data={}, headers={"X-Api-Key": st.session_state.api_key})
    if r.ok:
        st.write(f':green[{r.json()["message"]}]')
        detection_result = {"class": list(), "instance_id": list(), "pose": list()}
        for result in r.json()["result"]:
            detection_result["class"].append(str(result["class_name"]))
            detection_result["instance_id"].append(str(result["instance_id"]))
            np.set_printoptions(precision=3)  # needed for pretty print
            pose_string = f'{np.array(result["pose_6dof"]).reshape(4, 4)}'
            detection_result["pose"].append(pose_string)

        st.dataframe(
            detection_result,
            column_config={
                "class": "class label",
                "instance_id": "instance id",
                "pose": st.column_config.Column(
                    "6D pose",
                    help="The object's 6D pose in the camera frame",
                ),
            },
            hide_index=True,
        )
        # get Image
        load_bytes = BytesIO(base64.b64decode(r.json()["image_base64"]))
        loaded_np = np.load(load_bytes, allow_pickle=True)
        st.image(Image.fromarray(loaded_np), width="content")
    else:
        st.write(f':red[Error: {r.json()["detail"]}]')

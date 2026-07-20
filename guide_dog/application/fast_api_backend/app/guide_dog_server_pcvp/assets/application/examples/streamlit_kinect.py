import asyncio
from datetime import datetime
from io import BytesIO

import cv2
import numpy as np
import requests
import streamlit as st
from pyk4a import ColorResolution, Config, DepthMode, ImageFormat, PyK4A

QUEUE_SIZE = 10
API_URL = "https://your-api-endpoint.com/upload"


def get_url(page):
    return f"http://10.97.1.120:8000/{page}"
    # return f'http://rmc-lx0545:8000/{page}'


# -------------------------------------------------
# Initialize Azure Kinect once
# -------------------------------------------------
if "k4a" not in st.session_state:
    config = Config(
        color_format=ImageFormat.COLOR_BGRA32,
        color_resolution=ColorResolution.RES_720P,
        depth_mode=DepthMode.NFOV_UNBINNED,
        synchronized_images_only=True,
    )
    k4a = PyK4A(config)
    k4a.start()
    st.session_state.k4a = k4a

k4a = st.session_state.k4a


# -------------------------------------------------
# Producer
# -------------------------------------------------
async def produce_frames(queue, delay):
    while True:
        await asyncio.sleep(delay)

        capture = k4a.get_capture()
        if capture.color is not None:
            frame = cv2.cvtColor(capture.color, cv2.COLOR_BGRA2RGB)

            # Keep only latest frame (low latency mode)
            while not queue.empty():
                _ = queue.get_nowait()

            await queue.put(frame)
            st.session_state.produced_frames += 1


# -------------------------------------------------
# Consumer
# -------------------------------------------------
async def consume_frames(image_placeholder, queue_info_placeholder, queue, delay):
    while True:
        await asyncio.sleep(delay)

        if not queue.empty():
            frame = await queue.get()

            # Save latest frame globally for API call
            st.session_state.latest_frame = frame

            image_placeholder.image(
                frame,
                channels="RGB",
                caption=f"Displayed: {st.session_state.consumed_frames} | {datetime.now()}",
                width=700,
            )

            queue_info_placeholder.metric("Queue size", queue.qsize())

            st.session_state.consumed_frames += 1
            queue.task_done()


def convert_image_content_to_base64(image: np.ndarray) -> str:
    np_bytes = BytesIO()
    np.save(np_bytes, image, allow_pickle=True)
    return np_bytes.getvalue()


# -------------------------------------------------
# Async API Call (Non-Blocking)
# -------------------------------------------------
async def send_to_api(frame):
    def post_request():
        # _, img_bytes = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        # img_bytes = base64.b64encode(img_bytes).decode("utf-8")

        img_bytes = convert_image_content_to_base64(frame)

        r = requests.post(
            get_url("image"),
            data={"msg": "Uploaded image with streamlit.", "content_type": "multipart/form-data"},
            files={"file": img_bytes},
            headers={"X-Api-Key": "my_secret_key"},
            timeout=10,
        )
        return r

    try:
        response = post_request()

        # response = await asyncio.to_thread(post_request)
        return response.status_code
    except Exception as e:
        return str(e)


# -------------------------------------------------
# Run async tasks
# -------------------------------------------------
async def run_app(image_placeholder, queue_info_placeholder, queue, produce_delay, consume_delay):
    await asyncio.gather(
        produce_frames(queue, produce_delay),
        consume_frames(image_placeholder, queue_info_placeholder, queue, consume_delay),
    )


# -------------------------------------------------
# STREAMLIT APP
# -------------------------------------------------
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("Azure Kinect Async Stream + API Capture")

    # Persistent event loop
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

    if "queue" not in st.session_state:
        st.session_state.queue = asyncio.Queue(QUEUE_SIZE)
        st.session_state.produced_frames = 0
        st.session_state.consumed_frames = 0
        st.session_state.latest_frame = None
        st.session_state.api_result = None

    produce_delay = 1 / st.sidebar.slider("Capture FPS", 1, 30, 15)
    consume_delay = 1 / st.sidebar.slider("Display FPS", 1, 30, 15)

    col1, col2 = st.columns(2)
    image_placeholder = col1.empty()
    queue_info_placeholder = col2.empty()

    # 🚀 Capture button
    if st.button("Capture & Send to API"):
        if st.session_state.latest_frame is not None:
            st.info("Sending image to API...")
            status = asyncio.run(send_to_api(st.session_state.latest_frame))
            st.session_state.api_result = status
        else:
            st.warning("No frame available yet.")

    if st.session_state.api_result is not None:
        st.success(f"API Response: {st.session_state.api_result}")

    asyncio.run(
        run_app(
            image_placeholder,
            queue_info_placeholder,
            st.session_state.queue,
            produce_delay,
            consume_delay,
        )
    )

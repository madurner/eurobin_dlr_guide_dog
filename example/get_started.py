"""
Example client for the SocRob FastAPI backend.

This example demonstrates how to:

1. Check the image endpoint
2. Configure camera intrinsics
3. Upload an image
4. Request object detections

"""

from io import BytesIO
import json
from pathlib import Path

import cv2
import numpy as np
import requests


# =============================================================================
# Configuration
# =============================================================================

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "socrob_tests"

IMAGE_PATH = Path(
    "/home/schi_f0/testing/eurobin_dlr_guide_dog/guide_dog/application/fast_api_backend/app/images/cheezit_color_image.png"
   )


# =============================================================================
# API Client
# =============================================================================

class SocRobClient:
    """Simple client for communicating with the SocRob FastAPI backend."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-Api-Key": api_key}

    def url(self, endpoint: str) -> str:
        """Build a URL for a backend endpoint."""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def check_image_endpoint(self) -> None:
        """Check whether the image endpoint is reachable."""
        response = requests.get(
            self.url("image"),
            headers=self.headers,
        )

        #response.raise_for_status()
        print("OK - API is reachable")

    def set_camera(self) -> None:
        """Configure the camera intrinsics."""

        camera_intrinsics = {
            "principal_point_x": 961,
            "principal_point_y": 530,
            "focal_length_x": 936.0,
            "focal_length_y": 936.0,
            "image_width": 1920,
            "image_height": 1060,
        }

        camera_data = {
            "camera_name": "its_me_Camera",
            "intrinsics": camera_intrinsics,
        }

        response = requests.post(
            self.url("camera"),
            json=camera_data,
            headers=self.headers,
        )

        response.raise_for_status()
        print("OK - camera intrinsics configured")

    def upload_image(self, image_path: Path) -> None:
        """Load an image and upload it as a NumPy stream."""

        if not image_path.exists():
            raise FileNotFoundError(f"Image does not exist: {image_path}")

        # OpenCV loads images in BGR format.
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

        if image is None:
            raise RuntimeError(f"Could not read image: {image_path}")

        # Convert BGR to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Serialize the NumPy array into an in-memory byte stream.
        image_stream = BytesIO()
        np.save(image_stream, image, allow_pickle=False)

        metadata = {
            "msg": "Uploaded image from example script.",
            "content_type": "application/octet-stream",
        }

        response = requests.post(
            self.url("image"),
            data=metadata,
            files={
                "file": (
                    "image.npy",
                    image_stream.getvalue(),
                    "application/octet-stream",
                )
            },
            headers=self.headers,
        )

        response.raise_for_status()
        print("OK - image uploaded")

    def get_detections(self) -> dict:
        """Request object detections from the backend."""

        response = requests.get(
            self.url("detection"),
            headers=self.headers,
        )

        response.raise_for_status()

        detections = response.json()

        print("OK - received detection result")
        print(json.dumps(detections, indent=4))

        return detections


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    """Run the complete example."""

    client = SocRobClient(
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    try:
        print("\n--- Check API ---")
        client.check_image_endpoint()

        print("\n--- Configuring camera ---")
        client.set_camera()

        print("\n--- Uploading image ---")
        client.upload_image(IMAGE_PATH)

        print("\n--- Requesting detections ---")
        detections = client.get_detections()

        print("\nDetection result:")
        print(detections)

    except requests.HTTPError as error:
        print(f"\nHTTP error: {error}")

        if error.response is not None:
            print(f"Backend response: {error.response.text}")

    except Exception as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()



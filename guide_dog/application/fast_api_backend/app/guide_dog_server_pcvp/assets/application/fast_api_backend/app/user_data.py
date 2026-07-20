import asyncio
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Annotated, Optional, Union

import cv2
import numpy as np
from auth import get_ln_manager_address_from_key, handle_api_key
from fastapi import Depends
from guide_dog_server_pcvp.guide_dog_server import GuideDogServerPCVP
from ln_runner.main import LNRunner
from pydantic_models import Camera, Image, Intrinsics


@dataclass
class UserData:
    ln_manager_address: str = ""
    ln_manager_runner: Union[LNRunner, None] = None
    current_camera: Union[Camera, None] = None
    current_image: Union[Image, None] = None
    guide_dog_server: Union[GuideDogServerPCVP, None] = None
    path_to_workspace: Union[str, None] = None


def initialize_debug_user():
    debug_data = UserData()
    debug_data.path_to_workspace = "/tmp/guide_dog_debug_ws/"
    if not os.path.exists(debug_data.path_to_workspace):
        os.makedirs(debug_data.path_to_workspace)
    debug_image = cv2.imread("./images/cheezit_color_image.png")
    debug_image = cv2.cvtColor(debug_image, cv2.COLOR_BGR2RGB)
    np_bytes = BytesIO()
    np.save(np_bytes, debug_image, allow_pickle=True)
    debug_data.current_image = Image(file_name="debug_image", content=np_bytes.getvalue())
    debug_data.current_camera = Camera(
        camera_name="debug_camera",
        intrinsics=Intrinsics(
            image_width=1920,
            image_height=1080,
            focal_length_x=936.24,
            focal_length_y=936.75,
            principal_point_x=961,
            principal_point_y=529,
        ),
    )
    debug_data.ln_manager_address = "localhost:21112"
    debug_data.ln_manager_runner = LNRunner(debug_data.ln_manager_address)
    debug_data.guide_dog_server = GuideDogServerPCVP(debug_data.ln_manager_address)
    return debug_data


map_user_to_data: dict[str, UserData] = {"my_debug_key": initialize_debug_user()}


def get_user_data(key: Annotated[str, Depends(handle_api_key)]):
    global map_user_to_data
    if key not in map_user_to_data.keys():
        print(f"Create new user {key}")
        ln_manager_address = get_ln_manager_address_from_key(key)
        map_user_to_data[key] = UserData(
            ln_manager_address, LNRunner(ln_manager_address), None, None, GuideDogServerPCVP(ln_manager_address), None
        )
    return map_user_to_data[key]


def get_user_image(user_data: Annotated[UserData, Depends(get_user_data)]):
    return user_data.current_image


def set_user_image(image: Image, key: str):
    global map_user_to_data
    map_user_to_data[key].current_image = image


def delete_user_image(key: str):
    global map_user_to_data
    map_user_to_data[key].current_image = None


def get_user_camera(user_data: Annotated[UserData, Depends(get_user_data)]):
    return user_data.current_camera


def set_user_camera(camera: Camera, key: str):
    global map_user_to_data
    map_user_to_data[key].current_camera = camera


def update_user_camera(new_intrinsics: Intrinsics, key: str):
    global map_user_to_data
    map_user_to_data[key].current_camera.intrinsics = new_intrinsics
    return True


def get_guide_dog_connection(user_data: Annotated[UserData, Depends(get_user_data)]):
    return user_data.guide_dog_server


def stop_guide_dog_server(key: str):
    map_user_to_data[key].guide_dog_server.is_running = False


def get_ln_manager_runner(user_data: Annotated[UserData, Depends(get_user_data)]):
    return user_data.ln_manager_runner


async def create_and_start_pipeline(key: str, pcvp_modules: Optional[list[str]] = None, timeout: float = 60.0):
    """
    Create and start the PCVP pipeline with a timeout.

    Args:
        key: API key for user data
        pcvp_modules: List of optional PCVP modules to load
        timeout: Maximum time to wait for pipeline startup in seconds (default: 60)

    Returns:
        True on success

    Raises:
        TimeoutError: If pipeline startup takes longer than timeout
    """
    user_data = get_user_data(key)
    if user_data.guide_dog_server.is_running:
        return True

    # Reinitialize LNRunner with the selected pcvp_modules
    user_data.ln_manager_runner = LNRunner(user_data.ln_manager_address, pcvp_optional_modules=pcvp_modules)

    async def _start_pipeline():
        if user_data.path_to_workspace:
            path_to_workspace = await user_data.ln_manager_runner.run(user_data.path_to_workspace)
        else:
            path_to_workspace = await user_data.ln_manager_runner.run()

        map_user_to_data[key].path_to_workspace = path_to_workspace
        # Run blocking initialize() in a thread so it can be interrupted
        await asyncio.to_thread(map_user_to_data[key].guide_dog_server.initialize)
        return True

    try:
        return await asyncio.wait_for(_start_pipeline(), timeout=timeout)
    except asyncio.TimeoutError:
        # Clean up if runner process exists
        if user_data.ln_manager_runner and user_data.ln_manager_runner.ln_manager_process:
            user_data.ln_manager_runner.kill_cissy_and_lnm_process(user_data.ln_manager_runner.ln_manager_process)
            user_data.ln_manager_runner.ln_manager_process = None
        raise

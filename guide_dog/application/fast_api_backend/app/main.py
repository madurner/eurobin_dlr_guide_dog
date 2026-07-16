import asyncio

import uvicorn
from auth import handle_api_key
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from pydantic_models import *
from user_data import *

tags_metadata = [
    {
        "name": "Camera Management",
        "description": "Create, update and delete the camera and its intrinsic information.",
    },
    {
        "name": "Image Management",
        "description": "Create, update and delete the image.",
    },
    {
        "name": "LN-PCVP Management",
        "description": "Start/Stop and get status of the PCVP pipeline managed via LN.",
    },
    {
        "name": "Detection Pipeline Call",
        "description": "The actual pipeline call.",
    },
]


async def detect_stuff(camera: Camera, image: cv2.Mat, guide_dog_server: GuideDogServerPCVP) -> dict:
    print(
        f"Run inference for {camera.camera_name} with image with dims "
        f"{camera.intrinsics.image_width} x {camera.intrinsics.image_height}"
    )

    # Send the image and intrinsic to the pipeline
    success = guide_dog_server.push_image_to_pipeline(img=image, intr=camera.intrinsics.get_as_array())

    # Check if there is a result
    resp = False
    timeout = 30
    time = 0
    while resp is False and success is True and time <= timeout:
        resp = guide_dog_server.get_data()
        time += 1
    if time >= timeout or resp is False:
        # handle timeout
        return {}

    return resp


app = FastAPI(dependencies=[Depends(handle_api_key)])


@app.get("/")
async def root():
    return {"message": "Hello World"}


# CAMERA CRUD
@app.post("/camera", response_model=CameraResponse, tags=["Camera Management"])
def add_camera(camera: Camera, key: Annotated[str, Depends(handle_api_key)]):
    set_user_camera(camera, key)
    return CameraResponse(message="Camera created successfully", camera=camera)


@app.put("/camera/{update_camera_name}", response_model=CameraUpdateResponse, tags=["Camera Management"])
def update_camera_intrinsics(
    update_camera_name: str,
    new_intrinsics: Intrinsics,
    user_camera: Annotated[Camera, Depends(get_user_camera)],
    key: Annotated[str, Depends(handle_api_key)],
):
    if not user_camera:
        raise HTTPException(status_code=404, detail=f"Camera {update_camera_name} not found")
    if user_camera.name == update_camera_name:
        old_intrinsics = user_camera.intrinsics
        update_camera_intrinsics(new_intrinsics, key)

        return CameraUpdateResponse(
            message=f"Camera {update_camera_name} updated successfully",
            old_intrinsics=old_intrinsics,
            new_intrinsics=new_intrinsics,
        )

    raise HTTPException(status_code=404, detail=f"Camera {update_camera_name} not found")


@app.get("/camera", response_model=CameraResponse, tags=["Camera Management"])
def get_camera(user_camera: Annotated[Camera, Depends(get_user_camera)]):
    if user_camera is None:
        raise HTTPException(status_code=404, detail="No camera was found")
    return CameraResponse(message="Returning camera parameters.", camera=user_camera)


# IMAGE CRUD
@app.get("/image", response_model=ImageResponse, tags=["Image Management"])
def get_image(image: Annotated[Image, Depends(get_user_image)]):
    if image is None:
        raise HTTPException(status_code=404, detail="No Image was found")

    return ImageResponse(message="Return current image", image_base64=image)


@app.post("/image", tags=["Image Management"])
async def create_image(file: Annotated[UploadFile, File()], key: Annotated[str, Depends(handle_api_key)]):
    contents = await file.read()
    set_user_image(Image(file_name=file.filename, content=contents), key)
    return {
        "message": "Image uploaded successfully",
        "file_name": file.filename,
    }


@app.delete("/image", tags=["Image Management"])
async def delete_image(key: Annotated[str, Depends(handle_api_key)]):
    delete_user_image(key)
    return {
        "message": "Image deleted successfully",
    }


# LN-PCVP CRUD
@app.post("/pipeline", tags=["LN-PCVP Management"])
async def start_pipeline(gdsp: Annotated[GuideDogServerPCVP, Depends(get_guide_dog_connection)]):
    gdsp.initialize()
    return {
        "message": "Pipeline startup success.",
        "state": "ready",
    }


@app.get("/pipeline", tags=["LN-PCVP Management"])
async def get_pipeline_status(gdsp: Annotated[GuideDogServerPCVP, Depends(get_guide_dog_connection)]):
    if gdsp.is_running:
        status = "ready"
    else:
        status = "stopped"
    return {
        "message": "Pipeline status retrieved.",
        "state": status,
    }


@app.delete("/pipeline", tags=["LN-PCVP Management"])
async def stop_pipeline(key: Annotated[str, Depends(handle_api_key)]
):
    stop_guide_dog_server(key)
    return {"message": "Pipeline shut down successfully", "state": "stopped"}


# DETECTION
@app.get("/detection", response_model=DetectionResponse, tags=["Detection Pipeline Call"])
async def detect(
    camera: Annotated[Camera, Depends(get_user_camera)],
    image: Annotated[Image, Depends(get_user_image)],
    gdsp: Annotated[GuideDogServerPCVP, Depends(get_guide_dog_connection)],
):
    if camera is None:
        raise HTTPException(status_code=404, detail="No camera was initialized")
    if image.get_as_cv_image() is None:
        raise HTTPException(status_code=404, detail="No image can be found")

    result = await detect_stuff(camera, image.get_as_cv_image(), gdsp)

    if len(result.items()) == 0:
        raise HTTPException(status_code=408, detail="Timeout while waiting for response from detection pipeline!")

    detection_results = []
    for pose in result["poses"]:
        detection_results.append(DetectionResult(pose_6dof=pose[2].flatten(), instance_id=pose[1], class_name=pose[0]))
    return DetectionResponse(
        message="Success!",
        result=detection_results,
        image_base64=result["overlay"],
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

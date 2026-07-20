import base64
from io import BytesIO

import numpy as np
from pydantic import BaseModel, Field, field_validator


class Intrinsics(BaseModel):
    principal_point_x: int
    principal_point_y: int
    focal_length_x: float
    focal_length_y: float
    image_width: int
    image_height: int

    def get_as_array(self):
        return [self.focal_length_x, self.focal_length_y, self.principal_point_x, self.principal_point_y]


class Camera(BaseModel):
    camera_name: str
    intrinsics: Intrinsics


class CameraResponse(BaseModel):
    message: str
    camera: Camera


class CameraUpdateResponse(BaseModel):
    message: str
    old_intrinsics: Intrinsics
    new_intrinsics: Intrinsics


class Image(BaseModel):
    file_name: str
    content: bytes

    def get_as_cv_image(self):
        # returns BGR images
        load_bytes = BytesIO(self.content)
        loaded_np = np.load(load_bytes, allow_pickle=True)
        return loaded_np


class ImageResponse(BaseModel):
    message: str
    # image: Image
    image_base64: str

    @field_validator("image_base64", mode="before")
    @classmethod
    def convert_image_content_to_base64(cls, image: Image) -> str:
        return base64.b64encode(image.content).decode("utf-8")


class DetectionResult(BaseModel):
    class_name: str = Field(min_length=1, max_length=100, description="The instance class name")
    instance_id: int
    pose_6dof: list[float] = Field(max_length=16)


class DetectionResponse(BaseModel):
    message: str
    result: list[DetectionResult]
    image_base64: str

    @field_validator("image_base64", mode="before")
    @classmethod
    def convert_image_content_to_base64(cls, image: np.ndarray) -> str:
        np_bytes = BytesIO()
        np.save(np_bytes, image, allow_pickle=True)
        return base64.b64encode(np_bytes.getvalue()).decode("utf-8")

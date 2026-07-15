import codecs
import json
import logging
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from guide_dog_server_pcvp.git_relay_sync import sync_once, DEFAULT_EXCLUDES

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)

logger = logging.getLogger(__name__)


class GuideDogServerPCVP:
    def __init__(self):
        # Status
        self.is_running = False

        # Storage variables
        self._overlay = None
        self._poses = []

    def initialize(self):
        """
        Initialization of the client - module client and its interfaces
        """

        logger.info("connecting...")
        try:
            sync_once("./guide_dog_server_pcvp/assets", "./guide_dog_server_pcvp/assets", "main",
                      DEFAULT_EXCLUDES,
                      push=False, pull=True, retries=5, dry_run=False)
        except Exception as e:
            logger.error(f"Could not initialize connection to git_relay with error:\n {e}")
            self.is_running = False
            return

        logger.info("Initialization successful")
        self.is_running = True

    def push_image_to_pipeline(self, img=None | np.ndarray[tuple[Any, ...], np.dtype[Any]], intr=None | list):
        """
        Converts the input correctly and pushes it to the pipeline / git repo
        param: img: Image as numpy array
        param: intr: Intrinsic as array

        return: Boolean : True if message is send
        """
        if img is not None or intr is not None:
            # Convert to json format
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(str(Path(__file__).parent) + "/assets/input_image.png", img_rgb)
            json.dump(intr, codecs.open(str(Path(__file__).parent) + "/assets/intrinsic.json", 'w', encoding='utf-8'),
                      separators=(',', ':'),
                      sort_keys=True,
                      indent=4)  ### this saves the array in .json format

            # save to repo and push
            sync_once("./guide_dog_server_pcvp/assets", "./guide_dog_server_pcvp/assets", "main",
                      DEFAULT_EXCLUDES,
                      push=True, pull=False, retries=5, dry_run=False)
            return True
        else:
            return False

    def get_data(self):
        """
        Returns the result if it exists

        return: List[List of poses, overlay as numpy array]
        """
        logger.info("spinning...")
        files = sync_once("./guide_dog_server_pcvp/assets", "./guide_dog_server_pcvp/assets", "main",
                          DEFAULT_EXCLUDES,
                          push=False, pull=True, retries=5, dry_run=False)

        if len(files) == 0:
            time.sleep(1)
            return False

        # Received files
        self._poses = []
        for file in files:
            if file.find("overlay_image") != -1:
                img_bgr = cv2.imread(str(Path(__file__).parent) + "/assets/overlay_image.png")
                self._overlay = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            if file.find("poses") != -1:
                with codecs.open(str(Path(__file__).parent) + "/assets/poses.json", "r", encoding="utf-8") as f:
                    pose_dict = json.load(f)

                for class_name, instances in pose_dict.items():
                    for instance_id, pose in instances.items():
                        self._poses.append([
                            class_name,
                            int(instance_id),  # convert key back to int
                            np.array(pose).reshape(4, 4)  # or omit reshape if not applicable
                        ])

        # check if data has been written to storage variables
        if self._overlay is not None:
            result = {}
            p_list = []

            # convert nicely
            result["overlay"] = self._overlay
            if len(self._poses) != 0:
                result["poses"] = self._poses
            # reset storage variables
            self._overlay = None
            self._poses = None
            return result

        else:
            # return false if the request is not processed yet
            return False

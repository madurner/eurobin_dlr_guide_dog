import codecs
import json
import logging
import time
from pathlib import Path
from typing import Any

import cv2
import numpy

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
        self._poses = None

    def initialize(self):
        """
        Initialization of the client - module client and its interfaces
        """

        logger.info("connecting...")
        try:
            sync_once(".", ".", "main", DEFAULT_EXCLUDES,
                      push=True, pull=True, retries=5, dry_run=True)
        except Exception as e:
            logger.error(f"Could not initialize connection to git_relay with error:\n {e}")
            self.is_running = False
            return

        logger.info("Initialization successful")
        self.is_running = True

    def push_image_to_pipeline(self, img=None | numpy.ndarray[tuple[Any, ...], numpy.dtype[Any]], intr=None | list):
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
            sync_once(".", ".", "main", DEFAULT_EXCLUDES,
                      push=True, pull=True, retries=5, dry_run=True)
            return True
        else:
            return False

    def get_data(self):
        """
        Returns the result if it exists

        return: List[List of poses, overlay as numpy array]
        """
        logger.info("spinning...")
        files = sync_once(".", ".", "main", DEFAULT_EXCLUDES,
                          push=True, pull=True, retries=5, dry_run=True)

        if len(files) == 0:
            time.sleep(2)
            # TODO return if not in dry_run
            # return False

        # Received files
        files = [str(Path(__file__).parent) + "/assets/overlay_image.png",
                 str(Path(__file__).parent) + "/assets/poses.json"]  # TODO remove if not in dry_run
        for file in files:
            if file.find("overlay_image") != -1:
                img_bgr = cv2.imread(str(Path(__file__).parent) + "/assets/overlay_image.png")
                self._overlay = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            if file.find("poses") != -1:
                with open(file, 'r') as f:
                    print("opened poses.json")
                    # TODO parse poses from json format into expected dict!
                    self._poses = []  # json.load(f)

        # check if data has been written to storage variables
        if self._overlay is not None:
            result = {}
            p_list = []

            # convert nicely
            result["overlay"] = self._overlay
            if len(self._poses) != 0:
                for p in self._poses:
                    cls_name = p.get_class_name()
                    inst_id = p.get_instance_id()
                    inst_pose = p.get_transformation_se3().to_numpy_matrix()
                    p_list.append([cls_name, inst_id, inst_pose])
            result["poses"] = p_list
            # reset storage variables
            self._overlay = None
            self._poses = None
            return result

        else:
            # return false if the request is not processed yet
            return False

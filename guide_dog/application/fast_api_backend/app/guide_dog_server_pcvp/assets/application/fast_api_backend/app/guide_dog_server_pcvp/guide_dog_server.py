import logging
from pathlib import Path

import pcvp_client_py

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)


logger = logging.getLogger(__name__)


class GuideDogServerPCVP:
    def __init__(self, ln_manager_address: str):
        # Status
        self.is_running = False

        # Storage variables
        self._overlay = None
        self._poses = None

        # PCVP variables
        self.ln_manager_address = ln_manager_address
        self.module_client = None
        self.interface_client_source = None
        self.interface_client_sink = None

    def initialize(self):
        """
        Initialization of the pcvp client - module client and its interfaces

        """
        # # loading client module definition from yaml
        module_config_file = "guide_dog_server_pcvp/pcvp/module_definitions.yaml"
        yaml_richy = pcvp_client_py.RichYaml
        yaml_richy = yaml_richy.load_from_file(Path(module_config_file), unused_key_mode=pcvp_client_py.YamlUnusedKeyMode.WARN)

        # create pcvp client
        log_collector_thresholds = pcvp_client_py.LogCollectorThresholds.from_environment(
            8192, pcvp_client_py.TimeDifference.from_microseconds(250 * 1000)
        )
        log_collector = pcvp_client_py.LogCollector(log_collector_thresholds)
        self.module_client = pcvp_client_py.ModuleClientPy.create_with_ln_connection(
            ln_node_name="guide_dog_server_pcvp",
            ln_manager_address=self.ln_manager_address,
            pcvp_manager_ln_name="pcvp_manager",
            log_collector=log_collector,
            module_config=yaml_richy,
        )

        # Adding interface
        # INTERFACE 1:
        self.interface_client_source = self.module_client.create_interface_client_source("color_image_from_client")
        self.interface_client_source.disable_source_pull()

        # INTERFACE 2:
        self.interface_client_sink = self.module_client.create_interface_client_sink("detected_pose_image")
        self.interface_client_sink.set_on_receive_sink_push_callback(self._on_receive_sink_push_callback)

        logger.info("connecting...")
        self.module_client.connect_to_manager()
        logger.info("End initialization")

        self.is_running = True

    def _on_receive_sink_push_callback(self, msg=None):
        """
        Callback get called when module receives a message (overlay & poses)
        param: callback message
        """
        if msg is not None:
            # store to storage variables
            logger.info("---on_receive_source_pull_callback---")
            logger.info(msg)
            self._overlay = msg.overlay
            self._poses = msg.poses
        else:
            logger.info(f"_on_receive_sink_push_callback: {msg} is None")

    def push_image_to_pipeline(self, img=None, intr=None):
        """
        Converts the input correctly and pushes it to the pipeline
        param: img: Image as numpy array
        param: intr: Intrinsic as array

        return: Boolean : True if message is send
        """
        if img is not None or intr is not None:
            # Convert to pcvp format
            intrinsics = pcvp_client_py.CameraIntrinsics(intr[0], intr[1], intr[2], intr[3])

            img = pcvp_client_py.Image.from_numpy(
                image_meaning=pcvp_client_py.ImageMeaning.RGB,
                value_type=pcvp_client_py.ImageValueType.UINT8,
                value_scale=255,
                np_array=img,
                intrinsics=intrinsics,
            )

            output_msg_object = self.interface_client_source.create_output_message_object()

            output_msg_object.color_img = img
            output_msg_object.dummy_poses = []
            logger.info(output_msg_object)
            logger.info(type(output_msg_object))

            # push to manager
            self.interface_client_source.send_source_push(message=output_msg_object)
            return True
        else:
            return False

    def get_data(self):
        """
        Returns the result if it exists

        return: List[List of poses, overlay as numpy array]
        """
        logger.info("spinning...")
        self.module_client.spin_for(0.1)

        # check if data has been written to storage variables
        if self._overlay is not None:
            result = {}
            p_list = []

            # convert nicely
            result["overlay"] = self._overlay.get_image()
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

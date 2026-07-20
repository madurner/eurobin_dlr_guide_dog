import asyncio
import time
import logging
import os
import subprocess
import sys
import tempfile
import time
from typing import Literal, Optional, Union
from pathlib import Path

import links_and_nodes as ln

# from utils import check_if_package_is_latest


class LNRunner:
    def __init__(
        self,
        ln_manager_address: Union[str, int],
        pcvp_optional_modules: Optional[list[Literal["dense_pose", "yolov7", "m3t_refiner_cpp"]]] = None,
    ):
        self.ln_manager_address = ln_manager_address
        self.ln_manager_process = None
        self.pcvp_core_moduels = ["pcvp_manager", "guide_dog2_pcvp"]
        self.pcvp_optional_modules = [] if pcvp_optional_modules is None else pcvp_optional_modules

        if isinstance(self.ln_manager_address, str):
            if not self.ln_manager_address.startswith("localhost"):
                self.ln_manager_address = "localhost:" + f"{self.ln_manager_address}"

        if isinstance(self.ln_manager_address, int):
            self.ln_manager_address = "localhost:" + f"{self.ln_manager_address}"

    def _make_boilerplate_cissy_ws(self, path: str) -> str:
        ws = f"""
        config:
          generators: VirtualRunEnv, ln_env, ln_paths
          process_manager:
            start_command: ln_manager -c {path}/manager.lnc --mi-console #--webui
            requires:
              - links_and_nodes_manager/[^2.8]@common/stable
            requires_from_all: .*ln_msgdef"

        processes:
            pcvp_manager:
              requires:
                - pcvp_manager/3.5.0@semsa/unstable
              node: localhost
        """
        return ws

    def _make_pcvp_module_cissy_process(self, name: str) -> str:
        if name == "yolov7_pcvp":
            c = """
            yolov7_pcvp:
              requires:
                - yolov7_pcvp/2.4.0@semsa/unstable
              node: localhost
            """
        elif name == "dense_pose_pcvp":
            c = """
            dense_pose_pcvp:
              requires:
                - dense_pose_pcvp/3.0.4@semsa/unstable
              node: localhost
            """
        elif name == "m3t_refiner_cpp_pcvp":
            c = """
            m3t_refiner_pcvp:
              requires:
                - m3t_refiner_cpp_pcvp/0.3.1@semsa/unstable
                - pcvp_client_cpp/[^3.1.1]@semsa/unstable
              node: localhost
            """
        else:
            raise ValueError(f"Unknown module {name}")
        return c

    def _santinize_pcvp_optional_modules(
        self,
    ):
        pcvp_optional_modules = []
        for m in self.pcvp_optional_modules:
            if not m.endswith("_pcvp"):
                m += "_pcvp"
                pcvp_optional_modules.append(m)
        self.pcvp_optional_modules = pcvp_optional_modules

    def _dump_file(
        self,
        file: str,
        path: str,
        name: Optional[str] = None,
        type: Optional[Literal["yaml", "lnc"]] = None,
        verbose: bool = True,
    ) -> str:
        if not name.endswith(".yaml") or not name.endswith(".lnc"):
            if not type:
                raise Exception(f"{name} is not a yaml or lnc")
            assert type in ["yaml", "lnc"], f"{type} is not a yaml or lnc"
            name = name + f".{type}"
        # create temp file
        file_path = os.path.join(path, name)
        with open(file_path, "w") as f:
            f.write(file)

        if verbose:
            print(f"Dumping {name} at {file_path}")

        return file_path

    def create_cissy_ws_cfg(self, pcvp_modules: Union[list[str], str], path: str):
        if isinstance(pcvp_modules, str):
            pcvp_modules = [pcvp_modules]

        cissy_ws_cfg = self._make_boilerplate_cissy_ws(path=path)
        for pcvp_module in pcvp_modules:
            this_process_ws = self._make_pcvp_module_cissy_process(pcvp_module)
            cissy_ws_cfg += this_process_ws
        return cissy_ws_cfg

    def get_exact_pkg_version(self):
        pass

    def get_latest_pkg_version(self):
        pass

    def _make_yolov7_ln_process(self, path: Optional[str] = "%(CURDIR)"):
        return f"""
        process yolov7_pcvp
        use_template: yolov7_pcvp_gen
        use_template: pcvp_module_ln("yolov7_pcvp")
        command: pcvp_start_module --config {path}/detection_configs/config_yolo.yaml --disable-log
        add flags: forward_x11
        """

    def _make_dense_pose_ln_process(self, path: Optional[str] = "%(CURDIR)"):
        return f"""
        process dense_pose_pcvp
        use_template: dense_pose_pcvp_gen
        use_template: pcvp_module_ln("dense_pose_pcvp")
        command: pcvp_start_module --config {path}/detection_configs/config_dense_pose.yaml --disable-log
        """

    def _make_m3t_refiner_ln_process(self, path: Optional[str] = "%(CURDIR)"):
        return f"""
        process m3t_refiner_cpp_pcvp
        use_template: m3t_refiner_pcvp_gen
        use_template: pcvp_module_ln("m3t_refiner_cpp_pcvp")
        command: pcvp_start_module --configfile-path {path}/detection_configs/config_m3t.yaml --bin-file-path %(CURDIR)/generated_bin_files/ -c -r
        """

    def create_ln_cfg(self, ln_path: str, ln_manager_address: str, cissygen_path: str) -> str:
        path = Path.cwd()
        if path.name == "ln_runner":
            path = path.parent
        ln_lnc = f"""
        instance
        name: guide dog for {ln_manager_address!s}
        manager: {ln_manager_address}
        enable_auto_groups: true

        defines
        # Defined by cissy run
        CISSYGEN: %(env CISSYGEN)
        include_glob {cissygen_path}/cissygen/**/*.lnc !{cissygen_path}/cissygen/**/_*.lnc

        ##### templates ####
        include {path}/ln_runner/templates.inc.lnc

        ##### PCVP #####
        push_name_prefix: guide_dog

        process pcvp_manager
        use_template: pcvp_manager_gen
        add environment: PCVP_LN_MANAGER_ADDRESS=%(manager)
        add environment: LN_PROGRAM_NAME=pcvp_manager
        add environment: LC_ALL=C.utf8
        add environment: PCVP_LOG_LEVEL=INFO
        command: run_pcvp_manager --configFile {ln_path}/pcvp_manager.yaml
        """
        for m in self.pcvp_optional_modules:
            if m == "yolov7_pcvp":
                c = self._make_yolov7_ln_process(path=f"{path}/../../mockup_pipeline")
            elif m == "m3t_refiner_cpp_pcvp":
                c = self._make_m3t_refiner_ln_process(path=f"{path}/../../mockup_pipeline")
            elif m == "dense_pose_pcvp":
                c = self._make_dense_pose_ln_process(path=f"{path}/../../mockup_pipeline")
            else:
                logging.warning(f"Unsupported pcvp module {m} - cannot generate pcvp manager connection")
            ln_lnc += c

        ln_lnc += """
        pop_name_prefix guide_dog"""

        return ln_lnc

    def _make_yolov7_pcvp_manager_cfg_connection(self) -> str:
        return """
            yolov7_pcvp:
                object_detection:
                    color_image:
                        from: sync_img -> color_img"""

    def _make_dense_pose_pcvp_manager_cfg_connection(self) -> str:
        return """
            dense_pose_pcvp:
                pose_estimation:
                  color_image:
                    from: sync_img -> color_img
                  bounding_boxes:
                    from: yolov7_pcvp.object_detection -> bounding_boxes"""

    def _make_m3t_refiner_cpp_pcvp_manager_cfg_connection(self) -> str:
        return """
            m3t_refiner_cpp_pcvp:
                object_refiner_color:
                  ~policies:
                    - if_not_responsive: drop
                  color_image:
                    from: sync_img -> color_img
                  poses:
                    from: dense_pose_pcvp.pose_estimation -> poses"""

    def create_pcvp_manager_cfg(self, **kwargs) -> str:
        pcvp_mg = """
        manager_config_version: 3.0.0
        modules: """
        # start_ln_manager: {kwargs.get("start_ln_manager", "false")}

        fallback_overlay = "guide_dog_server_pcvp.color_image_from_client -> color_img"
        fallback_pose = "guide_dog_server_pcvp.color_image_from_client -> dummy_poses"

        m_connection = ""
        for m in self.pcvp_optional_modules:
            pcvp_mg += f"""
            {m}:
                ln_node_name: {m}
            """
            if m == "yolov7_pcvp":
                c = self._make_yolov7_pcvp_manager_cfg_connection()
            elif m == "m3t_refiner_cpp_pcvp":
                c = self._make_m3t_refiner_cpp_pcvp_manager_cfg_connection()
                fallback_overlay = "m3t_refiner_cpp_pcvp.object_refiner_color -> overlay"
                fallback_pose = "m3t_refiner_cpp_pcvp.object_refiner_color -> refined_poses"
            elif m == "dense_pose_pcvp":
                c = self._make_dense_pose_pcvp_manager_cfg_connection()
                if "m3t_refiner_cpp_pcvp" not in self.pcvp_optional_modules:
                    fallback_overlay = "dense_pose_pcvp.pose_estimation -> overlay"
                    fallback_pose = "dense_pose_pcvp.pose_estimation -> poses"
            else:
                logging.warning(f"Unsupported pcvp module {m} - cannot generate pcvp manager connection")

            if c:
                m_connection += c

        pcvp_mg += f"""
            guide_dog_server_pcvp:
                ln_node_name: guide_dog_server_pcvp

        flow_gates:
          sync_img:
            type: synchronize
            slots:
              color_img: guide_dog_server_pcvp.color_image_from_client->color_img
              dummy_poses: guide_dog_server_pcvp.color_image_from_client->dummy_poses

        connections:
            guide_dog_server_pcvp:
                detected_pose_image:
                    overlay:
                        from: {fallback_overlay}
                    poses:
                        from: {fallback_pose}"""
        pcvp_mg += m_connection
        return pcvp_mg

    def check_lnm(self):
        pass

    def connect_module(
        self, process: subprocess.Popen, module: str, wait_for: bool, state: str, timeout: float = 15.0
    ) -> bool:
        process.stdin.write(f"start guide_dog/{module}\n")
        process.stdin.flush()
        if wait_for:
            wait_for_line(process, f"guide_dog/{module}: {state}", print_out=True, timeout=timeout)
        return True

    def connect_all_processes(self, verbose: bool = False, timeout: Union[int, float] = 60) -> bool:
        self.connect_module(
            process=self.ln_manager_process,
            module="pcvp_manager",
            wait_for=True,
            state="started",
            timeout=timeout,
        )
        print("PCVP MANAGER started...")
        # start all the pcvp modules
        for m in self.pcvp_optional_modules:
            self.connect_module(process=self.ln_manager_process, module=m, wait_for=True, state="ready", timeout=timeout)
            print(f"{m} started...")
        print("All modules connected!")
        return True

    def get_module_state(self, process: subprocess.Popen, module: str, verbose: bool = True) -> str:
        process.stdin.write(f'print self._find_process("guide_dog/{module}").state\n')
        process.stdin.flush()

        assert process.stdout is not None

        prev_line = ""
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line == "":
                time.sleep(0.5)
                continue
            if verbose:
                print(stdout_line)

            state = stdout_line.strip().split("#")[0]
            if state != "" and module in prev_line:
                break
            prev_line = stdout_line

        # breakpoint()
        return state

    def check_all_processes_ready(self, verbose: bool = False) -> bool:
        if self.ln_manager_process is None:
            return False
        process = self.ln_manager_process
        state = self.get_module_state(process, "pcvp_manager")
        if verbose:
            print(f"{state} for pcvp_manager")
        if state != "started" and state != "ready":
            print(f"{state} for pcvp_manager")
            return False
        for m in self.pcvp_optional_modules:
            state = self.get_module_state(process, m)
            if verbose:
                print(f"{state} for {m}")
            if state != "ready":
                print(f"{m} is {state}")
                return False
        return True

    def stop_module(self, process: subprocess.Popen, module: str) -> None:
        process.stdin.write(f"stop guide_dog/{module}\n")
        process.stdin.flush()

    def kill_cissy_and_lnm_process(self, process: subprocess.Popen) -> None:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        netstat_result = subprocess.run(["netstat", "-anp"], capture_output=True, text=True, check=True)

        # Extract port from ln_manager_address (e.g., "localhost:21112" -> "21112")
        port = str(self.ln_manager_address).split(":")[-1]

        for line in result.stdout.split("\n"):
            if "ln_manager" in line and port in line and "guide_dog" in line and "grep" not in line:
                pid = line.split()[1]
                print("ln_manager process found:")
                print(f"  PID: {pid}")
                print(f"  Command: {line}")
                subprocess.run(["kill", "-9", pid], check=True)
                print(f"Killed process {pid}")
                break

        for netline in netstat_result.stdout.split("\n"):
            if f":{port}" in netline and "LISTEN" in netline:
                pid = netline.split()[-1].split("/")[0]
                print(f"  PID: {pid}")
                print(f"  Command: {netline}")
                subprocess.run(["kill", "-9", pid], check=True)
                print(f"Killed process {pid}")
                break
        process.terminate()
        process.kill()

    async def stop_all(self) -> None:
        process = self.ln_manager_process
        self.stop_module(process, "pcvp_manager")
        for m in self.pcvp_optional_modules:
            self.stop_module(process, m)
        self.kill_cissy_and_lnm_process(process)
        process.stdin.write("stop guide_dog\n")
        process.stdin.flush()

    async def run(self, ws_path: Optional[str] = None):
        self._santinize_pcvp_optional_modules()
        # set temp
        temp_path = tempfile.mkdtemp() if ws_path is None else ws_path
        # create pcvp manager cfg
        pcvp_manager_cfg = self.create_pcvp_manager_cfg()
        self._dump_file(file=pcvp_manager_cfg, name="pcvp_manager", type="yaml", path=temp_path)

        # create ln
        ln_lnc = self.create_ln_cfg(ln_path=temp_path, ln_manager_address=self.ln_manager_address, cissygen_path=temp_path)
        self._dump_file(file=ln_lnc, name="manager", type="lnc", path=temp_path)

        # create cissy ws
        cissy_ws_cfg = self.create_cissy_ws_cfg(self.pcvp_optional_modules, path=temp_path)
        cissy_ws_file = self._dump_file(file=cissy_ws_cfg, name="cissy_workspace", type="yaml", path=temp_path)

        # run
        os.environ["LN_MANAGER"] = self.ln_manager_address
        # if ln.ln_manager_dir not in sys.path:
        sys.path.insert(0, ln.ln_manager_dir)
        for pth in ln.pythonpath:
            os.environ["PYTHONPATH"] = os.getenv("PYTHONPATH", "") + ":" + pth
        os.environ["PYTHONPATH"] = os.getenv("PYTHONPATH") + ":" + ln.ln_manager_dir

        cmd = f"source /opt/rmc-build-tools/sourceme.sh && cissy run -w {cissy_ws_file} -o {temp_path}/cissygen"
        print(f"Running: {cmd}")
        self.ln_manager_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,  # output as text
            shell=True,
            encoding="utf-8",
            executable="/bin/bash",
            env=os.environ.copy(),
        )
        assert self.ln_manager_process.stdout is not None
        # IMPORTANT: Non-blocking reads, otherwise it might wait forever
        os.set_blocking(self.ln_manager_process.stdout.fileno(), False)
        # Wait until connected
        print("Waiting for LN MANAGER...")
        status = wait_for_line(
            self.ln_manager_process,
            f"listening on '{os.getenv('HOSTNAME')}:{self.ln_manager_address.split(':')[-1]}' for ln-clients!",
            print_out=True,
            timeout=60,
        )
        if not status:
            print("Error occured! Fix before setting up the LNM")
            return None
        print("LN MANAGER started...")
        assert self.ln_manager_process.stdin is not None
        self.connect_all_processes(verbose=True, timeout=180)
        return temp_path


def wait_for_line(
    process: subprocess.Popen, line: str, print_out: bool = False, timeout: float = 15.0, debug: bool = False
) -> bool:
    """
    Wait for a specific line to appear in the terminal.

    Args:
        process: The subprocess to monitor
        line: The line to wait for
        print_out: Whether to print output lines
        timeout: Maximum time to wait in seconds (default: 15)

    Raises:
        TimeoutError: If the line is not found within the timeout period
    """
    assert process.stdout is not None
    start_time = time.time()
    while True:
        stdout_line = process.stdout.readline()
        if stdout_line == "":
            time.sleep(0.5)
            # Check timeout after sleep
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timed out after {timeout} seconds waiting for line: {line}")
            continue
        if print_out:
            print(stdout_line)
        if debug:
            breakpoint()
        if line in stdout_line:
            return True
        elif "ERROR: " in line:
            break
    return False


async def main():
    ln_runner = LNRunner(
        ln_manager_address="localhost:38641", pcvp_optional_modules=["dense_pose", "m3t_refiner_cpp", "yolov7"]
    )

    path = await ln_runner.run(ws_path=os.getcwd())
    await asyncio.sleep(5)

    ready = ln_runner.check_all_processes_ready(verbose=True)

    if ready:
        print("LN Manager is running")
        await ln_runner.stop_all()
        print("LN Manager is stopped")
    else:
        print("LN Manager is not running")


if __name__ == "__main__":
    asyncio.run(main())

from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "a1fb8f73a20014f5"
    cissy_package_name = "process_dense_pose_pcvp_a1fb8f73a20014f5"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_dense_pose_pcvp_a1fb8f73a20014f5",
        "cissy_node": None,
    }

    requires = [
        ("dense_pose_pcvp/2.4.5@semsa/unstable"),
    ]

    def configure(self):
        self.options["*"].python_version = '3'


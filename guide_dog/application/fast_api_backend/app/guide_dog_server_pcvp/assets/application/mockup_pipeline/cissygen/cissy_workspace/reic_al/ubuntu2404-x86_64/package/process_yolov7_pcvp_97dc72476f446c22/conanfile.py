from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "97dc72476f446c22"
    cissy_package_name = "process_yolov7_pcvp_97dc72476f446c22"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_yolov7_pcvp_97dc72476f446c22",
        "cissy_node": None,
    }

    requires = [
        ("yolov7_pcvp/main@semsa/snapshot"),
    ]

    def configure(self):
        self.options["*"].python_version = '3'


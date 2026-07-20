from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "0e87107a980aa88d"
    cissy_package_name = "process_yolov7_pcvp_0e87107a980aa88d"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_yolov7_pcvp_0e87107a980aa88d",
        "cissy_node": None,
    }

    requires = [
        ("yolov7_pcvp/[^2.3.1]@semsa/unstable"),
    ]

    def configure(self):
        self.options["*"].python_version = '3'


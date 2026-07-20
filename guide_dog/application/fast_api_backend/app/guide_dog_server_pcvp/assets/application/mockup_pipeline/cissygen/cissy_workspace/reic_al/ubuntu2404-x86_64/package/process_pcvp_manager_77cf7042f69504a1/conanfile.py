from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "77cf7042f69504a1"
    cissy_package_name = "process_pcvp_manager_77cf7042f69504a1"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_pcvp_manager_77cf7042f69504a1",
        "cissy_node": None,
    }

    requires = [
        ("pcvp_manager/3.1.0@semsa/unstable"),
    ]



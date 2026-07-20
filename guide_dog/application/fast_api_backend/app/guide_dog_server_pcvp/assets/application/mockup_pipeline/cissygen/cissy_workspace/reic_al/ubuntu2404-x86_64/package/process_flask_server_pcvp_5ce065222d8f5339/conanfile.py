from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "5ce065222d8f5339"
    cissy_package_name = "process_flask_server_pcvp_5ce065222d8f5339"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_flask_server_pcvp_5ce065222d8f5339",
        "cissy_node": None,
    }

    requires = [
        ("flask_pcvp/0.10.0@semsa/unstable"),
    ]



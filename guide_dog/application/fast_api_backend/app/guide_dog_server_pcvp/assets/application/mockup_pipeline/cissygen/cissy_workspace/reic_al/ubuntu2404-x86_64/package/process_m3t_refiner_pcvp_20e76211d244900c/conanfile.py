from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "20e76211d244900c"
    cissy_package_name = "process_m3t_refiner_pcvp_20e76211d244900c"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_m3t_refiner_pcvp_20e76211d244900c",
        "cissy_node": None,
    }

    requires = [
        ("m3t_refiner_cpp_pcvp/0.3.0@semsa/unstable"),
        ("pcvp_client_cpp/3.5.0@semsa/unstable"),
    ]



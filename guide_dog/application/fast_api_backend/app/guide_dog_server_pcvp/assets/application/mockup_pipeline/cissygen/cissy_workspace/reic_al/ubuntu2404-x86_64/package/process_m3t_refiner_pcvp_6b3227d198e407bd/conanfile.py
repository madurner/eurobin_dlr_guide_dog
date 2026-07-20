from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "6b3227d198e407bd"
    cissy_package_name = "process_m3t_refiner_pcvp_6b3227d198e407bd"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process_m3t_refiner_pcvp_6b3227d198e407bd",
        "cissy_node": None,
    }

    requires = [
        ("m3t_refiner_cpp_pcvp/0.3.0@semsa/unstable"),
    ]



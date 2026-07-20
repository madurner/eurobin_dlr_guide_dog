from conan import ConanFile

class ConanInstallHelper(ConanFile):
    package_type = "application"
    author = "cissy <RMC-SEnAT@intra.dlr.de>"
    name = "a3c1aee5b38ffebe"
    cissy_package_name = "process__manager_process_a3c1aee5b38ffebe"
    url = "https://wiki.robotic.dlr.de/Cissy"
    settings = "os", "compiler", "build_type", "arch"

    generators = ("VirtualRunEnv", "ln_env", "ln_paths", )
    options = {
        "process_name": ["ANY"],
        "cissy_node": ["ANY"],
    }
    default_options = {
        "process_name": "process__manager_process_a3c1aee5b38ffebe",
        "cissy_node": None,
    }

    requires = [
        ("links_and_nodes_ln_msgdef/2.8.2@common/stable"),
        ("links_and_nodes_manager/[^2.6]@common/stable"),
    ]

    def configure(self):
        self.options["links_and_nodes_manager"].python_version = '3'


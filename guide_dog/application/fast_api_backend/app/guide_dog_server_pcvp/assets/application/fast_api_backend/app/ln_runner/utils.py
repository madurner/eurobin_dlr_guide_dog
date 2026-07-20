# Adjusted from ttk
import subprocess
import warnings

import packaging.version
from packaging.version import Version


def check_if_package_is_latest(package_name):
    result = subprocess.run(
        f"conan search -r rmc-conan-libs {package_name.split('/')[0]} --raw", shell=True, capture_output=True, text=True
    )
    assert result.stderr == "", f"Error during conan package search: {result.stderr}"
    package_list = result.stdout.split("\n")

    versions = []
    for package in package_list:
        try:
            if len(package.split("/")) > 1:
                versions.append(Version(Version(package.split("/")[1].split("@")[0]).base_version))
        except packaging.version.InvalidVersion:
            continue
        except Exception as e:
            raise e

    if package_name.endswith("snapshot"):
        warnings.warn(f"You use a snapshot version of {package_name}. Continuing at own risk ...", stacklevel=2)
    elif max(versions) > Version(package_name.split("@")[0].split("/")[1]):
        choice = input(
            f"There is a newer version for the package {package_name} available ({max(versions)}). You can "
            f"continue on own risk (y/n): "
        )
        if choice not in ["y", "Y"]:
            print(f"\nAborting (choice: `{choice}`).")
            exit(0)

        choice = input(
            "You continue on your own risk. Do you want to send boer_wo an email with information to "
            "update the default package list? (y/n): "
        )

import os
from glob import glob
from setuptools import find_packages, setup

package_name = "chroma_core"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="H.A. Sharif",
    maintainer_email="hiba2anwar@gmail.com",
    description="Core logic and decision-making nodes for the CHROMA framework",
    license="GPL-v3",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "capability_manager = chroma_core.capability_manager:main",
            "task_allocator = chroma_core.task_allocator:main",
            "mission_executor = chroma_core.mission_executor:main",
            "mission_spawner = chroma_core.mission_spawner:main",
            "validate_configs = scripts.validate_configs:validate_profiles",
            "benchmark_logger = scripts.benchmark_logger:main",
            "plot_benchmarks = scripts.plot_benchmarks:main",
            "fault_scenarios = scripts.fault_scenarios:main",
        ],
    },
)

import os
import json
import setuptools

# Read version from version.json
with open("version.json", "r") as f:
    version_info = json.load(f)
    version_str = version_info["version"]

# Configurations
with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()

# Get requirements
required_packages = []
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt"), "r") as f:
    for line in f:
        if line.strip() and not line.startswith("#") and "whl" not in line:
            required_packages.append(line.strip())

packages = [
    *setuptools.find_packages(),
]

setuptools.setup(
    install_requires=required_packages,  # Dependencies
    extras_require={},
    # Minimum Python version
    python_requires=">=3.10",
    name="taskweaver",  # Package name
    version=version_str,  # Version
    author="Microsoft TaskWeaver",  # Author name
    author_email="taskweaver@microsoft.com",  # Author mail
    description="A code-first agent framework for data analytics tasks",  # Short package description
    # Long package description
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Searches throughout all dirs for files to include
    packages=packages,
    # Must be true to include files depicted in MANIFEST.in
    include_package_data=True,
    license_files=["LICENSE"],  # License file
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_data={
        "taskweaver": ["**/*.yaml", "**/*.yml", "**/*.json"],
    },
    entry_points={
        "console_scripts": ["taskweaver=taskweaver.__main__:main"],
    },
)


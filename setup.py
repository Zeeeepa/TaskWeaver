import os
import re

import setuptools

# Get version from version.py
def get_version():
    try:
        with open(os.path.join("standalone_taskweaver", "version.py"), "r") as f:
            version_file = f.read()
        version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", version_file)
        if version_match:
            return version_match.group(1)
        return "unknown"
    except Exception as e:
        print(f"Error reading version: {str(e)}")
        return "unknown"

version_str = get_version()

# Configurations
with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()


# create zip file for ext
def create_zip_file():
    import zipfile
    from pathlib import Path

    root_dir = Path(__file__).parent
    ext_zip_file = root_dir / "taskweaver" / "cli" / "taskweaver-project.zip"
    if os.path.exists(ext_zip_file):
        os.remove(ext_zip_file)

    content_root = root_dir / "project"
    zipf = zipfile.ZipFile(ext_zip_file, "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(content_root):
        for file in files:
            zipf.write(
                os.path.join(root, file),
                os.path.relpath(Path(root) / file, root_dir),
            )
    zipf.close()

# Only create zip file if project directory exists
if os.path.exists(os.path.join(os.path.dirname(__file__), "project")):
    create_zip_file()

cur_dir = os.path.dirname(
    os.path.abspath(
        __file__,
    ),
)

required_packages = []
with open(os.path.join(cur_dir, "requirements.txt"), "r") as f:
    for line in f:
        if line.startswith("#"):
            continue
        else:
            package = line.strip()
            if "whl" in package:
                continue
            required_packages.append(package)
# print(required_packages)

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
    author="Microsoft Taskweaver",  # Author name
    author_email="taskweaver@microsoft.com",  # Author mail
    description="Python package taskweaver",  # Short package description
    # Long package description
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Searches throughout all dirs for files to include
    packages=packages,
    # Must be true to include files depicted in MANIFEST.in
    # include_package_data=True,
    license_files=["LICENSE"],  # License file
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_data={
        "taskweaver": ["**/*.yaml", "**/*.yml"],
        "taskweaver.cli": ["taskweaver-project.zip"],
    },
    entry_points={
        "console_scripts": ["taskweaver=taskweaver.__main__:main"],
    },
)

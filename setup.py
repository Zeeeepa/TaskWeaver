import os
import re

import setuptools
from scripts.get_package_version import get_package_version


def update_version_file(version: str):
    # Extract the version from the init file.
    VERSIONFILE = "taskweaver/__init__.py"
    with open(VERSIONFILE, "rt") as f:
        raw_content = f.read()

    content = re.sub(r"__version__ = [\"'][^']*[\"']", f'__version__ = "{version}"', raw_content)
    with open(VERSIONFILE, "wt") as f:
        f.write(content)

    def revert():
        with open(VERSIONFILE, "wt") as f:
            f.write(raw_content)

    return revert


version_str = get_package_version()
revert_version_file = update_version_file(version_str)

# Configurations
with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()


# create zip file for ext
def create_zip_file():
    import zipfile
    from pathlib import Path

    root_dir = Path(__file__).parent
    ext_zip_file = root_dir / "taskweaver" / "cli" / "taskweaver-project.zip"
    
    # Create the cli directory if it doesn't exist
    os.makedirs(os.path.dirname(ext_zip_file), exist_ok=True)
    
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

try:
    setuptools.setup(
        install_requires=required_packages,  # Dependencies
        extras_require={
            "dev": [
                "pytest>=7.4.0",
                "black>=23.7.0",
                "isort>=5.12.0",
                "flake8>=6.1.0",
                "mypy>=1.5.1",
            ],
        },
        # Minimum Python version
        python_requires=">=3.10",
        name="taskweaver",  # Package name
        version=version_str,  # Version
        author="Microsoft Taskweaver",  # Author name
        author_email="taskweaver@microsoft.com",  # Author mail
        description="A code-first agent framework for seamlessly planning and executing data analytics tasks",  # Short package description
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
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
        ],
        package_data={
            "taskweaver": ["**/*.yaml", "**/*.yml"],
            "taskweaver.cli": ["taskweaver-project.zip"],
        },
        entry_points={
            "console_scripts": ["taskweaver=taskweaver.__main__:main"],
        },
    )
finally:
    revert_version_file()

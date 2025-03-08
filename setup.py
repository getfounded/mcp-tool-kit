import os
from setuptools import setup, find_packages

# Read the content of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="mcptoolkit",
    version="0.1.0",
    author="getfounded",
    author_email="",  # Add author email if available
    description="A modular server implementation for Claude AI assistants with integrated tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/getfounded/mcp-tool-kit",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcptoolkit-server=mcptoolkit.mcp_unified_server:main",
            "mcptoolkit-config=mcptoolkit.config_ui:main",
        ],
    },
)

# First, build your distribution
import setuptools
import subprocess

# Build distribution
subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])

# Upload using the correct syntax
# Replace REPOSITORY_URL with your actual repository URL
subprocess.run([
    "python", "-m", "twine", "upload",
    "--repository-url", "https://test.pypi.org/legacy/",  # Example repository URL
    "dist/*"
])

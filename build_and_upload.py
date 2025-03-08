import subprocess
import os

# Ensure we have the right dependencies
subprocess.run(["python", "-m", "pip", "install",
               "--upgrade", "setuptools", "wheel", "twine"])

# Build the distribution packages
print("Building distribution packages...")
subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])

# Verify dist directory exists and contains files
dist_files = os.listdir("dist")
if not dist_files:
    print("No distribution files were created. Check for errors in the build process.")
    exit(1)

print(f"Created distribution files: {dist_files}")

# Upload to repository
print("Uploading to repository...")
# Replace with your actual repository URL
repository_url = "https://github.com/getfounded/mcp-tool-kit"
subprocess.run([
    "python", "-m", "twine", "upload",
    "--repository-url", repository_url,
    "dist/*"
])

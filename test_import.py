
#!/usr/bin/env python3
"""
Script to verify the powerpoint module imports correctly.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        # Try to import the powerpoint modules
        from app_old.tools.powerpoint.service import PowerPointService
        from app_old.tools.powerpoint.tools import ppt_create_presentation
        from app_old.tools.powerpoint.utils import PowerPointCommander
        
        print("✅ Successfully imported PowerPoint modules")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

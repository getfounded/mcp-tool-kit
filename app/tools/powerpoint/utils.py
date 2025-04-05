#!/usr/bin/env python3
"""
Utility functions for PowerPoint operations.
"""
import os
import re
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

class PowerPointCommander:
    """Process natural language commands for PowerPoint operations"""

    def __init__(self, ppt_service):
        """
        Initialize the PowerPoint commander.
        
        Args:
            ppt_service: PowerPoint service instance
        """
        self.ppt_service = ppt_service
        self.session_id = None
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a natural language command.
        
        Args:
            command: Natural language command string
            
        Returns:
            Dict with result information
        """
        command = command.lower().strip()
        
        # Create a new presentation
        if re.search(r'create|new|start', command) and re.search(r'presentation|slide deck|deck|ppt', command):
            if not self.session_id:
                self.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            template_path = None
            template_match = re.search(r'template\s+(?:from|at|is|=)\s+([\w\./\\]+)', command)
            if template_match:
                template_path = template_match.group(1)
            
            return self.ppt_service.create_presentation(self.session_id, template_path)
        
        # Open a presentation
        elif re.search(r'open|load', command) and re.search(r'presentation|slide deck|deck|ppt', command):
            file_match = re.search(r'(?:file|path)\s+(?:is|=)\s+([\w\./\\]+)', command)
            if file_match:
                file_path = file_match.group(1)
                
                if not self.session_id:
                    self.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                return self.ppt_service.open_presentation(self.session_id, file_path)
            else:
                return {
                    "status": "error",
                    "message": "Please specify the file path to open"
                }
        
        # Save a presentation
        elif re.search(r'save', command) and re.search(r'presentation|slide deck|deck|ppt', command):
            if not self.session_id:
                return {
                    "status": "error",
                    "message": "No active presentation session"
                }
            
            file_path = None
            file_match = re.search(r'(?:file|path|to)\s+(?:is|=|as)\s+([\w\./\\]+)', command)
            if file_match:
                file_path = file_match.group(1)
            
            return self.ppt_service.save_presentation(self.session_id, file_path)
        
        # Add a slide
        elif re.search(r'add', command) and re.search(r'slide', command):
            if not self.session_id:
                return {
                    "status": "error",
                    "message": "No active presentation session"
                }
            
            title = None
            title_match = re.search(r'title\s+(?:is|=)\s+([\w\s]+)', command)
            if title_match:
                title = title_match.group(1)
            
            content = None
            content_match = re.search(r'content\s+(?:is|=)\s+([\w\s]+)', command)
            if content_match:
                content = content_match.group(1)
            
            layout_index = 1
            layout_match = re.search(r'layout\s+(?:is|=)\s+(\d+)', command)
            if layout_match:
                layout_index = int(layout_match.group(1))
            
            return self.ppt_service.add_slide(self.session_id, layout_index, title, content)
        
        # Generate a presentation
        elif re.search(r'generate|create|make', command) and re.search(r'from|with|using', command) and re.search(r'content|text', command):
            if not self.session_id:
                self.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            title = "Generated Presentation"
            title_match = re.search(r'title\s+(?:is|=)\s+([\w\s]+)', command)
            if title_match:
                title = title_match.group(1)
            
            content = "Sample content"
            content_match = re.search(r'content\s+(?:is|=)\s+([\w\s]+)', command)
            if content_match:
                content = content_match.group(1)
            
            return self.ppt_service.generate_presentation(self.session_id, title, content)
        
        # Analyze a presentation
        elif re.search(r'analyze|review', command) and re.search(r'presentation|slide deck|deck|ppt', command):
            if not self.session_id:
                return {
                    "status": "error",
                    "message": "No active presentation session"
                }
            
            return self.ppt_service.analyze_presentation(self.session_id)
        
        # Enhance a presentation
        elif re.search(r'enhance|improve|suggest', command) and re.search(r'presentation|slide deck|deck|ppt', command):
            if not self.session_id:
                return {
                    "status": "error",
                    "message": "No active presentation session"
                }
            
            return self.ppt_service.enhance_presentation(self.session_id)
        
        else:
            return {
                "status": "error",
                "message": "Unrecognized command. Try something like 'create new presentation', 'add slide', or 'analyze presentation'."
            }

def is_windows_with_office() -> bool:
    """
    Check if running on Windows with Microsoft Office installed.
    
    Returns:
        bool: True if running on Windows with Office
    """
    if platform.system() != "Windows":
        return False
    
    try:
        import win32com.client
        # Try to create a PowerPoint application instance
        app = win32com.client.Dispatch("PowerPoint.Application")
        app.Quit()
        return True
    except:
        return False

def validate_image_path(path: str) -> bool:
    """
    Validate that a file exists and is an image.
    
    Args:
        path: Path to the image file
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(path):
        return False
    
    if not os.path.isfile(path):
        return False
    
    # Check file extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    _, ext = os.path.splitext(path.lower())
    
    return ext in image_extensions

def get_layout_name(layout_index: int) -> str:
    """
    Get a human-readable name for a slide layout index.
    
    Args:
        layout_index: Index of the slide layout
        
    Returns:
        str: Human-readable name for the layout
    """
    layout_names = {
        0: "Title Slide",
        1: "Title and Content",
        2: "Section Header",
        3: "Two Content",
        4: "Comparison",
        5: "Title Only",
        6: "Blank",
        7: "Content with Caption",
        8: "Picture with Caption"
    }
    
    return layout_names.get(layout_index, f"Layout {layout_index}")

def extract_color_components(hex_color: str) -> Tuple[int, int, int]:
    """
    Extract RGB components from a hex color string.
    
    Args:
        hex_color: Color as hex string (with or without #)
        
    Returns:
        Tuple[int, int, int]: RGB components
        
    Raises:
        ValueError: If the color format is invalid
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Validate format
    if not re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
        raise ValueError(f"Invalid color format: {hex_color}")
    
    # Extract components
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return r, g, b

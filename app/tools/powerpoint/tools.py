#!/usr/bin/env python3
"""
Tool functions for PowerPoint operations.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.powerpoint.service import get_service
from app.tools.powerpoint.utils import PowerPointCommander


@register_tool(
    name="ppt_create_presentation",
    description="Create a new PowerPoint presentation",
    category="powerpoint"
)
async def ppt_create_presentation(session_id: str, template_path: Optional[str] = None) -> str:
    """Create a new PowerPoint presentation

    Parameters:
    - session_id: Unique identifier for the presentation session
    - template_path: Optional path to a template file
    """
    powerpoint_service = get_service()
    result = powerpoint_service.create_presentation(session_id, template_path)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_open_presentation",
    description="Open an existing PowerPoint presentation",
    category="powerpoint"
)
async def ppt_open_presentation(session_id: str, file_path: str) -> str:
    """Open an existing PowerPoint presentation

    Parameters:
    - session_id: Unique identifier for the presentation session
    - file_path: Path to the PowerPoint file
    """
    powerpoint_service = get_service()
    result = powerpoint_service.open_presentation(session_id, file_path)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_save_presentation",
    description="Save the active PowerPoint presentation",
    category="powerpoint"
)
async def ppt_save_presentation(session_id: str, file_path: Optional[str] = None) -> str:
    """Save the active PowerPoint presentation

    Parameters:
    - session_id: ID of the presentation session
    - file_path: Optional path to save the file (if not provided, uses the existing path or generates a temporary one)
    """
    powerpoint_service = get_service()
    result = powerpoint_service.save_presentation(session_id, file_path)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_add_slide",
    description="Add a new slide to the presentation",
    category="powerpoint"
)
async def ppt_add_slide(
    session_id: str,
    layout_index: int = 1,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """Add a new slide to the presentation

    Parameters:
    - session_id: ID of the presentation session
    - layout_index: Index of the slide layout to use
    - title: Optional title for the slide
    - content: Optional content for the slide
    """
    powerpoint_service = get_service()
    result = powerpoint_service.add_slide(
        session_id, layout_index, title, content)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_add_text",
    description="Add text box to a slide",
    category="powerpoint"
)
async def ppt_add_text(
    session_id: str,
    slide_index: int,
    text: str,
    left: float = 1.0,
    top: float = 1.0,
    width: float = 8.0,
    height: float = 1.0,
    font_size: int = 18,
    font_name: str = 'Calibri',
    bold: bool = False,
    italic: bool = False,
    color: str = '000000'
) -> str:
    """Add text box to a slide

    Parameters:
    - session_id: ID of the presentation session
    - slide_index: Index of the slide (0-indexed)
    - text: Text content to add
    - left: Left position in inches
    - top: Top position in inches
    - width: Width in inches
    - height: Height in inches
    - font_size: Font size in points
    - font_name: Font name
    - bold: Whether the text should be bold
    - italic: Whether the text should be italic
    - color: Text color as hex string (without #)
    """
    powerpoint_service = get_service()
    result = powerpoint_service.add_text(
        session_id, slide_index, text, left, top, width, height,
        font_size, font_name, bold, italic, color
    )
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_add_image",
    description="Add image to a slide",
    category="powerpoint"
)
async def ppt_add_image(
    session_id: str,
    slide_index: int,
    image_path: str,
    left: float = 1.0,
    top: float = 1.0,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> str:
    """Add image to a slide

    Parameters:
    - session_id: ID of the presentation session
    - slide_index: Index of the slide (0-indexed)
    - image_path: Path to the image file
    - left: Left position in inches
    - top: Top position in inches
    - width: Optional width in inches (if None, maintains aspect ratio)
    - height: Optional height in inches (if None, maintains aspect ratio)
    """
    powerpoint_service = get_service()
    result = powerpoint_service.add_image(
        session_id, slide_index, image_path, left, top, width, height
    )
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_add_chart",
    description="Add chart to a slide",
    category="powerpoint"
)
async def ppt_add_chart(
    session_id: str,
    slide_index: int,
    chart_type: str,
    categories: List[str],
    series_names: List[str],
    series_values: List[List[float]],
    left: float = 1.0,
    top: float = 1.0,
    width: float = 8.0,
    height: float = 5.0,
    chart_title: Optional[str] = None
) -> str:
    """Add chart to a slide

    Parameters:
    - session_id: ID of the presentation session
    - slide_index: Index of the slide (0-indexed)
    - chart_type: Type of chart ('column', 'bar', 'line', 'pie', etc.)
    - categories: List of category labels
    - series_names: List of series names
    - series_values: List of lists containing values for each series
    - left: Left position in inches
    - top: Top position in inches
    - width: Width in inches
    - height: Height in inches
    - chart_title: Optional title for the chart
    """
    powerpoint_service = get_service()
    result = powerpoint_service.add_chart(
        session_id, slide_index, chart_type, categories, series_names, series_values,
        left, top, width, height, chart_title
    )
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_add_table",
    description="Add table to a slide",
    category="powerpoint"
)
async def ppt_add_table(
    session_id: str,
    slide_index: int,
    rows: int,
    cols: int,
    data: List[List[str]],
    left: float = 1.0,
    top: float = 1.0,
    width: float = 8.0,
    height: float = 5.0
) -> str:
    """Add table to a slide

    Parameters:
    - session_id: ID of the presentation session
    - slide_index: Index of the slide (0-indexed)
    - rows: Number of rows
    - cols: Number of columns
    - data: 2D list of data to populate the table
    - left: Left position in inches
    - top: Top position in inches
    - width: Width in inches
    - height: Height in inches
    """
    powerpoint_service = get_service()
    result = powerpoint_service.add_table(
        session_id, slide_index, rows, cols, data, left, top, width, height
    )
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_analyze_presentation",
    description="Analyze the content and structure of a presentation",
    category="powerpoint"
)
async def ppt_analyze_presentation(session_id: str) -> str:
    """Analyze the content and structure of a presentation

    Parameters:
    - session_id: ID of the presentation session
    """
    powerpoint_service = get_service()
    result = powerpoint_service.analyze_presentation(session_id)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_enhance_presentation",
    description="Provide suggestions to enhance the presentation",
    category="powerpoint"
)
async def ppt_enhance_presentation(session_id: str) -> str:
    """Provide suggestions to enhance the presentation

    Parameters:
    - session_id: ID of the presentation session
    """
    powerpoint_service = get_service()
    result = powerpoint_service.enhance_presentation(session_id)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_generate_presentation",
    description="Generate a presentation from text content",
    category="powerpoint"
)
async def ppt_generate_presentation(session_id: str, title: str, content: str) -> str:
    """Generate a presentation from text content

    Parameters:
    - session_id: ID of the presentation session
    - title: Title for the presentation
    - content: Text content to convert into a presentation
    """
    powerpoint_service = get_service()
    result = powerpoint_service.generate_presentation(
        session_id, title, content)
    return json.dumps(result, indent=2)


@register_tool(
    name="ppt_command",
    description="Process a natural language command for PowerPoint operations",
    category="powerpoint"
)
async def ppt_command(command: str) -> str:
    """Process a natural language command for PowerPoint operations

    Parameters:
    - command: Natural language command string
    """
    # Get the PowerPoint service
    powerpoint_service = get_service()

    # Initialize the command processor
    commander = PowerPointCommander(powerpoint_service)

    # Process the command
    result = commander.process_command(command)

    return json.dumps(result, indent=2)

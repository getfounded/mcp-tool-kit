# PowerPoint Tools

A comprehensive set of tools for creating and manipulating PowerPoint presentations programmatically.

## Features

- Cross-platform support (Windows-native via win32com, other platforms via python-pptx)
- Session-based presentation handling
- Support for all common PowerPoint operations (slides, text, images, charts, tables)
- Analysis and enhancement suggestions
- Natural language command processing

## Requirements

### Windows
- Python 3.6+
- win32com (pywin32)
- Microsoft PowerPoint installed

### Non-Windows (Linux, macOS)
- Python 3.6+
- python-pptx

## Usage Examples

### Creating a Presentation

```python
# Create a new presentation
session_id = "my_session_1"
result = await ppt_create_presentation(session_id)

# Create from template
result = await ppt_create_presentation(session_id, template_path="templates/company_template.pptx")
```

### Adding Content

```python
# Add a slide
result = await ppt_add_slide(session_id, layout_index=1, title="My Slide", content="This is the content")

# Add text
result = await ppt_add_text(
    session_id, 
    slide_index=0, 
    text="Hello World", 
    left=2.0, 
    top=3.0, 
    font_size=24, 
    bold=True, 
    color="0000FF"
)

# Add an image
result = await ppt_add_image(
    session_id,
    slide_index=0,
    image_path="/path/to/image.png",
    left=1.0,
    top=2.0,
    width=4.0
)

# Add a chart
result = await ppt_add_chart(
    session_id,
    slide_index=0,
    chart_type="column",
    categories=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Sales", "Profits"],
    series_values=[[100, 120, 130, 150], [50, 60, 65, 80]],
    chart_title="Quarterly Performance"
)

# Add a table
result = await ppt_add_table(
    session_id,
    slide_index=0,
    rows=3,
    cols=4,
    data=[
        ["Region", "Q1", "Q2", "Q3"],
        ["North", "$10K", "$12K", "$15K"],
        ["South", "$8K", "$9K", "$11K"]
    ]
)
```

### Analyzing and Enhancing

```python
# Analyze presentation
result = await ppt_analyze_presentation(session_id)

# Get enhancement suggestions
result = await ppt_enhance_presentation(session_id)
```

### Using Natural Language Commands

```python
# Process a natural language command
result = await ppt_command("create a new presentation with title 'Quarterly Report'")
result = await ppt_command("add a slide about sales figures")
result = await ppt_command("insert an image on slide 2")
```

### Saving and Closing

```python
# Save the presentation
result = await ppt_save_presentation(session_id, file_path="my_presentation.pptx")
```

## Environment Variables

- `PPT_TEMP_DIR`: Directory for temporary files (default: system temp directory)
- `PPT_USE_WIN32COM`: Whether to use win32com on Windows (default: "True")

## Implementation Details

The PowerPoint tools are built on a cross-platform abstraction that selects the appropriate implementation based on the operating system:

1. On Windows with Office installed, it uses win32com to directly control PowerPoint
2. On other platforms, it uses python-pptx for file manipulation

Each presentation is managed through a session ID, allowing multiple presentations to be managed simultaneously.

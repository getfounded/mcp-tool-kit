#!/usr/bin/env python3
"""
Cross-tool integration utilities for MCP tools.

This module provides utilities to facilitate integration and data exchange
between different tool services in the MCP Toolkit.
"""
import json
import logging
import importlib
from typing import Dict, List, Any, Optional, Union, Type, Callable

from app.toolkit import Toolkit
from app.tools.base.registry import get_or_create_service

logger = logging.getLogger(__name__)


def get_service(service_name: str) -> Optional[Any]:
    """
    Get a service instance by name.

    Args:
        service_name: Name of the service class

    Returns:
        Service instance or None if not found
    """
    try:
        # Try to find the service class dynamically
        module_path, class_name = service_name.rsplit('.', 1)
        module = importlib.import_module(module_path)
        service_class = getattr(module, class_name)

        # Get or create the service instance
        return get_or_create_service(service_class)
    except (ImportError, AttributeError, ValueError) as e:
        logger.error(f"Error getting service {service_name}: {e}")
        return None


def get_all_services() -> Dict[str, Any]:
    """
    Get all available services.

    Returns:
        Dictionary of service instances mapped by class name
    """
    toolkit = Toolkit()
    return toolkit.services


def convert_data_format(data: Any, source_format: str,
                        target_format: str) -> Any:
    """
    Convert data between different formats.

    Args:
        data: The data to convert
        source_format: Format of the input data
        target_format: Desired output format

    Returns:
        Converted data

    Raises:
        ValueError: If conversion is not supported
    """
    # Convert from source to JSON (intermediate format)
    if source_format == 'json':
        json_data = data
    elif source_format == 'dict':
        json_data = data
    elif source_format == 'json_string':
        json_data = json.loads(data)
    elif source_format == 'csv':
        import pandas as pd
        import io
        df = pd.read_csv(io.StringIO(data))
        json_data = json.loads(df.to_json(orient='records'))
    elif source_format == 'excel':
        import pandas as pd
        import io
        df = pd.read_excel(io.BytesIO(data))
        json_data = json.loads(df.to_json(orient='records'))
    else:
        raise ValueError(f"Conversion from {source_format} is not supported")

    # Convert from JSON to target format
    if target_format == 'json':
        return json_data
    elif target_format == 'dict':
        return json_data
    elif target_format == 'json_string':
        return json.dumps(json_data)
    elif target_format == 'csv':
        import pandas as pd
        import io
        df = pd.DataFrame(json_data)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue()
    elif target_format == 'excel':
        import pandas as pd
        import io
        df = pd.DataFrame(json_data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        return buffer.getvalue()
    elif target_format == 'html':
        import pandas as pd
        df = pd.DataFrame(json_data)
        return df.to_html()
    else:
        raise ValueError(f"Conversion to {target_format} is not supported")


def create_workflow(steps: List[Dict[str, Any]]) -> Callable:
    """
    Create a multi-step workflow across tools.

    The workflow is defined as a list of steps, where each step is a dictionary
    with the following keys:
    - 'tool': Name of the tool function
    - 'params': Parameters to pass to the tool
    - 'output': Name to assign to the output of this step (for referencing in later steps)

    Args:
        steps: List of workflow steps

    Returns:
        A callable function that executes the workflow

    Example:
        workflow = create_workflow([
            {
                'tool': 'xlsx_read_csv',
                'params': {'filename': 'data.csv'},
                'output': 'data'
            },
            {
                'tool': 'xlsx_filter_dataframe',
                'params': {'dataframe_id': '{data}', 'column': 'value', 'operator': '>', 'value': 10},
                'output': 'filtered_data'
            }
        ])
        result = await workflow()
    """
    toolkit = Toolkit()

    async def execute_workflow(**kwargs):
        """Execute the workflow steps sequentially."""
        context = kwargs.copy()
        results = []

        for i, step in enumerate(steps):
            tool_name = step['tool']
            params = step.get('params', {})
            output_name = step.get('output')

            # Process parameter references
            processed_params = {}
            for key, value in params.items():
                if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                    # Replace with a value from the context
                    ref_key = value[1:-1]
                    if ref_key in context:
                        processed_params[key] = context[ref_key]
                    else:
                        raise ValueError(
                            f"Step {i}: Reference {value} not found in context")
                else:
                    processed_params[key] = value

            # Execute the tool
            tool_fn = getattr(toolkit, tool_name)
            result = await tool_fn(**processed_params)

            # Store the result if an output name is provided
            if output_name:
                # Try to parse as JSON if it's a string
                if isinstance(result, str):
                    try:
                        parsed_result = json.loads(result)
                        context[output_name] = parsed_result
                    except json.JSONDecodeError:
                        context[output_name] = result
                else:
                    context[output_name] = result

            results.append(result)

        return results[-1] if results else None

    return execute_workflow


def export_workflow(steps: List[Dict[str, Any]], filepath: str) -> None:
    """
    Export a workflow definition to a JSON file.

    Args:
        steps: List of workflow steps
        filepath: Path to save the workflow JSON

    Returns:
        None
    """
    with open(filepath, 'w') as f:
        json.dump(steps, f, indent=2)


def import_workflow(filepath: str) -> Callable:
    """
    Import a workflow from a JSON file.

    Args:
        filepath: Path to the workflow JSON file

    Returns:
        A callable function that executes the workflow
    """
    with open(filepath, 'r') as f:
        steps = json.load(f)

    return create_workflow(steps)


def combine_results(results: List[Any],
                    method: str = 'concat',
                    **kwargs) -> Any:
    """
    Combine results from multiple tools.

    Args:
        results: List of results to combine
        method: Method for combining ('concat', 'merge', 'union', etc.)
        **kwargs: Additional parameters for the combination method

    Returns:
        Combined result

    Raises:
        ValueError: If combination method is not supported
    """
    import pandas as pd

    # Try to convert all results to pandas DataFrames
    dfs = []
    for result in results:
        if isinstance(result, pd.DataFrame):
            dfs.append(result)
        elif isinstance(result, dict) or isinstance(result, list):
            dfs.append(pd.DataFrame(result))
        elif isinstance(result, str):
            try:
                # Try to parse as JSON
                data = json.loads(result)
                dfs.append(pd.DataFrame(data))
            except json.JSONDecodeError:
                # Try to parse as CSV
                try:
                    import io
                    dfs.append(pd.read_csv(io.StringIO(result)))
                except:
                    raise ValueError(
                        f"Could not convert result to DataFrame: {result[:100]}...")
        else:
            raise ValueError(
                f"Could not convert result to DataFrame: {result}")

    # Apply the combination method
    if method == 'concat':
        return pd.concat(dfs, **kwargs)
    elif method == 'merge':
        if len(dfs) < 2:
            return dfs[0] if dfs else None

        result = dfs[0]
        for df in dfs[1:]:
            result = result.merge(df, **kwargs)

        return result
    elif method == 'union':
        # Union of unique rows
        return pd.concat(dfs).drop_duplicates().reset_index(drop=True)
    else:
        raise ValueError(f"Combination method {method} not supported")

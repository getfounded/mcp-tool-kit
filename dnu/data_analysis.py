#!/usr/bin/env python3
import os
import json
import logging
import io
import base64
from typing import List, Dict, Any, Optional, Union

# Data analysis libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import Tool, TextContent, ImageContent

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Data Analysis tools MCP reference set")


class DataAnalysisService:
    """Service to handle data analysis operations"""

    def __init__(self):
        # Set default plotting style
        sns.set(style="whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)

    async def read_data(self, file_path, file_format='auto'):
        """Read data from a file into a pandas DataFrame"""
        # Determine file format if auto
        if file_format == 'auto':
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                file_format = 'csv'
            elif ext == '.xlsx' or ext == '.xls':
                file_format = 'excel'
            elif ext == '.json':
                file_format = 'json'
            elif ext == '.sql':
                file_format = 'sql'
            else:
                file_format = 'csv'  # Default to CSV

        # Read data based on format
        try:
            if file_format == 'csv':
                return pd.read_csv(file_path)
            elif file_format == 'excel':
                return pd.read_excel(file_path)
            elif file_format == 'json':
                return pd.read_json(file_path)
            elif file_format == 'sql':
                # This requires SQLAlchemy and a connection string
                # For now, raise an error
                raise ValueError(
                    "SQL format requires SQLAlchemy and connection string")
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
        except Exception as e:
            raise ValueError(f"Error reading data: {str(e)}")

    async def get_data_summary(self, data):
        """Generate summary statistics for a DataFrame"""
        try:
            # Basic summary
            summary = {
                "shape": data.shape,
                "columns": list(data.columns),
                "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
                "missing_values": data.isna().sum().to_dict(),
                "numeric_summary": data.describe().to_dict()
            }

            # Add categorical summaries if needed
            cat_cols = data.select_dtypes(
                include=['object', 'category']).columns
            if len(cat_cols) > 0:
                summary["categorical_summary"] = {
                    # Limit to first 10
                    col: data[col].value_counts().to_dict() for col in cat_cols[:10]
                }

            return summary
        except Exception as e:
            raise ValueError(f"Error generating summary: {str(e)}")

    async def clean_data(self, data, operations=None):
        """Clean and preprocess a DataFrame based on specified operations"""
        try:
            cleaned_data = data.copy()
            results = {"operations_applied": []}

            if operations is None:
                # Default operations
                operations = ["drop_na", "convert_dates", "remove_duplicates"]

            for op in operations:
                if op == "drop_na":
                    old_shape = cleaned_data.shape[0]
                    cleaned_data = cleaned_data.dropna()
                    new_shape = cleaned_data.shape[0]
                    results["operations_applied"].append({
                        "operation": "drop_na",
                        "rows_removed": old_shape - new_shape
                    })

                elif op == "convert_dates":
                    # Try to automatically convert string columns that look like dates
                    for col in cleaned_data.select_dtypes(include=['object']).columns:
                        try:
                            pd.to_datetime(cleaned_data[col], errors='raise')
                            cleaned_data[col] = pd.to_datetime(
                                cleaned_data[col])
                            results["operations_applied"].append({
                                "operation": "convert_date",
                                "column": col
                            })
                        except:
                            pass

                elif op == "remove_duplicates":
                    old_shape = cleaned_data.shape[0]
                    cleaned_data = cleaned_data.drop_duplicates()
                    new_shape = cleaned_data.shape[0]
                    results["operations_applied"].append({
                        "operation": "remove_duplicates",
                        "rows_removed": old_shape - new_shape
                    })

                elif op == "fillna_mean" and "column" in operations:
                    col = operations["column"]
                    if col in cleaned_data.columns and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                        cleaned_data[col] = cleaned_data[col].fillna(
                            cleaned_data[col].mean())
                        results["operations_applied"].append({
                            "operation": "fillna_mean",
                            "column": col
                        })

                elif op == "scale" and "column" in operations:
                    col = operations["column"]
                    if col in cleaned_data.columns and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                        min_val = cleaned_data[col].min()
                        max_val = cleaned_data[col].max()
                        if max_val > min_val:  # Avoid division by zero
                            cleaned_data[col] = (
                                cleaned_data[col] - min_val) / (max_val - min_val)
                            results["operations_applied"].append({
                                "operation": "scale",
                                "column": col
                            })

            results["resulting_shape"] = cleaned_data.shape
            results["data"] = cleaned_data

            return results
        except Exception as e:
            raise ValueError(f"Error cleaning data: {str(e)}")

    async def create_visualization(self, data, viz_type, x_column=None, y_column=None,
                                   hue_column=None, title=None, **kwargs):
        """Create different types of visualizations for data"""
        try:
            # Create figure
            plt.figure(figsize=(10, 6))

            # Set up the visualization based on type
            if viz_type == "histogram":
                if x_column:
                    ax = sns.histplot(data=data, x=x_column,
                                      hue=hue_column, **kwargs)
                else:
                    raise ValueError(
                        "x_column must be specified for histogram")

            elif viz_type == "scatter":
                if x_column and y_column:
                    ax = sns.scatterplot(
                        data=data, x=x_column, y=y_column, hue=hue_column, **kwargs)
                else:
                    raise ValueError(
                        "Both x_column and y_column must be specified for scatter")

            elif viz_type == "line":
                if x_column and y_column:
                    ax = sns.lineplot(data=data, x=x_column,
                                      y=y_column, hue=hue_column, **kwargs)
                else:
                    raise ValueError(
                        "Both x_column and y_column must be specified for line")

            elif viz_type == "bar":
                if x_column and y_column:
                    ax = sns.barplot(data=data, x=x_column,
                                     y=y_column, hue=hue_column, **kwargs)
                else:
                    raise ValueError(
                        "Both x_column and y_column must be specified for bar")

            elif viz_type == "box":
                if x_column:
                    ax = sns.boxplot(data=data, x=x_column,
                                     y=y_column, hue=hue_column, **kwargs)
                else:
                    raise ValueError("x_column must be specified for box")

            elif viz_type == "heatmap":
                # For heatmap, data should be a correlation matrix or pivot table
                ax = sns.heatmap(data, annot=True, cmap="coolwarm", **kwargs)

            elif viz_type == "correlation":
                # Special case for correlation matrices
                corr_data = data.select_dtypes(include=['number']).corr()
                ax = sns.heatmap(corr_data, annot=True,
                                 cmap="coolwarm", **kwargs)

            elif viz_type == "pair":
                # Create pairplot (returns a PairGrid, not an Axes)
                columns = kwargs.get("columns", None)
                if columns:
                    grid = sns.pairplot(
                        data[columns], hue=hue_column, **kwargs)
                else:
                    numeric_cols = data.select_dtypes(
                        include=['number']).columns[:5]  # Limit to 5 columns
                    grid = sns.pairplot(
                        data[numeric_cols], hue=hue_column, **kwargs)
                plt.close()  # Close the original figure since pairplot creates its own
                fig = grid.fig
            else:
                raise ValueError(f"Unsupported visualization type: {viz_type}")

            # Set title if provided (except for pairplot which handles its own fig)
            if title and viz_type != "pair":
                plt.title(title)

            # Convert plot to image
            if viz_type == "pair":
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png')
                img_buf.seek(0)
                img_data = base64.b64encode(img_buf.read()).decode()
                plt.close(fig)
            else:
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png')
                img_buf.seek(0)
                img_data = base64.b64encode(img_buf.read()).decode()
                plt.close()

            return {
                "type": viz_type,
                "image_data": img_data
            }
        except Exception as e:
            plt.close()  # Ensure we close any open plots on error
            raise ValueError(f"Error creating visualization: {str(e)}")

    async def run_statistical_analysis(self, data, analysis_type, **kwargs):
        """Run statistical analyses on the data"""
        try:
            results = {"analysis_type": analysis_type}

            if analysis_type == "correlation":
                # Calculate correlation matrix
                correlation = data.select_dtypes(include=['number']).corr()
                results["correlation_matrix"] = correlation.to_dict()

                # Find top correlations
                corr_pairs = []
                for i, col1 in enumerate(correlation.columns):
                    for j, col2 in enumerate(correlation.columns):
                        if i < j:  # Only include each pair once
                            corr_pairs.append(
                                (col1, col2, correlation.loc[col1, col2]))

                # Sort by absolute correlation and get top 10
                corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                results["top_correlations"] = [
                    {"variable1": var1, "variable2": var2, "correlation": corr}
                    for var1, var2, corr in corr_pairs[:10]
                ]

            elif analysis_type == "regression":
                from sklearn.linear_model import LinearRegression
                from sklearn.metrics import mean_squared_error, r2_score

                x_cols = kwargs.get("x_columns", [])
                y_col = kwargs.get("y_column")

                if not x_cols or not y_col:
                    raise ValueError(
                        "x_columns and y_column must be specified for regression")

                # Prepare data
                X = data[x_cols].dropna()
                y = data[y_col].loc[X.index]

                # Fit model
                model = LinearRegression()
                model.fit(X, y)

                # Make predictions
                y_pred = model.predict(X)

                # Evaluate
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)

                results["coefficients"] = {x_cols[i]: float(
                    coef) for i, coef in enumerate(model.coef_)}
                results["intercept"] = float(model.intercept_)
                results["r2_score"] = r2
                results["mean_squared_error"] = mse

            elif analysis_type == "ttest":
                from scipy import stats

                group_col = kwargs.get("group_column")
                value_col = kwargs.get("value_column")
                group1 = kwargs.get("group1")
                group2 = kwargs.get("group2")

                if not group_col or not value_col:
                    raise ValueError(
                        "group_column and value_column must be specified for t-test")

                # If groups are specified, filter for those groups
                if group1 and group2:
                    sample1 = data[data[group_col] ==
                                   group1][value_col].dropna()
                    sample2 = data[data[group_col] ==
                                   group2][value_col].dropna()
                else:
                    # Otherwise use the first two unique groups
                    groups = data[group_col].unique()
                    if len(groups) < 2:
                        raise ValueError("Need at least two groups for t-test")

                    sample1 = data[data[group_col] ==
                                   groups[0]][value_col].dropna()
                    sample2 = data[data[group_col] ==
                                   groups[1]][value_col].dropna()
                    group1 = groups[0]
                    group2 = groups[1]

                # Run t-test
                t_stat, p_val = stats.ttest_ind(sample1, sample2)

                results["t_statistic"] = float(t_stat)
                results["p_value"] = float(p_val)
                results["group1"] = {"name": str(group1), "mean": float(
                    sample1.mean()), "std": float(sample1.std()), "count": len(sample1)}
                results["group2"] = {"name": str(group2), "mean": float(
                    sample2.mean()), "std": float(sample2.std()), "count": len(sample2)}
                results["significant_at_95"] = p_val < 0.05

            elif analysis_type == "anova":
                from scipy import stats

                group_col = kwargs.get("group_column")
                value_col = kwargs.get("value_column")

                if not group_col or not value_col:
                    raise ValueError(
                        "group_column and value_column must be specified for ANOVA")

                # Get samples for each group
                groups = []
                group_stats = []

                for group_name, group_data in data.groupby(group_col):
                    group_values = group_data[value_col].dropna()
                    if len(group_values) > 0:
                        groups.append(group_values)
                        group_stats.append({
                            "name": str(group_name),
                            "mean": float(group_values.mean()),
                            "std": float(group_values.std()),
                            "count": len(group_values)
                        })

                if len(groups) < 2:
                    raise ValueError("Need at least two groups for ANOVA")

                # Run ANOVA
                f_stat, p_val = stats.f_oneway(*groups)

                results["f_statistic"] = float(f_stat)
                results["p_value"] = float(p_val)
                results["groups"] = group_stats
                results["significant_at_95"] = p_val < 0.05

            elif analysis_type == "summary_stats":
                columns = kwargs.get("columns", data.select_dtypes(
                    include=['number']).columns)
                results["summary"] = data[columns].describe().to_dict()

            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

            return results
        except Exception as e:
            raise ValueError(f"Error in statistical analysis: {str(e)}")

# Tool function definitions that will be registered with MCP


async def data_analyze_file(file_path: str, file_format: str = 'auto', summary: bool = True,
                            visualize: bool = True, viz_type: str = 'correlation',
                            ctx: Context = None) -> str:
    """Analyze a data file with summary statistics and visualizations.

    Parameters:
    - file_path: Path to the data file
    - file_format: Format of the file ('auto', 'csv', 'excel', 'json')
    - summary: Whether to include summary statistics
    - visualize: Whether to include visualizations
    - viz_type: Type of visualization to create ('correlation', 'histogram', 'scatter', etc.)
    """
    try:
        data_service = _get_data_analysis_service()

        # Read data
        df = await data_service.read_data(file_path, file_format)

        results = {"file_path": file_path, "rows": len(
            df), "columns": len(df.columns)}

        # Generate summary if requested
        if summary:
            summary_data = await data_service.get_data_summary(df)
            results["summary"] = summary_data

        # Generate visualization if requested
        if visualize:
            if viz_type == 'correlation':
                viz_result = await data_service.create_visualization(df, 'correlation')
            elif viz_type == 'histogram' and len(df.columns) > 0:
                # Get first numeric column for histogram
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    viz_result = await data_service.create_visualization(
                        df, 'histogram', x_column=numeric_cols[0]
                    )
                else:
                    viz_result = {
                        "error": "No numeric columns found for histogram"}
            elif viz_type == 'pair':
                # Get first few numeric columns for pairplot
                # Limit to 4 columns for performance
                numeric_cols = df.select_dtypes(include=['number']).columns[:4]
                if len(numeric_cols) >= 2:
                    viz_result = await data_service.create_visualization(
                        df, 'pair', columns=numeric_cols
                    )
                else:
                    viz_result = {
                        "error": "Need at least 2 numeric columns for pair plot"}
            else:
                viz_result = {
                    "error": f"Visualization type {viz_type} not handled automatically"}

            results["visualization"] = viz_result

            # Create visualization image resource if available
            if "image_data" in viz_result:
                if ctx:
                    # Check if we have MCP context to return the image
                    img = Image(data=viz_result["image_data"], format="png")
                    img_resource_id = f"data_viz_{id(df)}_{viz_type}"
                    ctx.set_resource(img_resource_id, img)
                    results["image_resource"] = img_resource_id

        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def data_clean(file_path: str, operations: List[str] = None, output_path: str = None,
                     ctx: Context = None) -> str:
    """Clean and preprocess a data file.

    Parameters:
    - file_path: Path to the data file
    - operations: List of cleaning operations to perform (drop_na, convert_dates, remove_duplicates, etc.)
    - output_path: Path to save the cleaned data (if not provided, results are not saved)
    """
    try:
        data_service = _get_data_analysis_service()

        # Read data
        df = await data_service.read_data(file_path)

        # Clean data
        clean_results = await data_service.clean_data(df, operations)
        cleaned_df = clean_results["data"]

        # Save if output path is specified
        if output_path:
            ext = os.path.splitext(output_path)[1].lower()
            if ext == '.csv':
                cleaned_df.to_csv(output_path, index=False)
            elif ext == '.xlsx':
                cleaned_df.to_excel(output_path, index=False)
            elif ext == '.json':
                cleaned_df.to_json(output_path, orient='records', indent=2)
            else:
                # Default to CSV
                cleaned_df.to_csv(output_path, index=False)

            clean_results["saved_to"] = output_path

        # Remove DataFrame from results to make it JSON serializable
        del clean_results["data"]

        return json.dumps(clean_results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def data_visualize(file_path: str, viz_type: str, x_column: str = None, y_column: str = None,
                         hue_column: str = None, title: str = None, viz_options: Dict = None,
                         ctx: Context = None) -> str:
    """Create a visualization from data.

    Parameters:
    - file_path: Path to the data file
    - viz_type: Type of visualization (histogram, scatter, line, bar, box, heatmap, correlation, pair)
    - x_column: Column to use for x-axis
    - y_column: Column to use for y-axis
    - hue_column: Column to use for color grouping
    - title: Title for the visualization
    - viz_options: Additional options for the visualization (depends on type)
    """
    try:
        data_service = _get_data_analysis_service()

        # Read data
        df = await data_service.read_data(file_path)

        # Process visualization options
        viz_kwargs = viz_options or {}

        # Create visualization
        viz_result = await data_service.create_visualization(
            df, viz_type, x_column, y_column, hue_column, title, **viz_kwargs
        )

        # Create visualization image resource if available
        if "image_data" in viz_result and ctx:
            img = Image(data=viz_result["image_data"], format="png")
            img_resource_id = f"data_viz_{viz_type}_{id(df)}"
            ctx.set_resource(img_resource_id, img)
            viz_result["image_resource"] = img_resource_id

        return json.dumps(viz_result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def data_statistical_test(file_path: str, analysis_type: str, **kwargs) -> str:
    """Run a statistical analysis on data.

    Parameters:
    - file_path: Path to the data file
    - analysis_type: Type of analysis (correlation, regression, ttest, anova, summary_stats)
    - **kwargs: Additional parameters for the specific analysis type
    """
    try:
        data_service = _get_data_analysis_service()

        # Read data
        df = await data_service.read_data(file_path)

        # Run analysis
        analysis_result = await data_service.run_statistical_analysis(df, analysis_type, **kwargs)

        return json.dumps(analysis_result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# Tool registration and initialization
_data_analysis_service = None


def initialize_data_analysis_service():
    """Initialize the data analysis service"""
    global _data_analysis_service
    _data_analysis_service = DataAnalysisService()
    return _data_analysis_service


def _get_data_analysis_service():
    """Get or initialize the data analysis service"""
    global _data_analysis_service
    if _data_analysis_service is None:
        _data_analysis_service = initialize_data_analysis_service()
    return _data_analysis_service


def get_data_analysis_tools():
    """Get a dictionary of all data analysis tools for registration with MCP"""
    return {
        "data_analyze_file": data_analyze_file,
        "data_clean": data_clean,
        "data_visualize": data_visualize,
        "data_statistical_test": data_statistical_test
    }

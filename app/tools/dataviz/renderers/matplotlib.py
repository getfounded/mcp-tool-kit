"""
Matplotlib renderer for DataViz service.

This module provides visualization rendering using matplotlib.
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure matplotlib for non-interactive use
matplotlib.use('Agg')

# Configure logging
logger = logging.getLogger(__name__)


class MatplotlibRenderer:
    """Renderer implementation using matplotlib."""
    
    def __init__(self, service):
        """
        Initialize with parent service reference.
        
        Args:
            service: The parent DataVizService instance
        """
        self.service = service
        self._configure()
        
    def _configure(self):
        """Configure matplotlib settings."""
        # Set default style
        plt.style.use('ggplot')
        
        # Configure default figure size
        plt.rcParams['figure.figsize'] = (10, 6)
        
        # Improve font rendering
        plt.rcParams['font.family'] = 'sans-serif'
        
        logger.debug("MatplotlibRenderer configured")
    
    def _create_figure(self) -> Tuple[Figure, Any]:
        """
        Create a new figure and axis.
        
        Returns:
            Tuple containing (figure, axis)
        """
        fig, ax = plt.subplots()
        return fig, ax
    
    def line_chart(self, data, x_column, y_columns, title=None, **kwargs):
        """
        Render a line chart using matplotlib.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis
            y_columns: List of columns for y-axis
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating line chart with columns: {y_columns}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Plot each y column
        for y_col in y_columns:
            ax.plot(df[x_column], df[y_col], label=y_col, marker='o', markersize=4)
        
        # Add labels and title
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_columns[0] if len(y_columns) == 1 else 'Value')
        
        if title:
            ax.set_title(title)
        
        # Add legend if multiple columns
        if len(y_columns) > 1:
            ax.legend()
        
        # Format date x-axis if applicable
        if pd.api.types.is_datetime64_any_dtype(df[x_column]):
            fig.autofmt_xdate()
            
        # Tight layout for better spacing
        fig.tight_layout()
        
        return fig
    
    def bar_chart(self, data, x_column, y_columns, stacked=False, title=None, **kwargs):
        """
        Render a bar chart using matplotlib.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis
            y_columns: List of columns for y-axis
            stacked: Whether to create a stacked bar chart
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating bar chart with columns: {y_columns}, stacked={stacked}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Width of each bar
        width = 0.8 / len(y_columns) if not stacked else 0.8
        
        # X positions
        x = np.arange(len(df[x_column]))
        
        # Plot each y column
        for i, y_col in enumerate(y_columns):
            if stacked and i > 0:
                # For stacked bars, we need to calculate the bottom position
                bottom = df[y_columns[i-1]].values
                for j in range(i-2, -1, -1):
                    bottom += df[y_columns[j]].values
                ax.bar(x, df[y_col].values, width, label=y_col, bottom=bottom)
            else:
                # For grouped or first stacked bar
                offset = (i - len(y_columns) / 2 + 0.5) * width if not stacked else 0
                ax.bar(x + offset, df[y_col].values, width, label=y_col)
        
        # Set x-axis labels
        ax.set_xticks(x)
        ax.set_xticklabels(df[x_column], rotation=45 if len(df) > 10 else 0, ha='right')
        
        # Add labels and title
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_columns[0] if len(y_columns) == 1 else 'Value')
        
        if title:
            ax.set_title(title)
        
        # Add legend if multiple columns
        if len(y_columns) > 1:
            ax.legend()
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def scatter_plot(self, data, x_column, y_column, size_column=None, 
                    color_column=None, title=None, **kwargs):
        """
        Render a scatter plot using matplotlib.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis
            y_column: Column for y-axis
            size_column: Column for point sizes
            color_column: Column for point colors
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating scatter plot with {x_column} vs {y_column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Prepare sizes if provided
        sizes = None
        if size_column and size_column in df.columns:
            # Normalize sizes between 20 and 200
            min_val = df[size_column].min()
            max_val = df[size_column].max()
            if min_val != max_val:
                sizes = 20 + 180 * (df[size_column] - min_val) / (max_val - min_val)
            else:
                sizes = 100  # Default size if all values are the same
        
        # Prepare colors if provided
        colors = None
        if color_column and color_column in df.columns:
            colors = df[color_column]
        
        # Create the scatter plot
        scatter = ax.scatter(
            df[x_column], 
            df[y_column],
            s=sizes,
            c=colors,
            alpha=0.7,
            **kwargs
        )
        
        # Add colorbar if colors are provided
        if colors is not None:
            plt.colorbar(scatter, ax=ax, label=color_column)
        
        # Add labels and title
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        
        if title:
            ax.set_title(title)
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def pie_chart(self, data, value_column, label_column=None, title=None, **kwargs):
        """
        Render a pie chart using matplotlib.
        
        Args:
            data: The processed data dictionary
            value_column: Column with values for slices
            label_column: Column with labels for slices
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating pie chart with {value_column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Prepare labels
        labels = None
        if label_column and label_column in df.columns:
            labels = df[label_column]
        
        # Create the pie chart
        ax.pie(
            df[value_column],
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            shadow=False,
            **kwargs
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        if title:
            ax.set_title(title)
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def heatmap(self, data, x_column, y_column, value_column=None, 
               colormap='viridis', title=None, **kwargs):
        """
        Render a heatmap using matplotlib.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis categories
            y_column: Column for y-axis categories
            value_column: Column for cell values
            colormap: Name of the colormap to use
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating heatmap with {x_column}, {y_column}, {value_column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create pivot table if not already pivoted
        if y_column and value_column:
            pivot_df = df.pivot(index=y_column, columns=x_column, values=value_column)
        elif y_column:
            # If no value column provided, try to use all numeric columns as values
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            numeric_cols = [col for col in numeric_cols 
                          if col != x_column and col != y_column]
            
            if not numeric_cols:
                raise ValueError("No numeric columns found for heatmap values")
                
            pivot_df = df.pivot(index=y_column, columns=x_column, values=numeric_cols[0])
        else:
            # Assume data is already in matrix form
            pivot_df = df
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Create the heatmap
        im = ax.imshow(pivot_df, cmap=colormap, aspect='auto')
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        
        # Add labels to the axes
        ax.set_xticks(np.arange(len(pivot_df.columns)))
        ax.set_yticks(np.arange(len(pivot_df.index)))
        ax.set_xticklabels(pivot_df.columns, rotation=45, ha='right')
        ax.set_yticklabels(pivot_df.index)
        
        if title:
            ax.set_title(title)
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def histogram(self, data, column, bins=10, density=False, title=None, **kwargs):
        """
        Render a histogram using matplotlib.
        
        Args:
            data: The processed data dictionary
            column: Column to plot the distribution of
            bins: Number of bins or list of bin edges
            density: Whether to normalize the histogram
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating histogram for {column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Create the histogram
        ax.hist(
            df[column], 
            bins=bins, 
            density=density,
            alpha=0.7,
            edgecolor='black',
            **kwargs
        )
        
        # Add labels and title
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency' if not density else 'Density')
        
        if title:
            ax.set_title(title)
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def boxplot(self, data, value_columns, group_column=None, title=None, **kwargs):
        """
        Render a boxplot using matplotlib.
        
        Args:
            data: The processed data dictionary
            value_columns: Columns to show distributions for
            group_column: Column to group boxplots by
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating boxplot for {value_columns}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        if group_column:
            # Grouped boxplot
            grouped_data = []
            labels = []
            
            for value_col in value_columns:
                for group in df[group_column].unique():
                    group_data = df[df[group_column] == group][value_col].dropna()
                    grouped_data.append(group_data)
                    labels.append(f"{value_col} - {group}")
            
            # Create the boxplot
            ax.boxplot(grouped_data, labels=labels, **kwargs)
            plt.xticks(rotation=45, ha='right')
        else:
            # Simple boxplot for multiple columns
            data_to_plot = [df[col].dropna() for col in value_columns]
            
            # Create the boxplot
            ax.boxplot(data_to_plot, labels=value_columns, **kwargs)
        
        # Add labels and title
        if group_column:
            ax.set_xlabel(f"{group_column} by {', '.join(value_columns)}")
        else:
            ax.set_xlabel('Variables')
        ax.set_ylabel('Value')
        
        if title:
            ax.set_title(title)
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def correlation_matrix(self, data, columns=None, method='pearson', title=None, **kwargs):
        """
        Render a correlation matrix using matplotlib.
        
        Args:
            data: The processed data dictionary
            columns: List of columns to include
            method: Correlation method ('pearson', 'kendall', 'spearman')
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating correlation matrix with method {method}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Select columns for correlation
        if columns:
            selected_df = df[columns].select_dtypes(include=[np.number])
        else:
            selected_df = df.select_dtypes(include=[np.number])
        
        # Calculate correlation matrix
        corr_matrix = selected_df.corr(method=method)
        
        # Create figure and axis
        fig, ax = self._create_figure()
        
        # Create heatmap of correlation matrix
        im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label(f'{method.capitalize()} Correlation')
        
        # Set labels
        ax.set_xticks(np.arange(len(corr_matrix.columns)))
        ax.set_yticks(np.arange(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr_matrix.columns)
        
        # Add correlation values in the cells
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                       ha='center', va='center', 
                       color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
        
        if title:
            ax.set_title(title)
            
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def multiple_charts(self, data, chart_configs, layout=None, title=None, **kwargs):
        """
        Create multiple charts in a single figure.
        
        Args:
            data: The processed data dictionary (optional)
            chart_configs: List of chart configurations
            layout: Layout configuration for the charts (rows, cols)
            title: Overall title
            **kwargs: Additional parameters
            
        Returns:
            Matplotlib figure object
        """
        logger.debug(f"Creating multiple charts with {len(chart_configs)} configs")
        
        # Determine layout
        if layout and 'rows' in layout and 'cols' in layout:
            rows = layout['rows']
            cols = layout['cols']
        else:
            # Auto-calculate layout based on number of charts
            n_charts = len(chart_configs)
            cols = min(3, n_charts)  # Max 3 columns
            rows = (n_charts + cols - 1) // cols  # Ceiling division
        
        # Create figure with subplots
        fig, axes = plt.subplots(rows, cols, figsize=(cols*5, rows*4))
        
        # Make axes accessible as a 1D array
        if rows == 1 and cols == 1:
            axes = np.array([axes])
        elif rows == 1:
            axes = np.array([ax for ax in axes])
        elif cols == 1:
            axes = np.array([ax for ax in axes])
        axes = axes.flatten()
        
        # Create each chart
        for i, config in enumerate(chart_configs):
            if i >= len(axes):
                logger.warning(f"More charts than available axes, skipping after {i}")
                break
                
            ax = axes[i]
            
            # Handle either pre-created charts or configs to create charts
            if 'chart' in config and isinstance(config['chart'], Figure):
                # Extract the existing figure and copy to this axis
                existing_fig = config['chart']
                for ax_src in existing_fig.get_axes():
                    # Copy contents of the source axis to our target axis
                    for collection in ax_src.collections:
                        ax.add_collection(collection.copy())
                    for line in ax_src.lines:
                        ax.add_line(line.copy())
                    for patch in ax_src.patches:
                        ax.add_patch(patch.copy())
                    
                    # Copy axis labels and title
                    ax.set_xlabel(ax_src.get_xlabel())
                    ax.set_ylabel(ax_src.get_ylabel())
                    if ax_src.get_title():
                        ax.set_title(ax_src.get_title())
                    
                    # Only copy from the first axis if there are multiple
                    break
            elif 'type' in config and 'data' in config:
                # Create a new chart based on config
                chart_type = config['type']
                chart_data = config['data']
                
                # Call the appropriate chart creation method
                if hasattr(self, f"{chart_type}_chart"):
                    chart_method = getattr(self, f"{chart_type}_chart")
                    
                    # Extract parameters for the chart method
                    method_params = {k: v for k, v in config.items() 
                                 if k not in ['type', 'data']}
                    
                    # Create the chart directly on the axis
                    chart_method(data=chart_data, ax=ax, **method_params)
                else:
                    ax.text(0.5, 0.5, f"Unsupported chart type: {chart_type}",
                           ha='center', va='center')
            else:
                ax.text(0.5, 0.5, "Invalid chart configuration",
                       ha='center', va='center')
            
            # Add chart title if specified in config
            if 'title' in config and not ax.get_title():
                ax.set_title(config['title'])
        
        # Hide any unused axes
        for i in range(len(chart_configs), len(axes)):
            axes[i].set_visible(False)
        
        # Add overall title if provided
        if title:
            fig.suptitle(title, fontsize=16)
            
        # Adjust layout
        fig.tight_layout()
        if title:
            # Add space for title
            fig.subplots_adjust(top=0.9)
        
        return fig
    
    def export(self, fig, output_format, output_path=None):
        """
        Export the figure to the specified format.
        
        Args:
            fig: The matplotlib figure to export
            output_format: Format to export to ('png', 'svg', 'pdf', etc.)
            output_path: Path to save the file (optional)
            
        Returns:
            Path to the exported file
        """
        logger.debug(f"Exporting figure to {output_format}")
        
        if output_path is None:
            # Generate a temporary file path
            import tempfile
            output_dir = tempfile.mkdtemp()
            filename = f"viz_{id(fig)}.{output_format}"
            output_path = os.path.join(output_dir, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the figure
        fig.savefig(output_path, format=output_format, bbox_inches='tight', dpi=300)
        
        # Close the figure to free memory
        plt.close(fig)
        
        return output_path

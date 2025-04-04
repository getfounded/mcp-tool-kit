"""
Plotly renderer for DataViz service.

This module provides visualization rendering using plotly.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class PlotlyRenderer:
    """Renderer implementation using Plotly."""
    
    def __init__(self, service):
        """
        Initialize with parent service reference.
        
        Args:
            service: The parent DataVizService instance
        """
        self.service = service
        self._configure()
        
    def _configure(self):
        """Configure plotly settings."""
        # Use white template for better readability
        pio.templates.default = "plotly_white"
        
        logger.debug("PlotlyRenderer configured")
    
    def line_chart(self, data, x_column, y_columns, title=None, **kwargs):
        """
        Render a line chart using plotly.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis
            y_columns: List of columns for y-axis
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"Creating line chart with columns: {y_columns}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure
        fig = go.Figure()
        
        # Add each line series
        for y_col in y_columns:
            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=df[y_col],
                    mode='lines+markers',
                    name=y_col
                )
            )
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title=x_column,
            yaxis_title=y_columns[0] if len(y_columns) == 1 else 'Value',
            legend_title='Series',
            hovermode='closest'
        )
        
        # Format date axis if applicable
        if pd.api.types.is_datetime64_any_dtype(df[x_column]):
            fig.update_xaxes(
                rangeslider_visible=False,
                tickformatstops=[
                    dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
                    dict(dtickrange=[1000, 60000], value="%H:%M:%S"),
                    dict(dtickrange=[60000, 3600000], value="%H:%M"),
                    dict(dtickrange=[3600000, 86400000], value="%H:%M"),
                    dict(dtickrange=[86400000, 604800000], value="%e %b"),
                    dict(dtickrange=[604800000, "M1"], value="%e %b"),
                    dict(dtickrange=["M1", "M12"], value="%b '%y"),
                    dict(dtickrange=["M12", None], value="%Y")
                ]
            )
        
        return fig
    
    def bar_chart(self, data, x_column, y_columns, stacked=False, title=None, **kwargs):
        """
        Render a bar chart using plotly.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis
            y_columns: List of columns for y-axis
            stacked: Whether to create a stacked bar chart
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"Creating bar chart with columns: {y_columns}, stacked={stacked}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create figure
        fig = go.Figure()
        
        # Add each bar series
        for i, y_col in enumerate(y_columns):
            fig.add_trace(
                go.Bar(
                    x=df[x_column],
                    y=df[y_col],
                    name=y_col
                )
            )
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title=x_column,
            yaxis_title=y_columns[0] if len(y_columns) == 1 else 'Value',
            legend_title='Series',
            barmode='stack' if stacked else 'group'
        )
        
        return fig
    
    def scatter_plot(self, data, x_column, y_column, size_column=None, 
                    color_column=None, title=None, **kwargs):
        """
        Render a scatter plot using plotly.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis
            y_column: Column for y-axis
            size_column: Column for point sizes
            color_column: Column for point colors
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"Creating scatter plot with {x_column} vs {y_column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create the scatter plot
        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            size=size_column,
            color=color_column,
            title=title,
            hover_data=df.columns
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column
        )
        
        return fig
    
    def pie_chart(self, data, value_column, label_column=None, title=None, **kwargs):
        """
        Render a pie chart using plotly.
        
        Args:
            data: The processed data dictionary
            value_column: Column with values for slices
            label_column: Column with labels for slices
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"Creating pie chart with {value_column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create the pie chart
        fig = px.pie(
            df,
            values=value_column,
            names=label_column,
            title=title,
            hover_data=df.columns
        )
        
        # Update layout
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def heatmap(self, data, x_column, y_column, value_column=None, 
               colormap='viridis', title=None, **kwargs):
        """
        Render a heatmap using plotly.
        
        Args:
            data: The processed data dictionary
            x_column: Column for x-axis categories
            y_column: Column for y-axis categories
            value_column: Column for cell values
            colormap: Name of the colormap to use
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
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
        
        # Create the heatmap
        fig = px.imshow(
            pivot_df,
            color_continuous_scale=colormap,
            labels=dict(color=value_column or "Value"),
            x=pivot_df.columns,
            y=pivot_df.index,
            title=title
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column
        )
        
        return fig
    
    def histogram(self, data, column, bins=10, density=False, title=None, **kwargs):
        """
        Render a histogram using plotly.
        
        Args:
            data: The processed data dictionary
            column: Column to plot the distribution of
            bins: Number of bins or list of bin edges
            density: Whether to normalize the histogram
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"Creating histogram for {column}")
        
        # Extract the DataFrame
        df = data['data']
        
        # Create the histogram
        fig = px.histogram(
            df,
            x=column,
            nbins=bins if isinstance(bins, int) else None,
            histnorm='probability density' if density else None,
            title=title
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title=column,
            yaxis_title='Density' if density else 'Count'
        )
        
        return fig
    
    def boxplot(self, data, value_columns, group_column=None, title=None, **kwargs):
        """
        Render a boxplot using plotly.
        
        Args:
            data: The processed data dictionary
            value_columns: Columns to show distributions for
            group_column: Column to group boxplots by
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"Creating boxplot for {value_columns}")
        
        # Extract the DataFrame
        df = data['data']
        
        if group_column:
            # Need to melt the DataFrame for grouped boxplot
            melted_df = pd.melt(
                df,
                id_vars=[group_column],
                value_vars=value_columns,
                var_name='Variable',
                value_name='Value'
            )
            
            fig = px.box(
                melted_df,
                x='Variable',
                y='Value',
                color=group_column,
                title=title
            )
        else:
            # Simple boxplot for multiple columns
            fig = go.Figure()
            
            for col in value_columns:
                fig.add_trace(go.Box(
                    y=df[col],
                    name=col,
                    boxmean=True  # adds mean as a dashed line
                ))
            
            fig.update_layout(title=title)
        
        return fig
    
    def correlation_matrix(self, data, columns=None, method='pearson', title=None, **kwargs):
        """
        Render a correlation matrix using plotly.
        
        Args:
            data: The processed data dictionary
            columns: List of columns to include
            method: Correlation method ('pearson', 'kendall', 'spearman')
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
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
        
        # Create heatmap of correlation matrix
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            title=title
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Variables",
            yaxis_title="Variables"
        )
        
        return fig
    
    def candlestick_chart(self, data, open_col, high_col, low_col, close_col, 
                         volume_col=None, title=None, **kwargs):
        """
        Render a candlestick chart using plotly.
        
        Args:
            data: The processed data dictionary
            open_col: Column with opening prices
            high_col: Column with high prices
            low_col: Column with low prices
            close_col: Column with closing prices
            volume_col: Column with volume data (optional)
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug("Creating candlestick chart")
        
        # Extract the DataFrame
        df = data['data']
        
        # Ensure the date column is in the first position
        date_col = df.columns[0]
        
        fig = go.Figure()
        
        # Add candlestick trace
        fig.add_trace(go.Candlestick(
            x=df[date_col],
            open=df[open_col],
            high=df[high_col],
            low=df[low_col],
            close=df[close_col],
            name='Price'
        ))
        
        # Add volume trace if requested
        if volume_col and volume_col in df.columns:
            # Create a secondary y-axis for volume
            fig.add_trace(go.Bar(
                x=df[date_col],
                y=df[volume_col],
                name='Volume',
                yaxis='y2',
                marker_color='rgba(0, 0, 255, 0.3)'
            ))
            
            # Update layout for dual y-axis
            fig.update_layout(
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right'
                )
            )
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title=date_col,
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def ohlc_chart(self, data, open_col, high_col, low_col, close_col, 
                  volume_col=None, title=None, **kwargs):
        """
        Render an OHLC chart using plotly.
        
        Args:
            data: The processed data dictionary
            open_col: Column with opening prices
            high_col: Column with high prices
            low_col: Column with low prices
            close_col: Column with closing prices
            volume_col: Column with volume data (optional)
            title: Chart title
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure object
        """
        logger.debug("Creating OHLC chart")
        
        # Extract the DataFrame
        df = data['data']
        
        # Ensure the date column is in the first position
        date_col = df.columns[0]
        
        fig = go.Figure()
        
        # Add OHLC trace
        fig.add_trace(go.Ohlc(
            x=df[date_col],
            open=df[open_col],
            high=df[high_col],
            low=df[low_col],
            close=df[close_col],
            name='Price'
        ))
        
        # Add volume trace if requested
        if volume_col and volume_col in df.columns:
            # Create a secondary y-axis for volume
            fig.add_trace(go.Bar(
                x=df[date_col],
                y=df[volume_col],
                name='Volume',
                yaxis='y2',
                marker_color='rgba(0, 0, 255, 0.3)'
            ))
            
            # Update layout for dual y-axis
            fig.update_layout(
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right'
                )
            )
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title=date_col,
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
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
            Plotly figure object
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
        
        # Create subplot figure
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=rows, 
            cols=cols,
            subplot_titles=[config.get('title', f'Chart {i+1}') 
                           for i, config in enumerate(chart_configs)]
        )
        
        # Add each chart to the subplots
        for i, config in enumerate(chart_configs):
            # Calculate row and column
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            # Handle either pre-created charts or configs to create charts
            if 'chart' in config and isinstance(config['chart'], go.Figure):
                # Copy traces from existing figure
                for trace in config['chart'].data:
                    fig.add_trace(trace, row=row, col=col)
                    
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
                    
                    # Create the chart
                    temp_fig = chart_method(data=chart_data, **method_params)
                    
                    # Add each trace to the subplot
                    for trace in temp_fig.data:
                        fig.add_trace(trace, row=row, col=col)
                    
                    # Copy layout elements as needed
                    # (titles are already handled by subplot_titles)
                else:
                    # Add a blank chart with error text
                    fig.add_annotation(
                        text=f"Unsupported chart type: {chart_type}",
                        x=0.5, y=0.5,
                        xref=f"x{i+1}", yref=f"y{i+1}",
                        showarrow=False,
                        row=row, col=col
                    )
            else:
                # Add a blank chart with error text
                fig.add_annotation(
                    text="Invalid chart configuration",
                    x=0.5, y=0.5,
                    xref=f"x{i+1}", yref=f"y{i+1}",
                    showarrow=False,
                    row=row, col=col
                )
        
        # Update layout
        fig.update_layout(
            title=title,
            showlegend=True,
            height=300 * rows,
            width=400 * cols
        )
        
        return fig
    
    def export(self, fig, output_format, output_path=None):
        """
        Export the figure to the specified format.
        
        Args:
            fig: The plotly figure to export
            output_format: Format to export to ('png', 'svg', 'pdf', 'html', 'json')
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
        
        # Handle different output formats
        if output_format == 'html':
            final_path = f"{os.path.splitext(output_path)[0]}.html"
            fig.write_html(final_path, include_plotlyjs=True, full_html=True)
        elif output_format == 'json':
            final_path = f"{os.path.splitext(output_path)[0]}.json"
            with open(final_path, 'w') as f:
                json.dump(fig.to_dict(), f)
        elif output_format in ['png', 'jpg', 'jpeg', 'webp', 'svg', 'pdf']:
            final_path = output_path
            fig.write_image(final_path, engine="kaleido")
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        return final_path

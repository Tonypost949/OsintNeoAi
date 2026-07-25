import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd

def plot_timeline(timeline_data: List[Dict], timeline_type: str = "general") -> go.Figure:
    """Create a timeline visualization using Plotly.
    
    Args:
        timeline_data: List of timeline events
        timeline_type: Type of timeline (agricultural, commercial, or general)
        
    Returns:
        Plotly figure object
    """
    if not timeline_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title=f"No {timeline_type.capitalize()} Timeline Data Available",
            xaxis_title="Year",
            yaxis_title="Property",
            height=400
        )
        return fig
    
    # Create DataFrame from timeline data
    df = pd.DataFrame(timeline_data)
    
    # Extract start and end years from time_period
    years = []
    for period in df['time_period']:
        if '-' in str(period):
            start, end = period.split('-')
            try:
                years.append((int(start), int(end)))
            except ValueError:
                # Handle non-numeric years
                years.append((0, 0))
        else:
            try:
                year = int(period)
                years.append((year, year))
            except ValueError:
                # Handle non-numeric years
                years.append((0, 0))
    
    df['start_year'] = [y[0] for y in years]
    df['end_year'] = [y[1] for y in years]
    
    # Sort by start year
    df = df.sort_values('start_year')
    
    # Create unique identifiers for each address
    addresses = df['address'].unique()
    address_map = {addr: i for i, addr in enumerate(addresses)}
    df['y_pos'] = df['address'].map(address_map)
    
    # Color mapping based on timeline type
    if timeline_type == "agricultural":
        color_map = {
            "Farming": "green",
            "Irrigation": "blue",
            "Harvest": "gold",
            "Purchase": "purple"
        }
        default_color = "darkgreen"
    elif timeline_type == "commercial":
        color_map = {
            "Store": "red",
            "Factory": "brown",
            "Office": "blue",
            "Warehouse": "orange"
        }
        default_color = "darkred"
    else:
        color_map = {}
        default_color = "gray"
    
    # Determine color for each event
    def get_color(event):
        for key, color in color_map.items():
            if key.lower() in event.lower():
                return color
        return default_color
    
    df['color'] = df['event'].apply(get_color)
    
    # Create figure
    fig = go.Figure()
    
    # Add events as bars on timeline
    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row['end_year'] - row['start_year']],
            y=[row['y_pos']],
            base=[row['start_year']],
            orientation='h',
            marker_color=row['color'],
            name=row['event'],
            hovertemplate=f"<b>{row['event']}</b><br>" +
                          f"Period: {row['time_period']}<br>" +
                          f"Address: {row['address']}<br>" +
                          f"{row['details']}<extra></extra>",
            showlegend=False
        ))
    
    # Add property addresses on y-axis
    fig.update_layout(
        title=f"{timeline_type.capitalize()} Timeline",
        xaxis_title="Year",
        yaxis=dict(
            tickmode='array',
            tickvals=list(address_map.values()),
            ticktext=list(address_map.keys()),
            title="Property"
        ),
        hovermode="closest",
        height=400 + (len(addresses) * 40)  # Adjust height based on number of properties
    )
    
    return fig

def plot_crop_comparison(crop_data: Dict[str, List[Dict]]) -> go.Figure:
    """Create a visualization comparing crops across properties.
    
    Args:
        crop_data: Dictionary of crop data by crop type
        
    Returns:
        Plotly figure object
    """
    if not crop_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No Crop Comparison Data Available",
            xaxis_title="Year",
            yaxis_title="Crop Type",
            height=400
        )
        return fig
    
    # Prepare data for visualization
    plot_data = []
    for crop, entries in crop_data.items():
        for entry in entries:
            plot_data.append({
                "crop": crop,
                "address": entry["address"],
                "start_year": entry["start_year"],
                "end_year": entry["end_year"],
                "acreage": entry["acreage"],
                "duration": entry["end_year"] - entry["start_year"] + 1  # Include both start and end years
            })
    
    if not plot_data:
        # Return empty figure if no plot data
        fig = go.Figure()
        fig.update_layout(
            title="No Crop Comparison Data Available",
            xaxis_title="Year",
            yaxis_title="Crop Type",
            height=400
        )
        return fig
    
    df = pd.DataFrame(plot_data)
    
    # Create a grouped bar chart
    fig = px.bar(
        df, 
        x="address", 
        y="acreage", 
        color="crop",
        title="Crop Comparison by Property",
        labels={"address": "Property", "acreage": "Acreage", "crop": "Crop Type"},
        height=500,
        hover_data=["start_year", "end_year", "duration"]
    )
    
    # Add text labels on bars
    fig.update_traces(texttemplate='%{y} acres', textposition='outside')
    
    # Improve layout
    fig.update_layout(
        barmode='group',
        xaxis_tickangle=-45,
        legend_title="Crop Types"
    )
    
    return fig

def plot_business_evolution(business_data: List[Dict]) -> go.Figure:
    """Create a visualization showing business evolution over time.
    
    Args:
        business_data: List of business evolution data by property
        
    Returns:
        Plotly figure object
    """
    if not business_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No Business Evolution Data Available",
            xaxis_title="Year",
            yaxis_title="Property",
            height=400
        )
        return fig
    
    # Prepare data for timeline visualization
    plot_data = []
    
    for property_data in business_data:
        address = property_data["address"]
        
        for business in property_data["evolution"]:
            time_period = business["time_period"]
            
            # Parse time period
            if "-" in time_period:
                start_year, end_year = map(int, time_period.split("-"))
            else:
                start_year = end_year = int(time_period)
            
            plot_data.append({
                "address": address,
                "start_year": start_year,
                "end_year": end_year,
                "business_name": business["business_name"],
                "business_type": business["business_type"],
                "details": business.get("transition", "")
            })
    
    if not plot_data:
        # Return empty figure if no plot data
        fig = go.Figure()
        fig.update_layout(
            title="No Business Evolution Data Available",
            xaxis_title="Year",
            yaxis_title="Property",
            height=400
        )
        return fig
        
    df = pd.DataFrame(plot_data)
    
    # Create unique identifiers for each address
    addresses = df['address'].unique()
    address_map = {addr: i for i, addr in enumerate(addresses)}
    df['y_pos'] = df['address'].map(address_map)
    
    # Create figure
    fig = go.Figure()
    
    # Color map based on business types
    business_types = df['business_type'].unique()
    colors = px.colors.qualitative.Plotly[:len(business_types)]
    color_map = {biz_type: color for biz_type, color in zip(business_types, colors)}
    
    # Add businesses as bars on timeline
    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row['end_year'] - row['start_year']],
            y=[row['y_pos']],
            base=[row['start_year']],
            orientation='h',
            marker_color=color_map.get(row['business_type'], 'gray'),
            name=row['business_type'],
            text=row['business_name'],
            hovertemplate=f"<b>{row['business_name']}</b><br>" +
                          f"Type: {row['business_type']}<br>" +
                          f"Period: {row['start_year']}-{row['end_year']}<br>" +
                          f"{row['details']}<extra></extra>",
        ))
    
    # Create legend based on business types
    for biz_type, color in color_map.items():
        fig.add_trace(go.Bar(
            x=[0], y=[0],
            marker_color=color,
            name=biz_type,
            showlegend=True,
            visible='legendonly'
        ))
    
    # Add property addresses on y-axis
    fig.update_layout(
        title="Business Evolution Timeline",
        xaxis_title="Year",
        yaxis=dict(
            tickmode='array',
            tickvals=list(address_map.values()),
            ticktext=list(address_map.keys()),
            title="Property"
        ),
        barmode='overlay',
        hovermode="closest",
        height=400 + (len(addresses) * 40),  # Adjust height based on number of properties
        legend_title="Business Types"
    )
    
    return fig

def create_interactive_timeline(property_data: Dict) -> go.Figure:
    """Create an interactive timeline visualization that combines all property events.
    
    Args:
        property_data: Dictionary containing comprehensive property data
        
    Returns:
        Plotly figure object with interactive timeline
    """
    if not property_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No Property Data Available for Timeline",
            xaxis_title="Year",
            yaxis_title="Event Category",
            height=500
        )
        return fig
    
    # Extract all relevant events from different categories
    timeline_events = []
    
    # Property basic info
    address = property_data.get("address", "Unknown Address")
    start_year = property_data.get("start_year", 1900)
    end_year = property_data.get("end_year", 2025)
    
    # Add property existence as baseline
    timeline_events.append({
        "category": "Property",
        "event": f"Property Existence",
        "start_year": start_year,
        "end_year": end_year,
        "details": f"Property record period: {start_year}-{end_year}",
        "color": "gray",
        "order": 0  # For y-axis ordering
    })
    
    # Agricultural data
    if "agricultural_data" in property_data and property_data["agricultural_data"]:
        for idx, item in enumerate(property_data["agricultural_data"]):
            # Parse time period
            period = item.get("time_period", "")
            if "-" in period:
                ag_start, ag_end = map(int, period.split("-"))
            else:
                try:
                    ag_start = ag_end = int(period)
                except (ValueError, TypeError):
                    continue  # Skip if can't parse time period
            
            timeline_events.append({
                "category": "Agriculture",
                "event": f"{item.get('crop_type', 'Crop')}",
                "start_year": ag_start,
                "end_year": ag_end,
                "details": f"Crop: {item.get('crop_type', 'Unknown')}<br>" +
                           f"Acreage: {item.get('acreage', 'Unknown')}<br>" +
                           f"Soil: {item.get('soil_type', 'Unknown')}<br>" +
                           f"Irrigation: {item.get('irrigation', 'Unknown')}<br>" +
                           f"Yield: {item.get('annual_yield', 'Unknown')}",
                "color": "green",
                "order": 1
            })
    
    # Commercial usage
    if "commercial_usage" in property_data and property_data["commercial_usage"]:
        for idx, item in enumerate(property_data["commercial_usage"]):
            # Parse time period
            period = item.get("time_period", "")
            if "-" in period:
                com_start, com_end = map(int, period.split("-"))
            else:
                try:
                    com_start = com_end = int(period)
                except (ValueError, TypeError):
                    continue  # Skip if can't parse time period
            
            timeline_events.append({
                "category": "Business",
                "event": f"{item.get('business_name', 'Business')}",
                "start_year": com_start,
                "end_year": com_end,
                "details": f"Business: {item.get('business_name', 'Unknown')}<br>" +
                           f"Type: {item.get('business_type', 'Unknown')}<br>" +
                           f"Activity: {item.get('commercial_activity', 'Unknown')}<br>" +
                           f"Employees: {item.get('employees', 'Unknown')}",
                "color": "blue",
                "order": 2
            })
    
    # Historical events
    if "historical_events" in property_data and property_data["historical_events"]:
        for idx, item in enumerate(property_data["historical_events"]):
            # Historical events typically have a single date rather than a range
            try:
                event_year = int(item.get("date", 0))
                timeline_events.append({
                    "category": "Historical",
                    "event": f"{item.get('description', 'Event')}",
                    "start_year": event_year,
                    "end_year": event_year,
                    "details": item.get("details", ""),
                    "color": "red",
                    "order": 3,
                    "is_point": True  # Flag as point event rather than range
                })
            except (ValueError, TypeError):
                continue  # Skip if can't parse date
    
    # Property values
    if "value_history" in property_data and property_data["value_history"]:
        for idx, item in enumerate(property_data["value_history"]):
            try:
                value_year = int(item.get("year", 0))
                value = item.get("assessed_value", 0)
                timeline_events.append({
                    "category": "Valuation",
                    "event": f"${value:,.2f}",
                    "start_year": value_year,
                    "end_year": value_year,
                    "details": f"Assessed value: ${value:,.2f}",
                    "color": "purple",
                    "order": 4,
                    "is_point": True  # Flag as point event rather than range
                })
            except (ValueError, TypeError):
                continue  # Skip if can't parse year
    
    # Water wells
    if "water_wells" in property_data and property_data["water_wells"]:
        for idx, item in enumerate(property_data["water_wells"]):
            try:
                well_year = int(item.get("installation_year", 0))
                timeline_events.append({
                    "category": "Water Well",
                    "event": f"Well Installation",
                    "start_year": well_year,
                    "end_year": well_year,
                    "details": f"Depth: {item.get('depth', 'Unknown')} ft<br>" +
                               f"Water Quality: {item.get('water_quality', 'Unknown')}<br>" +
                               f"Flow Rate: {item.get('flow_rate', 'Unknown')}<br>" +
                               f"Status: {item.get('status', 'Unknown')}<br>" +
                               f"{item.get('notes', '')}",
                    "color": "cyan",
                    "order": 5,
                    "is_point": True  # Flag as point event rather than range
                })
            except (ValueError, TypeError):
                continue  # Skip if can't parse year
    
    # Newspaper archives
    if "newspaper_archives" in property_data and property_data["newspaper_archives"]:
        for idx, item in enumerate(property_data["newspaper_archives"]):
            # Try to extract year from date string
            date_str = item.get("date", "")
            try:
                if "-" in date_str:
                    news_year = int(date_str.split("-")[0])
                else:
                    news_year = int(date_str)
                
                timeline_events.append({
                    "category": "News",
                    "event": f"{item.get('headline', 'News Article')}",
                    "start_year": news_year,
                    "end_year": news_year,
                    "details": f"Source: {item.get('source', 'Unknown')}<br>" +
                               f"Date: {date_str}<br>" +
                               f"{item.get('snippet', '')}",
                    "color": "orange",
                    "order": 6,
                    "is_point": True  # Flag as point event rather than range
                })
            except (ValueError, TypeError):
                continue  # Skip if can't parse date
    
    # Web archives
    if "web_archives" in property_data and property_data["web_archives"]:
        for idx, item in enumerate(property_data["web_archives"]):
            # Try to extract year from date string
            date_str = item.get("date", "")
            try:
                if "-" in date_str:
                    web_year = int(date_str.split("-")[0])
                else:
                    web_year = int(date_str)
                
                timeline_events.append({
                    "category": "Web",
                    "event": f"{item.get('title', 'Web Archive')}",
                    "start_year": web_year,
                    "end_year": web_year,
                    "details": f"URL: {item.get('url', 'Unknown')}<br>" +
                               f"Date: {date_str}<br>" +
                               f"{item.get('snippet', '')}",
                    "color": "brown",
                    "order": 7,
                    "is_point": True  # Flag as point event rather than range
                })
            except (ValueError, TypeError):
                continue  # Skip if can't parse date
    
    if not timeline_events:
        # Return empty figure if no events
        fig = go.Figure()
        fig.update_layout(
            title=f"No Timeline Data Available for {address}",
            xaxis_title="Year",
            yaxis_title="Event Category",
            height=500
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(timeline_events)
    
    # Sort by category order for y-axis
    df = df.sort_values("order")
    
    # Define category colors
    category_colors = {
        "Property": "gray",
        "Agriculture": "green",
        "Business": "blue",
        "Historical": "red",
        "Valuation": "purple",
        "Water Well": "cyan",
        "News": "orange",
        "Web": "brown"
    }
    
    # Create interactive figure
    fig = go.Figure()
    
    # Add range events (bars)
    range_events = df[~df.get("is_point", False)]
    for idx, row in range_events.iterrows():
        fig.add_trace(go.Bar(
            x=[row['end_year'] - row['start_year']],  # Width of bar
            y=[row['category']],
            base=[row['start_year']],  # Start position of bar
            orientation='h',
            marker_color=category_colors.get(row['category'], row['color']),
            name=row['event'],
            text=row['event'],
            hovertemplate=(
                f"<b>{row['event']}</b><br>" +
                f"Period: {row['start_year']}-{row['end_year']}<br>" +
                f"{row['details']}<extra></extra>"
            ),
            showlegend=False
        ))
    
    # Add point events (markers)
    point_events = df[df.get("is_point", False)]
    for category in point_events['category'].unique():
        cat_events = point_events[point_events['category'] == category]
        
        fig.add_trace(go.Scatter(
            x=cat_events['start_year'],
            y=[category] * len(cat_events),
            mode='markers',
            marker=dict(
                color=category_colors.get(category, 'gray'),
                size=12,
                symbol='diamond'
            ),
            name=category,
            text=cat_events['event'],
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Year: %{x}<br>" +
                "%{customdata}<extra></extra>"
            ),
            customdata=cat_events['details'],
            showlegend=False
        ))
    
    # Add a trace for each category for the legend
    for category, color in category_colors.items():
        if category in df['category'].values:
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=category,
                showlegend=True
            ))
    
    # Calculate year range for x-axis
    min_year = df['start_year'].min() - 5
    max_year = df['end_year'].max() + 5
    
    # Improve layout
    fig.update_layout(
        title=f"Interactive Timeline for {address}",
        xaxis=dict(
            title="Year",
            range=[min_year, max_year],
            tickmode='linear',
            dtick=10  # Decade ticks
        ),
        yaxis=dict(
            title="Event Category",
            categoryorder='array',
            categoryarray=df['category'].unique()
        ),
        height=600,
        hovermode="closest",
        barmode='overlay',
        legend_title="Event Categories",
        margin=dict(l=150)  # Ensure space for category labels
    )
    
    # Add range slider for time navigation
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                thickness=0.05
            )
        )
    )
    
    return fig

def plot_property_valuation(valuation_data: List[Dict]) -> go.Figure:
    """Create a visualization showing property valuation trends over time.
    
    Args:
        valuation_data: List of property valuation data
        
    Returns:
        Plotly figure object
    """
    if not valuation_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No Property Valuation Data Available",
            xaxis_title="Year",
            yaxis_title="Assessed Value ($)",
            height=400
        )
        return fig
    
    # Create figure
    fig = go.Figure()
    
    # Add a line for each property
    for property_data in valuation_data:
        address = property_data["address"]
        years = property_data["years"]
        values = property_data["values"]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=address,
            hovertemplate=f"<b>{address}</b><br>" +
                          "Year: %{x}<br>" +
                          "Value: $%{y:,.2f}<extra></extra>"
        ))
    
    # Improve layout
    fig.update_layout(
        title="Property Valuation Trends",
        xaxis_title="Year",
        yaxis_title="Assessed Value ($)",
        hovermode="closest",
        height=500,
        yaxis=dict(
            tickformat="$,.0f"
        )
    )
    
    return fig

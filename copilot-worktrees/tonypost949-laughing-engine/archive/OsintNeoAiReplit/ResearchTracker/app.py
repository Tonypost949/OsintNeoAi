import streamlit as st
import pandas as pd
import os
import logging
import json
import base64
from datetime import datetime
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
import subprocess

from property_analyzer import FarmingBusinessAnalyzer
from osint_tools import OSINTAnalyzer
from database import get_all_properties, get_property_data, search_properties, add_property
from utils import load_addresses, parse_address_list, validate_year_range
from visualization import (
    plot_timeline, 
    plot_crop_comparison, 
    plot_business_evolution, 
    plot_property_valuation,
    create_interactive_timeline
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("historical_property_app")

# Set page configuration
st.set_page_config(
    page_title="Historical Property Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title and introduction
st.title("Historical Property Analysis")
st.markdown("""
This application analyzes the agricultural and commercial evolution of properties over time.
Upload property addresses or enter them manually, specify a date range, and explore historical patterns.
""")

# Sidebar for application controls
st.sidebar.header("Analysis Controls")

# Input method selection
input_method = st.sidebar.radio(
    "How would you like to input addresses?",
    ["Text file upload", "Manual entry"]
)

addresses = []

# File upload option
if input_method == "Text file upload":
    uploaded_file = st.sidebar.file_uploader("Upload a text file with addresses (one per line)", type=["txt"])
    
    if uploaded_file is not None:
        try:
            # Read the file as a string
            content = StringIO(uploaded_file.getvalue().decode("utf-8"))
            addresses = load_addresses(content)
            
            if addresses:
                st.sidebar.success(f"Loaded {len(addresses)} addresses from file")
            else:
                st.sidebar.error("No valid addresses found in the file")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
            logger.error(f"File upload error: {str(e)}")

# Manual entry option
else:
    # Get all properties from database for the dropdown
    db_properties = get_all_properties()
    saved_addresses = [p['address'] for p in db_properties] if db_properties else []
    
    # Create address selection method
    address_input_method = st.sidebar.radio(
        "Address Input Method",
        ["Select from Database", "Manual Entry", "Both"],
        index=0 if saved_addresses else 1
    )
    
    selected_addresses = []
    
    # Select from database
    if address_input_method in ["Select from Database", "Both"] and saved_addresses:
        selected_db_addresses = st.sidebar.multiselect(
            "Select saved addresses",
            options=saved_addresses,
            default=None
        )
        if selected_db_addresses:
            selected_addresses.extend(selected_db_addresses)
    
    # Manual entry
    if address_input_method in ["Manual Entry", "Both"]:
        # Create searchable address input with autocomplete suggestions
        if saved_addresses:
            # Get an initial input for autocomplete
            manual_address = st.sidebar.text_input(
                "Enter an address (autocomplete enabled)",
                key="address_autocomplete",
                help="Start typing to see suggestions from existing addresses"
            )
            
            # Filter addresses based on current input for suggestions
            filtered_addresses = [addr for addr in saved_addresses if manual_address.lower() in addr.lower()] if manual_address else []
            
            # Display filtered suggestions as a selectbox if we have matches
            if manual_address and filtered_addresses:
                selected_suggestion = st.sidebar.selectbox(
                    "Select from suggestions",
                    options=[""] + filtered_addresses,
                    index=0,
                    key="address_suggestion"
                )
                
                # If a suggestion was selected, use it
                if selected_suggestion:
                    manual_address = selected_suggestion
            
            # Add button to add the current address to the list
            if manual_address:
                if st.sidebar.button("Add Address to Selection"):
                    if manual_address not in selected_addresses:
                        selected_addresses.append(manual_address)
                        st.sidebar.success(f"Added: {manual_address}")
                    else:
                        st.sidebar.warning("Address already in selection")
        
        # Always keep the text area for multiple addresses or for when no saved addresses exist
        address_input = st.sidebar.text_area(
            "Or enter multiple addresses (one per line)", 
            height=150,
            help="Each line should contain one address"
        )
        
        if address_input:
            manual_addresses = parse_address_list(address_input)
            if manual_addresses:
                # Add only addresses that aren't already selected
                for addr in manual_addresses:
                    if addr not in selected_addresses:
                        selected_addresses.append(addr)
        
        # Display currently selected addresses
        if selected_addresses:
            st.sidebar.write("**Currently Selected:**")
            for idx, addr in enumerate(selected_addresses):
                st.sidebar.write(f"{idx+1}. {addr}")
    
    if selected_addresses:
        addresses = selected_addresses
        st.sidebar.success(f"Selected {len(addresses)} addresses")
    else:
        st.sidebar.error("No valid addresses found")

# Date range selection
st.sidebar.subheader("Time Period")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_year = st.number_input("Start Year", min_value=1800, max_value=2023, value=1900, step=1)
with col2:
    end_year = st.number_input("End Year", min_value=1800, max_value=2023, value=1940, step=1)

# Validate year range
if not validate_year_range(start_year, end_year):
    st.sidebar.error("End year must be greater than or equal to start year")

# Run analysis button
run_analysis = st.sidebar.button("Run Analysis", type="primary", disabled=not addresses or not validate_year_range(start_year, end_year))

# About section in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.info(
    "This application analyzes historical property data to track "
    "agricultural and commercial changes over time. "
    "It visualizes trends, compares properties, and generates detailed reports."
)

# Display selected addresses
if addresses:
    st.subheader("Selected Properties")
    for i, addr in enumerate(addresses, 1):
        st.text(f"{i}. {addr}")

# Main analysis section
if run_analysis:
    try:
        with st.spinner("Analyzing property data..."):
            # Create the analyzer
            analyzer = FarmingBusinessAnalyzer(addresses)
            
            # Collect and analyze data
            analyzer.collect_all_data(start_year, end_year)
            results = analyzer.analyze_all()
            
            if not results:
                st.error("No data found for the specified properties and time period.")
            else:
                # Display results in tabs
                tabs = st.tabs([
                    "Timeline Analysis", 
                    "Interactive Timeline",
                    "Crop Patterns", 
                    "Business Evolution", 
                    "Property Valuation",
                    "Water Wells",
                    "OSINT Analysis",
                    "Regional Patterns",
                    "Database Management",
                    "Export Results"
                ])
                
                # Timeline Analysis Tab
                with tabs[0]:
                    st.header("Historical Timeline Analysis")
                    
                    timeline_type = st.radio(
                        "Select timeline type",
                        ["Agricultural", "Commercial", "Combined"],
                        horizontal=True
                    )
                    
                    if timeline_type == "Agricultural":
                        if results["agricultural_timeline"]:
                            st.plotly_chart(plot_timeline(results["agricultural_timeline"], "agricultural"), use_container_width=True)
                            
                            st.subheader("Agricultural Timeline Details")
                            ag_df = pd.DataFrame(results["agricultural_timeline"])
                            st.dataframe(ag_df, use_container_width=True)
                        else:
                            st.info("No agricultural timeline data available.")
                    
                    elif timeline_type == "Commercial":
                        if results["commercial_timeline"]:
                            st.plotly_chart(plot_timeline(results["commercial_timeline"], "commercial"), use_container_width=True)
                            
                            st.subheader("Commercial Timeline Details")
                            com_df = pd.DataFrame(results["commercial_timeline"])
                            st.dataframe(com_df, use_container_width=True)
                        else:
                            st.info("No commercial timeline data available.")
                    
                    else:  # Combined
                        col1, col2 = st.columns(2)
                        with col1:
                            if results["agricultural_timeline"]:
                                st.subheader("Agricultural Timeline")
                                st.plotly_chart(plot_timeline(results["agricultural_timeline"], "agricultural"), use_container_width=True)
                            else:
                                st.info("No agricultural timeline data available.")
                        
                        with col2:
                            if results["commercial_timeline"]:
                                st.subheader("Commercial Timeline")
                                st.plotly_chart(plot_timeline(results["commercial_timeline"], "commercial"), use_container_width=True)
                            else:
                                st.info("No commercial timeline data available.")
                
                # Interactive Timeline Tab
                with tabs[1]:
                    st.header("Interactive Property Timeline")
                    
                    # Allow selection of properties for timeline visualization
                    if "properties" in results:
                        property_options = [p["address"] for p in results["properties"]]
                        
                        if property_options:
                            selected_property = st.selectbox(
                                "Select a property to view comprehensive timeline:",
                                options=property_options
                            )
                            
                            # Find the selected property data
                            property_data = None
                            for p in results["properties"]:
                                if p["address"] == selected_property:
                                    property_data = p
                                    break
                            
                            if property_data:
                                # Display property information
                                location = f"{property_data.get('city', '')}, {property_data.get('state', '')} {property_data.get('zip_code', '')}"
                                location = location.strip().rstrip(', ')
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Address:** {property_data['address']}")
                                with col2:
                                    st.markdown(f"**Location:** {location if location else 'Unknown'}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Time Period:** {property_data.get('start_year', 'Unknown')} - {property_data.get('end_year', 'Present')}")
                                with col2:
                                    # Get property from database to ensure complete data
                                    db_property = get_property_data(address=selected_property)
                                    if db_property:
                                        st.markdown(f"**Database ID:** {db_property.get('id', 'Not in database')}")
                                    else:
                                        st.markdown("**Database ID:** Not in database")
                                
                                st.markdown("---")
                                
                                # Create tabs for different visualization options
                                viz_tabs = st.tabs(["Comprehensive Timeline", "Ownership History", "Document Archive", "Environmental Data", "Event Summary"])
                                
                                with viz_tabs[0]:
                                    st.subheader(f"Comprehensive Timeline for {selected_property}")
                                    
                                    # Get complete property data from database if possible
                                    timeline_data = db_property if db_property else property_data
                                    
                                    # Create interactive timeline
                                    fig = create_interactive_timeline(timeline_data)
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Add explanation
                                    st.markdown("""
                                    **Timeline Guide:**
                                    - Bars represent time spans (like property existence, crop cultivation, or business operations)
                                    - Diamond markers represent point events (like historical events, well installations, or property valuations)
                                    - Hover over elements to see details
                                    - Use the range slider at bottom to zoom into specific time periods
                                    - Click on legend items to show/hide categories
                                    """)
                                
                                with viz_tabs[1]:
                                    st.subheader("Ownership History")
                                    
                                    # Display ownership history if available
                                    if "ownership_history" in timeline_data and timeline_data["ownership_history"]:
                                        ownership_data = timeline_data["ownership_history"]
                                        
                                        # Create a DataFrame from the ownership data
                                        df = pd.DataFrame(ownership_data)
                                        
                                        # Create a Gantt chart to visualize ownership periods
                                        fig = px.timeline(
                                            df, 
                                            x_start="start_year", 
                                            x_end="end_year", 
                                            y="owner",
                                            color="owner",
                                            hover_data=["purchase_price", "transaction_type", "document_id"],
                                            labels={
                                                "owner": "Owner",
                                                "start_year": "From",
                                                "end_year": "To",
                                                "purchase_price": "Purchase Price",
                                                "transaction_type": "Transaction Type",
                                                "document_id": "Document ID"
                                            },
                                            title=f"Ownership Timeline for {selected_property}"
                                        )
                                        
                                        fig.update_yaxes(autorange="reversed")  # Reverse the order to show oldest at the top
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Display the ownership data in a table
                                        st.subheader("Detailed Ownership Records")
                                        
                                        # Reorder columns for better readability
                                        if not df.empty:
                                            cols = ["owner", "start_year", "end_year", "purchase_price", "transaction_type", "document_id"]
                                            df = df[cols]
                                            st.dataframe(df, use_container_width=True)
                                            
                                            # Add a download link for ownership data
                                            csv = df.to_csv(index=False).encode('utf-8')
                                            st.download_button(
                                                "Download Ownership History as CSV",
                                                csv,
                                                f"{selected_property.replace(' ', '_')}_ownership_history.csv",
                                                "text/csv",
                                                key="download-ownership-csv"
                                            )
                                    else:
                                        st.info("No ownership history available for this property.")
                                
                                with viz_tabs[2]:
                                    st.subheader("Document Archive")
                                    
                                    # Display document archive if available
                                    if "property_documents" in timeline_data and timeline_data["property_documents"]:
                                        documents = timeline_data["property_documents"]
                                        
                                        # Create a DataFrame from the documents
                                        df = pd.DataFrame(documents)
                                        
                                        # Add filtering options
                                        st.write("### Filter Documents")
                                        
                                        # Get unique document types and years for filtering
                                        if not df.empty:
                                            doc_types = ["All Types"] + sorted(df["type"].unique().tolist())
                                            years_range = range(df["year"].min(), df["year"].max() + 1)
                                            
                                            # Create filtering widgets
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                selected_type = st.selectbox("Document Type", doc_types)
                                            with col2:
                                                year_range = st.slider(
                                                    "Year Range", 
                                                    min_value=int(df["year"].min()), 
                                                    max_value=int(df["year"].max()),
                                                    value=(int(df["year"].min()), int(df["year"].max()))
                                                )
                                            
                                            # Filter the documents based on selection
                                            filtered_df = df.copy()
                                            
                                            # Filter by type if not "All Types"
                                            if selected_type != "All Types":
                                                filtered_df = filtered_df[filtered_df["type"] == selected_type]
                                            
                                            # Filter by year range
                                            filtered_df = filtered_df[(filtered_df["year"] >= year_range[0]) & 
                                                                     (filtered_df["year"] <= year_range[1])]
                                            
                                            # Sort by year
                                            filtered_df = filtered_df.sort_values("year")
                                            
                                            # Display filtered document count
                                            st.write(f"Showing {len(filtered_df)} of {len(df)} documents")
                                            
                                            # Create document cards with download links
                                            st.write("### Available Documents")
                                            
                                            # Group documents by decade for better organization
                                            filtered_df["decade"] = (filtered_df["year"] // 10) * 10
                                            decades = sorted(filtered_df["decade"].unique())
                                            
                                            for decade in decades:
                                                decade_docs = filtered_df[filtered_df["decade"] == decade]
                                                st.markdown(f"#### {decade}s")
                                                
                                                # Create columns for the document cards
                                                cols = st.columns(3)
                                                
                                                # Display document cards
                                                for i, (_, doc) in enumerate(decade_docs.iterrows()):
                                                    col_idx = i % 3
                                                    with cols[col_idx]:
                                                        with st.container():
                                                            st.markdown(f"**{doc['title']}**")
                                                            st.markdown(f"Year: {doc['year']}")
                                                            st.markdown(f"Type: {doc['type']}")
                                                            st.markdown(f"Location: {doc['location']}")
                                                            st.markdown(f"Document ID: {doc['document_id']}")
                                                            
                                                            # Add download link
                                                            st.markdown(f"[Download Document]({doc['url']})")
                                                            st.markdown("---")
                                            
                                            # Add download button for all filtered documents as CSV
                                            csv = filtered_df.to_csv(index=False).encode('utf-8')
                                            st.download_button(
                                                "Download Document List as CSV",
                                                csv,
                                                f"{selected_property.replace(' ', '_')}_documents.csv",
                                                "text/csv",
                                                key="download-documents-csv"
                                            )
                                    else:
                                        st.info("No document archive available for this property.")
                                
                                with viz_tabs[3]:
                                    st.subheader("Environmental Data")
                                    
                                    # Display EPA and GeoTracker data
                                    st.markdown("### EPA Environmental Data")
                                    
                                    # Check if we have environmental data
                                    if "environmental_data" in timeline_data and timeline_data["environmental_data"]:
                                        env_data = timeline_data["environmental_data"]
                                        
                                        # Display EPA data
                                        if "epa_data" in env_data and env_data["epa_data"]:
                                            epa_data = env_data["epa_data"]
                                            
                                            for record in epa_data:
                                                with st.expander(f"{record.get('record_type', 'EPA Record')} - {record.get('date', 'No Date')}"):
                                                    st.markdown(f"**Record ID:** {record.get('record_id', 'Unknown')}")
                                                    st.markdown(f"**Description:** {record.get('description', 'No description available')}")
                                                    st.markdown(f"**Status:** {record.get('status', 'Unknown')}")
                                                    
                                                    if "documents" in record and record["documents"]:
                                                        st.markdown("**Related Documents:**")
                                                        for doc in record["documents"]:
                                                            st.markdown(f"- [{doc.get('title', 'Document')}]({doc.get('url', '#')})")
                                        else:
                                            st.info("No EPA data available for this property.")
                                        
                                        # Display GeoTracker data
                                        st.markdown("### GeoTracker Data")
                                        if "geotracker_data" in env_data and env_data["geotracker_data"]:
                                            geotracker_data = env_data["geotracker_data"]
                                            
                                            for record in geotracker_data:
                                                with st.expander(f"{record.get('site_type', 'Site')} - {record.get('date', 'No Date')}"):
                                                    st.markdown(f"**Site ID:** {record.get('site_id', 'Unknown')}")
                                                    st.markdown(f"**Description:** {record.get('description', 'No description available')}")
                                                    st.markdown(f"**Status:** {record.get('status', 'Unknown')}")
                                                    st.markdown(f"**Contaminants:** {record.get('contaminants', 'None specified')}")
                                                    
                                                    if "cleanup_actions" in record and record["cleanup_actions"]:
                                                        st.markdown("**Cleanup Actions:**")
                                                        for action in record["cleanup_actions"]:
                                                            st.markdown(f"- {action.get('date', 'No date')}: {action.get('description', 'No description')}")
                                        else:
                                            st.info("No GeoTracker data available for this property.")
                                    else:
                                        st.warning("Environmental data collection is in progress. This feature will show EPA and GeoTracker data related to the property's environmental history.")
                                        
                                        # Show explanation about what will be included
                                        st.markdown("""
                                        **Environmental Data Integration:**
                                        
                                        When available, this tab will include:
                                        
                                        **EPA Data:**
                                        - Environmental violations
                                        - Compliance records
                                        - Permit information
                                        - Enforcement actions
                                        - Air and water quality monitoring
                                        
                                        **GeoTracker Data:**
                                        - Contaminated site information
                                        - Leaking underground storage tanks
                                        - Cleanup status
                                        - Site investigation reports
                                        - Groundwater monitoring
                                        """)
                                
                                with viz_tabs[3]:
                                    st.subheader("Event Summary")
                                    
                                    # Create summary tables of events
                                    event_summary = {
                                        "Agricultural Data": len(timeline_data.get("agricultural_data", [])),
                                        "Commercial Usage": len(timeline_data.get("commercial_usage", [])),
                                        "Historical Events": len(timeline_data.get("historical_events", [])),
                                        "Property Values": len(timeline_data.get("value_history", [])),
                                        "Water Wells": len(timeline_data.get("water_wells", [])),
                                        "Newspaper Records": len(timeline_data.get("newspaper_archives", [])),
                                        "Web Archives": len(timeline_data.get("web_archives", [])),
                                        "Environmental Records": len(timeline_data.get("environmental_data", {}).get("epa_data", [])) + 
                                                                len(timeline_data.get("environmental_data", {}).get("geotracker_data", []))
                                    }
                                    
                                    # Convert to DataFrame
                                    summary_df = pd.DataFrame({
                                        "Event Type": list(event_summary.keys()),
                                        "Count": list(event_summary.values())
                                    })
                                    
                                    # Display as bar chart
                                    if not summary_df["Count"].sum() == 0:
                                        fig = px.bar(
                                            summary_df,
                                            x="Event Type",
                                            y="Count",
                                            color="Event Type",
                                            title=f"Event Counts for {selected_property}"
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Display summary table
                                    st.dataframe(summary_df, use_container_width=True)
                            else:
                                st.error("Property data not found.")
                        else:
                            st.warning("No properties available for timeline visualization.")
                    else:
                        st.error("No property data available. Please run an analysis first.")
                
                # Crop Patterns Tab
                with tabs[2]:
                    st.header("Crop Pattern Analysis")
                    
                    if results["crop_comparisons"]:
                        st.plotly_chart(plot_crop_comparison(results["crop_comparisons"]), use_container_width=True)
                        
                        st.subheader("Crop Details")
                        for crop, data in results["crop_comparisons"].items():
                            with st.expander(f"{crop} - {len(data)} records"):
                                st.dataframe(pd.DataFrame(data))
                    else:
                        st.info("No crop data available for the selected properties and time period.")
                
                # Business Evolution Tab
                with tabs[2]:
                    st.header("Business Evolution Analysis")
                    
                    if results["business_evolution"]:
                        st.plotly_chart(plot_business_evolution(results["business_evolution"]), use_container_width=True)
                        
                        st.subheader("Business Evolution Details")
                        for property_data in results["business_evolution"]:
                            with st.expander(f"Property: {property_data['address']}"):
                                st.dataframe(pd.DataFrame(property_data["evolution"]))
                    else:
                        st.info("No business evolution data available for the selected properties and time period.")
                
                # Property Valuation Tab
                with tabs[3]:
                    st.header("Property Valuation Trends")
                    
                    if results["property_valuation_trends"]:
                        st.plotly_chart(plot_property_valuation(results["property_valuation_trends"]), use_container_width=True)
                        
                        st.subheader("Valuation Details")
                        for property_data in results["property_valuation_trends"]:
                            with st.expander(f"Property: {property_data['address']}"):
                                # Create a DataFrame with years and values
                                values_df = pd.DataFrame({
                                    "Year": property_data["years"],
                                    "Assessed Value ($)": property_data["values"]
                                })
                                st.dataframe(values_df)
                                
                                if "growth_rates" in property_data and property_data["growth_rates"]:
                                    st.subheader("Growth Rates")
                                    growth_df = pd.DataFrame(property_data["growth_rates"])
                                    growth_df["annual_growth_rate"] = growth_df["annual_growth_rate"].round(2).astype(str) + "%"
                                    st.dataframe(growth_df)
                    else:
                        st.info("No property valuation data available for the selected properties and time period.")
                
                # Water Wells Tab
                with tabs[4]:
                    st.header("Water Wells Analysis")
                    
                    # Collect water wells data from all properties
                    water_wells_data = {}
                    for address, data in analyzer.property_data.items():
                        if "findings" in data and "water_wells" in data["findings"] and data["findings"]["water_wells"]:
                            water_wells_data[address] = data["findings"]["water_wells"]
                    
                    if water_wells_data:
                        # Create visualization
                        st.subheader("Water Wells Timeline")
                        
                        # Create a DataFrame with all well data
                        wells_list = []
                        for address, wells in water_wells_data.items():
                            for well in wells:
                                wells_list.append({
                                    "address": address,
                                    "installation_year": well["installation_year"],
                                    "depth": well["depth"],
                                    "water_quality": well["water_quality"],
                                    "flow_rate": well["flow_rate"],
                                    "status": well["status"],
                                    "notes": well.get("notes", "")
                                })
                        
                        if wells_list:
                            wells_df = pd.DataFrame(wells_list)
                            
                            # Plot well depths by installation year
                            fig = px.scatter(
                                wells_df, 
                                x="installation_year", 
                                y="depth", 
                                color="address",
                                size=[30] * len(wells_df),  # Consistent point size
                                hover_data=["water_quality", "flow_rate", "status", "notes"],
                                labels={
                                    "installation_year": "Installation Year",
                                    "depth": "Well Depth (feet)",
                                    "address": "Property"
                                },
                                title="Water Well Depths by Installation Year"
                            )
                            
                            # Create a separate line trace for each property
                            for address in wells_df["address"].unique():
                                address_df = wells_df[wells_df["address"] == address]
                                # Sort by installation year
                                address_df = address_df.sort_values(by="installation_year")
                                if len(address_df) > 1:
                                    # Create a new trace for the lines connecting points
                                    fig.add_trace(go.Scatter(
                                        x=address_df["installation_year"].tolist(),
                                        y=address_df["depth"].tolist(),
                                        mode="lines",
                                        line=dict(dash="dot"),
                                        name=f"{address} trend",
                                        showlegend=False
                                    ))
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display detailed information
                            st.subheader("Water Wells Details")
                            
                            for address, wells in water_wells_data.items():
                                with st.expander(f"Property: {address} - {len(wells)} wells"):
                                    for i, well in enumerate(wells, 1):
                                        st.markdown(f"##### Well {i} - Installed {well['installation_year']}")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"**Depth:** {well['depth']} feet")
                                            st.write(f"**Water Quality:** {well['water_quality']}")
                                        with col2:
                                            st.write(f"**Flow Rate:** {well['flow_rate']}")
                                            st.write(f"**Status:** {well['status']}")
                                        
                                        if "notes" in well:
                                            st.write(f"**Notes:** {well['notes']}")
                                        st.divider()
                    else:
                        st.info("No water wells data available for the selected properties and time period.")
                
                # OSINT Analysis Tab
                with tabs[5]:
                    st.header("OSINT Intelligence Analysis")
                    
                    st.write("This tab provides advanced Open Source Intelligence (OSINT) capabilities similar to those used in Kali Linux tools.")
                    
                    # Initialize OSINT analyzer
                    with st.spinner("Running OSINT analysis tools..."):
                        osint_analyzer = OSINTAnalyzer(addresses, start_year, end_year)
                        osint_results = osint_analyzer.analyze_all_addresses()
                    
                    if osint_results:
                        # Create subtabs for different OSINT categories
                        osint_subtabs = st.tabs([
                            "Newspaper Archives", 
                            "Property Records", 
                            "Web Intelligence",
                            "Water Rights History",
                            "Relationships & Connections",
                            "Digital Reconnaissance"
                        ])
                        
                        # Newspaper Archives Tab
                        with osint_subtabs[0]:
                            st.subheader("Historical Newspaper Intelligence")
                            
                            for address, data in osint_results.items():
                                newspaper_data = data.get("newspaper_archives", [])
                                if newspaper_data:
                                    with st.expander(f"{address} - {len(newspaper_data)} newspaper records found"):
                                        for article in newspaper_data:
                                            st.markdown(f"### {article['headline']}")
                                            st.markdown(f"**Source:** {article['source']} | **Date:** {article['date']}")
                                            st.markdown(f"_{article['snippet']}_")
                                            st.divider()
                                else:
                                    st.info(f"No newspaper records found for {address}")
                        
                        # Property Records Tab
                        with osint_subtabs[1]:
                            st.subheader("Property Records Intelligence")
                            
                            for address, data in osint_results.items():
                                property_data = data.get("property_records", {})
                                if property_data:
                                    with st.expander(f"{address} - Property Records"):
                                        # Ownership History
                                        if "ownership_history" in property_data:
                                            st.markdown("### Ownership History")
                                            ownership_df = pd.DataFrame(property_data["ownership_history"])
                                            st.dataframe(ownership_df)
                                        
                                        # Land Use Changes
                                        if "land_use_changes" in property_data:
                                            st.markdown("### Land Use Classification Changes")
                                            land_use_df = pd.DataFrame(property_data["land_use_changes"])
                                            st.dataframe(land_use_df)
                                        
                                        # Building Permits
                                        if "building_permits" in property_data:
                                            st.markdown("### Building Permits")
                                            permits_df = pd.DataFrame(property_data["building_permits"])
                                            st.dataframe(permits_df)
                                else:
                                    st.info(f"No property records found for {address}")
                        
                        # Web Intelligence Tab
                        with osint_subtabs[2]:
                            st.subheader("Web Intelligence & Digital Footprint Analysis")
                            
                            for address, data in osint_results.items():
                                web_data = data.get("web_archives", [])
                                if web_data:
                                    with st.expander(f"{address} - {len(web_data)} web references found"):
                                        for item in web_data:
                                            st.markdown(f"### {item['title']}")
                                            st.markdown(f"**URL:** [{item['url']}]({item['url']})")
                                            st.markdown(f"**Archived:** {item['date']}")
                                            st.markdown(f"_{item['snippet']}_")
                                            
                                            # Add option to view full content
                                            if st.button(f"Extract Full Content from {item['url'][:30]}...", key=f"url_{item['url'][:20]}"):
                                                with st.spinner("Extracting content..."):
                                                    content = osint_analyzer.get_web_content(item['url'])
                                                    st.text_area("Extracted Content", content, height=300)
                                            
                                            st.divider()
                                else:
                                    st.info(f"No web intelligence found for {address}")
                        
                        # Water Rights History Tab
                        with osint_subtabs[3]:
                            st.subheader("Water Rights & Resource Intel")
                            
                            for address, data in osint_results.items():
                                water_data = data.get("water_rights_history", {})
                                if water_data:
                                    with st.expander(f"{address} - Water Rights Intelligence"):
                                        # Water Rights
                                        if "water_rights" in water_data:
                                            st.markdown("### Water Rights History")
                                            rights_df = pd.DataFrame(water_data["water_rights"])
                                            st.dataframe(rights_df)
                                        
                                        # Well Inspections
                                        if "well_inspections" in water_data:
                                            st.markdown("### Well Inspection Records")
                                            inspections_df = pd.DataFrame(water_data["well_inspections"])
                                            st.dataframe(inspections_df)
                                        
                                        # Historical Notes
                                        if "historical_notes" in water_data:
                                            st.markdown("### Historical Notes")
                                            st.markdown(f"_{water_data['historical_notes']}_")
                                else:
                                    st.info(f"No water rights intelligence found for {address}")
                        
                        # Relationships & Connections Tab
                        with osint_subtabs[4]:
                            st.subheader("Property Relationship Analysis")
                            
                            if len(addresses) > 1:
                                # Generate relationship analysis
                                relationship_data = osint_analyzer.generate_relationship_analysis()
                                
                                if "connections" in relationship_data and relationship_data["connections"]:
                                    for connection in relationship_data["connections"]:
                                        st.markdown(f"### {connection['type']}")
                                        st.markdown(f"**Entity:** {connection['details']}")
                                        
                                        # Display properties in this connection
                                        properties_df = pd.DataFrame(connection["properties"])
                                        st.dataframe(properties_df)
                                else:
                                    st.info("No significant connections found between properties.")
                            else:
                                st.info("Relationship analysis requires multiple properties to analyze.")
                        
                        # Digital Reconnaissance Tab
                        with osint_subtabs[5]:
                            st.subheader("Digital Reconnaissance Tools")
                            
                            st.markdown("""
                            This section provides access to simulated reconnaissance tools similar to those 
                            available in Kali Linux for information gathering.
                            """)
                            
                            tool_choice = st.selectbox(
                                "Select Tool",
                                ["Whois Lookup", "DNS Information", "Satellite Imagery", "Manual OSINT Command"]
                            )
                            
                            if tool_choice == "Whois Lookup":
                                st.write("Simulated Whois lookup for property location:")
                                for address in addresses:
                                    st.code(f"""
Domain Information for {address.split()[0]}.{address.split()[1]}.property:
Registrar: Historical Property Registry
Registration Date: {start_year}-01-01
Expiration Date: Current
Status: Active
Name Servers: ns1.propertyhistory.org, ns2.propertyhistory.org
                                    """)
                            
                            elif tool_choice == "DNS Information":
                                st.write("Simulated DNS records for property location:")
                                for address in addresses:
                                    st.code(f"""
DNS Records for {address.split()[0]}.{address.split()[1]}.property:
A Record: 192.168.1.{address.split()[0][-2:]}
MX Records: mail.propertyhistory.org
NS Records: ns1.propertyhistory.org, ns2.propertyhistory.org
Historical Records First Registered: {start_year}-01-01
                                    """)
                            
                            elif tool_choice == "Satellite Imagery":
                                st.write("Historical satellite imagery analysis:")
                                
                                for address, data in osint_results.items():
                                    imagery_data = data.get("historical_imagery", [])
                                    if imagery_data:
                                        st.markdown(f"#### {address} - Available Historical Imagery")
                                        imagery_df = pd.DataFrame(imagery_data)
                                        st.dataframe(imagery_df)
                                    else:
                                        st.info(f"No imagery intelligence found for {address}")
                            
                            elif tool_choice == "Manual OSINT Command":
                                st.write("Enter manual OSINT command (simulated):")
                                osint_command = st.text_input("Command:", "whois ")
                                
                                if st.button("Execute Command"):
                                    if any(cmd in osint_command for cmd in ["whois", "dig", "nslookup", "host"]):
                                        st.code(f"""
Executing: {osint_command}
Output:
-------
Historical record lookup for {osint_command.split()[-1] if len(osint_command.split()) > 1 else "target"}
First records date to {start_year}
Registry information available through county historical archives
                                        """)
                                    elif "nmap" in osint_command:
                                        st.warning("Network scanning functionality is only available in full version")
                                    else:
                                        st.error("Command not recognized or available in this environment")
                    else:
                        st.error("OSINT analysis failed to return results.")
                
                # Regional Patterns Tab
                with tabs[6]:
                    st.header("Regional Pattern Analysis")
                    
                    if "regional_patterns" in results and results["regional_patterns"]:
                        regional_data = results["regional_patterns"]
                        
                        st.subheader(f"Analysis of {regional_data.get('neighboring_properties', 0)} Properties in the Region")
                        
                        if "common_crops" in regional_data and regional_data["common_crops"]:
                            st.write("**Common Crops in the Region**")
                            for crop, data in regional_data["common_crops"].items():
                                with st.expander(f"{crop} - Found in {len(data['properties'])} properties"):
                                    st.write(f"Properties: {', '.join(data['properties'])}")
                                    st.write(f"Time periods: {', '.join(data['time_periods'])}")
                        
                        if "business_transitions" in regional_data and regional_data["business_transitions"]:
                            st.write("**Business Transition Patterns**")
                            st.dataframe(pd.DataFrame(regional_data["business_transitions"]))
                        
                        if "interlinked_history" in regional_data and regional_data["interlinked_history"]:
                            st.write("**Interlinked Property History**")
                            st.dataframe(pd.DataFrame(regional_data["interlinked_history"]))
                    else:
                        st.info("Regional pattern analysis requires multiple properties in the same area.")
                
                # Database Management Tab
                with tabs[7]:
                    st.header("Database Management")
                    
                    st.markdown("""
                    This tab allows you to interact directly with the property database. 
                    You can view all properties, search for specific properties, and see detailed information.
                    """)
                    
                    # Create database management subtabs
                    db_tabs = st.tabs(["Properties Overview", "Search Database", "Property Details", "Add Property"])
                    
                    # Properties Overview Tab
                    with db_tabs[0]:
                        st.subheader("All Properties in Database")
                        
                        # Get all properties from database
                        all_properties = get_all_properties()
                        
                        if all_properties:
                            # Create a DataFrame from the properties
                            props_df = pd.DataFrame(all_properties)
                            
                            # Format the created_at date
                            if 'created_at' in props_df.columns:
                                props_df['created_at'] = pd.to_datetime(props_df['created_at']).dt.strftime('%Y-%m-%d')
                            
                            # Display the properties in a table
                            st.dataframe(props_df, use_container_width=True)
                            
                            st.info(f"Found {len(all_properties)} properties in the database.")
                        else:
                            st.error("No properties found in the database.")
                    
                    # Search Database Tab
                    with db_tabs[1]:
                        st.subheader("Search Property Database")
                        
                        # Create search form
                        with st.form("search_form"):
                            search_query = st.text_input("Search Query (address, city, state, etc.)")
                            col1, col2 = st.columns(2)
                            with col1:
                                min_year = st.number_input("Minimum Year", min_value=1800, max_value=2023, value=1900)
                            with col2:
                                max_year = st.number_input("Maximum Year", min_value=1800, max_value=2023, value=2023)
                                
                            search_button = st.form_submit_button("Search Database")
                        
                        if search_button:
                            # Perform search
                            search_results = search_properties(search_query, min_year, max_year)
                            
                            if search_results:
                                # Create a DataFrame from the search results
                                results_df = pd.DataFrame(search_results)
                                
                                # Format the created_at date
                                if 'created_at' in results_df.columns:
                                    results_df['created_at'] = pd.to_datetime(results_df['created_at']).dt.strftime('%Y-%m-%d')
                                
                                # Display the search results
                                st.dataframe(results_df, use_container_width=True)
                                
                                st.success(f"Found {len(search_results)} matching properties.")
                            else:
                                st.warning("No properties found matching your search criteria.")
                    
                    # Property Details Tab
                    with db_tabs[2]:
                        st.subheader("Property Details View")
                        
                        # Get all properties for the dropdown
                        all_properties = get_all_properties()
                        
                        if all_properties:
                            # Create a list of property addresses for the dropdown
                            property_options = [f"{p['address']} (ID: {p['id']})" for p in all_properties]
                            
                            # Add a dropdown to select a property
                            selected_property = st.selectbox("Select a property to view details", property_options)
                            
                            if selected_property:
                                # Extract property ID from the selection
                                property_id = int(selected_property.split("(ID: ")[1].split(")")[0])
                                
                                # Get detailed property data
                                property_data = get_property_data(property_id=property_id)
                                
                                if property_data:
                                    # Display property information in sections
                                    st.markdown(f"### {property_data['address']}")
                                    st.markdown(f"**Location:** {property_data.get('city', 'N/A')}, {property_data.get('state', 'N/A')} {property_data.get('zip_code', 'N/A')}")
                                    st.markdown(f"**Time Period:** {property_data.get('start_year', 'N/A')} - {property_data.get('end_year', 'N/A')}")
                                    
                                    # Create detailed information tabs
                                    detail_tabs = st.tabs([
                                        "Agricultural Data", 
                                        "Commercial Usage", 
                                        "Historical Events",
                                        "Property Value",
                                        "Water Wells",
                                        "Documents & Media"
                                    ])
                                    
                                    # Agricultural Data Tab
                                    with detail_tabs[0]:
                                        if property_data.get("agricultural_data"):
                                            ag_df = pd.DataFrame(property_data["agricultural_data"])
                                            st.dataframe(ag_df, use_container_width=True)
                                        else:
                                            st.info("No agricultural data available for this property.")
                                    
                                    # Commercial Usage Tab
                                    with detail_tabs[1]:
                                        if property_data.get("commercial_usage"):
                                            com_df = pd.DataFrame(property_data["commercial_usage"])
                                            st.dataframe(com_df, use_container_width=True)
                                        else:
                                            st.info("No commercial usage data available for this property.")
                                    
                                    # Historical Events Tab
                                    with detail_tabs[2]:
                                        if property_data.get("historical_events"):
                                            events_df = pd.DataFrame(property_data["historical_events"])
                                            st.dataframe(events_df, use_container_width=True)
                                        else:
                                            st.info("No historical events available for this property.")
                                    
                                    # Property Value Tab
                                    with detail_tabs[3]:
                                        if property_data.get("value_history"):
                                            values_df = pd.DataFrame(property_data["value_history"])
                                            
                                            # Create a line chart of property values
                                            if not values_df.empty:
                                                fig = px.line(
                                                    values_df, 
                                                    x="year", 
                                                    y="assessed_value",
                                                    markers=True,
                                                    labels={"year": "Year", "assessed_value": "Assessed Value ($)"},
                                                    title="Property Value History"
                                                )
                                                
                                                st.plotly_chart(fig, use_container_width=True)
                                                st.dataframe(values_df, use_container_width=True)
                                        else:
                                            st.info("No property value history available for this property.")
                                    
                                    # Water Wells Tab
                                    with detail_tabs[4]:
                                        if property_data.get("water_wells"):
                                            wells_df = pd.DataFrame(property_data["water_wells"])
                                            
                                            # Create a scatter plot of well depths
                                            if not wells_df.empty:
                                                fig = px.scatter(
                                                    wells_df,
                                                    x="installation_year",
                                                    y="depth",
                                                    size=[30] * len(wells_df),
                                                    hover_data=["water_quality", "flow_rate", "status", "notes"],
                                                    labels={
                                                        "installation_year": "Installation Year",
                                                        "depth": "Well Depth (feet)"
                                                    },
                                                    title="Water Well Depths by Installation Year"
                                                )
                                                
                                                st.plotly_chart(fig, use_container_width=True)
                                                st.dataframe(wells_df, use_container_width=True)
                                        else:
                                            st.info("No water well data available for this property.")
                                    
                                    # Documents & Media Tab
                                    with detail_tabs[5]:
                                        st.subheader("Related Documents & Media")
                                        
                                        # Newspaper archives
                                        if property_data.get("newspaper_archives"):
                                            st.markdown("### Newspaper Archives")
                                            for article in property_data["newspaper_archives"]:
                                                with st.expander(f"{article['headline']} - {article['date']}"):
                                                    st.markdown(f"**Source:** {article['source']}")
                                                    st.markdown(f"**Date:** {article['date']}")
                                                    st.markdown(f"_{article['snippet']}_")
                                        
                                        # Web archives
                                        if property_data.get("web_archives"):
                                            st.markdown("### Web Archives")
                                            for archive in property_data["web_archives"]:
                                                with st.expander(f"{archive['title']} - {archive['date']}"):
                                                    st.markdown(f"**URL:** [{archive['url']}]({archive['url']})")
                                                    st.markdown(f"**Date:** {archive['date']}")
                                                    st.markdown(f"_{archive['snippet']}_")
                                        
                                        if not property_data.get("newspaper_archives") and not property_data.get("web_archives"):
                                            st.info("No documents or media available for this property.")
                                else:
                                    st.error("Failed to retrieve property details from the database.")
                        else:
                            st.error("No properties found in the database.")
                    
                    # Add Property Tab
                    with db_tabs[3]:
                        st.subheader("Add New Property to Database")
                        
                        with st.form("add_property_form"):
                            address = st.text_input("Property Address*")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                city = st.text_input("City")
                            with col2:
                                state = st.text_input("State")
                                
                            col1, col2 = st.columns(2)
                            with col1:
                                zip_code = st.text_input("Zip Code")
                            with col2:
                                pass
                                
                            col1, col2 = st.columns(2)
                            with col1:
                                start_year = st.number_input("Start Year", min_value=1800, max_value=2025, value=1900)
                            with col2:
                                end_year = st.number_input("End Year", min_value=1800, max_value=2025, value=2025)
                                
                            st.markdown("*Required fields")
                            
                            submit_button = st.form_submit_button("Add Property")
                        
                        if submit_button:
                            if not address:
                                st.error("Address is required")
                            elif not validate_year_range(start_year, end_year):
                                st.error("End year must be greater than or equal to start year")
                            else:
                                # Add property to database
                                property_id = add_property(
                                    address=address,
                                    city=city,
                                    state=state,
                                    zip_code=zip_code,
                                    start_year=start_year,
                                    end_year=end_year
                                )
                                
                                if property_id is not None:
                                    st.success(f"Successfully added property: {address}")
                                    st.info("You can now add more data for this property using the database SQL interface.")
                                else:
                                    st.error(f"Failed to add property: {address}")
                
                # Export Results Tab
                with tabs[8]:
                    st.header("Export Analysis Results")
                    
                    export_format = st.radio(
                        "Select export format",
                        ["CSV", "JSON", "PDF (Report)"],
                        horizontal=True
                    )
                    
                    if export_format == "CSV":
                        # Generate CSV files for each analysis component
                        csv_files = {}
                        
                        if results["agricultural_timeline"]:
                            ag_df = pd.DataFrame(results["agricultural_timeline"])
                            csv_files["agricultural_timeline.csv"] = ag_df.to_csv(index=False)
                        
                        if results["commercial_timeline"]:
                            com_df = pd.DataFrame(results["commercial_timeline"])
                            csv_files["commercial_timeline.csv"] = com_df.to_csv(index=False)
                        
                        if results["crop_comparisons"]:
                            crops_data = []
                            for crop, data in results["crop_comparisons"].items():
                                for entry in data:
                                    entry["crop"] = crop
                                    crops_data.append(entry)
                            if crops_data:
                                crops_df = pd.DataFrame(crops_data)
                                csv_files["crop_comparisons.csv"] = crops_df.to_csv(index=False)
                        
                        # Display download buttons for each CSV file
                        for filename, csv_content in csv_files.items():
                            csv_b64 = base64.b64encode(csv_content.encode()).decode()
                            href = f'<a href="data:file/csv;base64,{csv_b64}" download="{filename}">Download {filename}</a>'
                            st.markdown(href, unsafe_allow_html=True)
                    
                    elif export_format == "JSON":
                        # Export the entire results as JSON
                        json_str = json.dumps(results, indent=2)
                        json_b64 = base64.b64encode(json_str.encode()).decode()
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"property_analysis_{timestamp}.json"
                        
                        href = f'<a href="data:file/json;base64,{json_b64}" download="{filename}">Download Complete Analysis (JSON)</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    
                    else:  # PDF Report
                        st.info("PDF export functionality will be implemented in a future update.")
                        
                        # Display what would be included in the PDF
                        st.subheader("PDF Report Would Include:")
                        
                        report_sections = [
                            "Property Summary",
                            "Agricultural Timeline Analysis",
                            "Commercial Timeline Analysis",
                            "Crop Pattern Comparisons",
                            "Business Evolution Charts",
                            "Property Valuation Trends",
                            "Regional Pattern Analysis"
                        ]
                        
                        for section in report_sections:
                            st.write(f"✓ {section}")
        
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        logger.error(f"Analysis error: {str(e)}", exc_info=True)

# Image gallery section
st.markdown("---")
st.header("Historical Property Images")

# Create a 2x2 grid for historical farm images
st.subheader("Historical Farms")
col1, col2 = st.columns(2)
with col1:
    st.image("https://pixabay.com/get/g4597006e287d5485c1a7d02b5d8f6e20680210e393fbfeef31035373eceeb05d5543a52935983b299ba067b29a719c0f660a3f922ba33d02c1274e94e784c245_1280.jpg", 
             caption="Historical Farm Scene")
    st.image("https://pixabay.com/get/g9b50e76596b1a3c748093a3a6bbc98ccfc4a29dfb2aa1441619f4d5851011feb141becb8a4cf7764e1740c9564305d45ee19b2b0c7730e1c73f8451c423b99ca_1280.jpg", 
             caption="Vintage Farming Methods")
with col2:
    st.image("https://pixabay.com/get/g66547cf2511a2e36b6c14c19eb93a1d07bc222230197bc01dac1933722e6dab8e28fd8ede999a5dc42976647c948e0490b9695b10e50b5b5653e29f1e8726543_1280.jpg", 
             caption="Rural Farm Property")
    st.image("https://pixabay.com/get/g9571f93d09b25f23033932854a9c5b259f24883c33bb6e3bbbe25dfb45214f553220ec9913e04404c481c5ab315fae022808801f3993f0a06d03bd2a3e69442e_1280.jpg", 
             caption="Agricultural Heritage")

# Create a 2x2 grid for commercial building images
st.subheader("Commercial Buildings")
col1, col2 = st.columns(2)
with col1:
    st.image("https://pixabay.com/get/g276131767019ace958ad030f5ae5d43f3044573805c3c24d9dbf4ad9ec2a3199c180e47d6f583c01418772044039cddf3c73efb6924b9203370d7f67d4a53c95_1280.jpg", 
             caption="Historical Commercial District")
    st.image("https://pixabay.com/get/g566917dbeaba4cb51f74720e0ca52faf2be5c3f834abdc232f0ccf0cae9f1a723224f5cd4176e75993d96ee3875f1d2412bb18d37f0de77b7ebbf08edc5b8a0b_1280.jpg", 
             caption="Traditional Main Street")
with col2:
    st.image("https://pixabay.com/get/g70817815e2ea90bda33a7ee35921facc8a4a325bc47ccb6a1d71a48a8326492668d57b8bb419ef29acfe630af39f274a3304491d535cde5a38b3eeff6e5adc3f_1280.jpg", 
             caption="Historic Business Complex")
    st.image("https://pixabay.com/get/gf853248f617c46ab97091f3bc3704d23d5836db15a02dd40616223b8aeffc68537ed1d324417ccce82380331adccd2c13a6cb04e00aefd44332e1bb9d2ee27e5_1280.jpg", 
             caption="Urban Commercial Evolution")

# Add property records images in a row
st.subheader("Property Records")
col1, col2 = st.columns(2)
with col1:
    st.image("https://pixabay.com/get/gb7a1be4baf246e4ccef0d245e6c5380441e0a1f4778e0daba3195f2fb0840f6db0ed8bfa6ef3356b62404b367cf612dc67c27bf52ed520a272d966faa4388064_1280.jpg", 
             caption="Historical Property Documents")
with col2:
    st.image("https://pixabay.com/get/g72e866b0218bc4a674712a45647ca44db4639ccb0a959b525725a92906ce0246d5b217c0b265c42fad1f5f9a697f7aaced26fdf985422b01604ad6dd6c9b5803_1280.jpg", 
             caption="Archive of Property Records")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p>© 2023 Historical Property Analysis Tool</p>
    </div>
    """, 
    unsafe_allow_html=True
)

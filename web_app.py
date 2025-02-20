# Import necessary libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Set page config
st.set_page_config(page_title="Health Facilities in Kenya", page_icon="🌎", layout="wide")

# Load Kenyan county boundaries shapefile
@st.cache_data
def load_shapefile():
    shapefile_path = "kenyan_counties/County.shp"  # Ensure this file is in your working directory
    gdf = gpd.read_file(shapefile_path)
    return gdf

kenya_gdf = load_shapefile()

# Load health facilities data
df = pd.read_excel('health_facilities_data_updated.xlsx')

# Sidebar logo
st.sidebar.image("logo.png", caption="Health Facilities in Kenya")
# Sidebar for county selection
counties = df['County'].unique()
selected_county = st.sidebar.selectbox("Search & Zoom to County", ["All"] + list(counties))

# Function to create a map
def create_map(df, selected_county):
    # Default map center (Kenya)
    center_lat, center_lon, zoom_level = 1.2921, 36.8219, 6

    # Filter for the selected county
    if selected_county != "All":
        df = df[df['County'] == selected_county]
        county_shape = kenya_gdf[kenya_gdf['COUNTY'] == selected_county]
        if not county_shape.empty:
            center_lat, center_lon = county_shape.geometry.centroid.y.values[0], county_shape.geometry.centroid.x.values[0]
            zoom_level = 9

    # Create the map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

    # Add Kenyan counties boundaries
    folium.GeoJson(
        kenya_gdf,
        name="Kenyan Counties",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "blue",
            "weight": 1,
            "fillOpacity": 0.6,
        },
        tooltip=folium.GeoJsonTooltip(fields=["COUNTY"], aliases=["County:"], localize=True),
    ).add_to(m)

    # Add Marker Cluster
    marker_cluster = MarkerCluster().add_to(m)

    # Add health facility markers
    for _, row in df.iterrows():
        popup_content = f"""
        <h4>{row['Facility_Name']}</h4>
        <b>level:</b> {row['Facility_Type']}<br>
        <b>County:</b> {row['County']}<br>
        <b>Sub-County:</b> {row['Sub_County']}<br>
        <b>Location:</b> {row['Location']}<br>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            tooltip=row['Facility_Name'],
            icon=folium.Icon(color='red', icon='plus',prefix='fa'),
        ).add_to(marker_cluster).add_child(folium.Popup(popup_content, max_width=400))

    # Add Google Maps Basemap
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Google Satellite",
        overlay=True,
        control=True,
    ).add_to(m)

    # Add Google Labels
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}",
        attr="Google Labels",
        name="Google Labels",
        overlay=True,
        control=True,
    ).add_to(m)

    # Add Layer Control
    folium.LayerControl(collapsed=False).add_to(m)

    return m

# Generate map
m = create_map(df, selected_county)

# Display map in Streamlit
folium_static(m, width=1350, height=600)

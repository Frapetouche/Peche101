import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Guide Pêche QC", layout="wide", initial_sidebar_state="collapsed")

LAT, LON, ZOOM = 48.45520, -71.05210, 13
url_garmin = f"https://webapp.navionics.com/?lang=en#boating@13@{LAT},{LON}"

# Plein écran : on retire les marges et le padding de Streamlit
st.markdown("""
    <style>
        .stApp { max-width: 100%; padding: 0; margin: 0; }
        .block-container { padding-top: 0; padding-bottom: 0; }
        iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

# Lien vers Navionics HD en haut
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 16px; background: #0f172a; border-bottom: 1px solid #1e3a5f;">
    <span style="color: #7dd3fc; font-weight: 700; font-size: 1rem;">🧭 Bathymétrie — Guide Pêche QC</span>
    <a href="{url_garmin}" target="_blank" style="background: linear-gradient(135deg, #004b87, #0284c7); color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 0.85rem; white-space: nowrap;">🗺️ Garmin HD</a>
</div>
""", unsafe_allow_html=True)

# Carte plein écran avec couches bathymétriques nautiques
m = folium.Map(location=[LAT, LON], zoom_start=ZOOM, control_scale=True, tiles=None)

# Base: carte nautique OpenSeaMap
folium.TileLayer(
    tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='OpenStreetMap', name='🗺️ Carte nautique', overlay=False
).add_to(m)

# Overlay: bathymétrie / marques nautiques OpenSeaMap
folium.TileLayer(
    tiles='https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
    attr='OpenSeaMap', name='🧭 Bathymétrie & isobathes', overlay=True, control=True
).add_to(m)

# Base alternative: Satellite HD
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite', name='🛰️ Satellite HD', overlay=False
).add_to(m)

# Base alternative: Topographie
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap', name='⛰️ Topographie', overlay=False
).add_to(m)

folium.Marker(location=[LAT, LON], tooltip="Cassure Principale", icon=folium.Icon(color="red", icon="fish", prefix="fa")).add_to(m)

folium.LayerControl(position="topright").add_to(m)
st_folium(m, width="100%", height=800, returned_objects=[], key="map_plein_ecran")

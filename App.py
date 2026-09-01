import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Guide Pêche QC", layout="wide", initial_sidebar_state="collapsed")

LAT, LON, ZOOM = 48.45520, -71.05210, 13
url_garmin = f"https://webapp.navionics.com/?lang=en#boating@13@{LAT},{LON}"

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.markdown("### 🛰️ Satellite & Topo")
    m = folium.Map(location=[LAT, LON], zoom_start=ZOOM, control_scale=True, tiles=None)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite', name='🛰️ Satellite HD', overlay=False
    ).add_to(m)

    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap', name='⛰️ Topographie', overlay=False
    ).add_to(m)

    folium.Marker(location=[LAT, LON], tooltip="Cassure Principale", icon=folium.Icon(color="red", icon="fish", prefix="fa")).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    st_folium(m, width="100%", height=550, returned_objects=[], key="map_fixe")

with col_droite:
    st.markdown("### 🧭 Bathymétrie Garmin / Navionics")
    st.markdown(f"""
    <div style="background-color: #1e293b; padding: 40px; border-radius: 10px; border: 1px solid #334155; text-align: center; height: 550px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <h3 style="color: #f1f5f9; margin-bottom: 20px;">Cartes Isobathes HD</h3>
        <p style="color: #94a3b8; margin-bottom: 30px;">Visualisez les profondeurs et structures sous-marines en simultané.</p>
        <a href="{url_garmin}" target="_blank" style="background-color: #004b87; color: white; padding: 15px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;">🗺️ Ouvrir Garmin / Navionics</a>
    </div>
    """, unsafe_allow_html=True)

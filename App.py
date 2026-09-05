import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(page_title="Bathymétrie Saguenay", layout="wide")

st.title("🗺️ Bathymétrie - Lacs du Saguenay")
st.markdown("Explorez les profondeurs des lacs du Saguenay")

# Données statiques des lacs du Saguenay
LACS_SAGUENAY = {
    "Lac Saint-Jean": {
        "lat": 48.4552,
        "lon": -71.0521,
        "profondeur_max": 10.1,
        "zoom": 13
    },
    "Lac Ha! Ha!": {
        "lat": 48.5789,
        "lon": -71.2156,
        "profondeur_max": 8.5,
        "zoom": 13
    },
    "Lac Kénogami": {
        "lat": 48.3645,
        "lon": -71.1234,
        "profondeur_max": 6.2,
        "zoom": 13
    },
    "Lac Pikauba": {
        "lat": 48.2134,
        "lon": -71.4567,
        "profondeur_max": 7.8,
        "zoom": 13
    }
}

# Sidebar
st.sidebar.markdown("### 🎣 Sélectionnez un lac")
lac_selected = st.sidebar.selectbox(
    "Lacs du Saguenay",
    list(LACS_SAGUENAY.keys()),
    index=0
)

lac_info = LACS_SAGUENAY[lac_selected]

# Stats
col1, col2 = st.columns(2)
with col1:
    st.metric("🌊 Profondeur max", f"{lac_info['profondeur_max']:.1f} m")
with col2:
    st.metric("📍 Coordonnées", f"{lac_info['lat']:.3f}, {lac_info['lon']:.3f}")

# Créer la carte
st.markdown(f"### 🗺️ {lac_selected}")

m = folium.Map(
    location=[lac_info['lat'], lac_info['lon']],
    zoom_start=lac_info['zoom'],
    control_scale=True,
    tiles=None
)

# Satellite Google
folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google Satellite',
    name='🛰️ Satellite',
    overlay=False,
    show=True
).add_to(m)

# Topographie
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap',
    name='⛰️ Topographie',
    overlay=False,
    show=False
).add_to(m)

# Marqueur du lac
folium.CircleMarker(
    location=[lac_info['lat'], lac_info['lon']],
    radius=20,
    popup=f"<b>{lac_selected}</b><br>Profondeur max: {lac_info['profondeur_max']:.1f}m",
    tooltip=lac_selected,
    color='#0066ff',
    fill=True,
    fillColor='#0066ff',
    fillOpacity=0.3,
    weight=2
).add_to(m)

folium.LayerControl(position="topright").add_to(m)
st_folium(m, width="100%", height=600, returned_objects=[], key="map_main")

# Infos
st.markdown(f"""
**{lac_selected}**
- 📍 Latitude: {lac_info['lat']:.3f}
- 📍 Longitude: {lac_info['lon']:.3f}
- 🌊 Profondeur maximale: {lac_info['profondeur_max']:.1f} m
- 🌍 Région: Saguenay-Lac-Saint-Jean, Québec
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 Lacs disponibles
Tous les lacs du Saguenay avec leurs profondeurs maximales
""")

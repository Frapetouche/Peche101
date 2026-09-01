import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Guide Pêche QC", layout="wide", initial_sidebar_state="expanded")

BASE_SECTEURS = {
    "saguenay_terres_rompues": {
        "nom": "Fjord du Saguenay — Terres-Rompues",
        "coords_centre": [48.45520, -71.05210],
        "zoom": 13,
        "points": [{"nom": "Cassure Principale", "coords": [48.45520, -71.05210]}]
    },
    "lac_saint_jean": {
        "nom": "Lac Saint-Jean — Secteur Central",
        "coords_centre": [48.58200, -71.95500],
        "zoom": 12,
        "points": [{"nom": "Haut-fond de sable", "coords": [48.57500, -71.94000]}]
    },
    "fleuve_quebec_levis": {
        "nom": "Fleuve Saint-Laurent — Québec / Lévis",
        "coords_centre": [46.81250, -71.20520],
        "zoom": 13,
        "points": [{"nom": "Fosse de la Citadelle", "coords": [46.81100, -71.20700]}]
    }
}

st.sidebar.markdown("### 🎛️ Sélection")
choix = st.sidebar.selectbox("Zone :", options=list(BASE_SECTEURS.keys()), format_func=lambda x: BASE_SECTEURS[x]["nom"])

secteur = BASE_SECTEURS[choix]
lat, lon = secteur["coords_centre"]
url_garmin = f"https://webapp.navionics.com/?lang=en#boating@13@{lat},{lon}"

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.markdown(f"### 🛰️ Satellite & Topo : {secteur['nom']}")
    m = folium.Map(location=[lat, lon], zoom_start=secteur["zoom"], control_scale=True, tiles=None)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite', name='🛰️ Satellite HD', overlay=False
    ).add_to(m)

    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap', name='⛰️ Topographie', overlay=False
    ).add_to(m)

    for pt in secteur["points"]:
        folium.Marker(location=pt["coords"], tooltip=pt["nom"], icon=folium.Icon(color="red", icon="fish", prefix="fa")).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    st_folium(m, width="100%", height=550, returned_objects=[], key=f"map_{choix}")

with col_droite:
    st.markdown(f"### 🧭 Bathymétrie Garmin / Navionics")
    st.markdown(f"""
    <div style="background-color: #1e293b; padding: 40px; border-radius: 10px; border: 1px solid #334155; text-align: center; height: 550px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <h3 style="color: #f1f5f9; margin-bottom: 20px;">Cartes Isobathes HD</h3>
        <p style="color: #94a3b8; margin-bottom: 30px;">Visualisez les profondeurs et structures sous-marines en simultané.</p>
        <a href="{url_garmin}" target="_blank" style="background-color: #004b87; color: white; padding: 15px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;">🗺️ Ouvrir Garmin / Navionics</a>
    </div>
    """, unsafe_allow_html=True)

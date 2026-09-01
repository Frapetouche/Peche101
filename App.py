import streamlit as st
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. CONFIGURATION PLEINE PAGE
# ==========================================
st.set_page_config(
    page_title="Pêche QC — Carte Bathymétrique",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Optimisation de l'espace d'affichage
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0284c7;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DONNÉES DES SECTEURS ET POINTS GPS
# ==========================================
BANQUE_SECTEURS = {
    "saguenay_terres_rompues": {
        "nom": "Terres-Rompues (Fjord du Saguenay)",
        "coords_centre": [48.45520, -71.05210],
        "zoom": 14,
        "debarcadere": {
            "nom": "Rampe des Terres-Rompues",
            "coords": [48.45831, -71.05582],
            "info": "Gratuit / Parking 25 remorques"
        },
        "spots_cles": [
            {"nom": "Cassure Principale (8m à 38m)", "coords": [48.45520, -71.05210]},
            {"nom": "Pointe des Courants", "coords": [48.45280, -71.04550]}
        ]
    },
    "anse_saint_jean": {
        "nom": "L'Anse-Saint-Jean (Fjord Profond)",
        "coords_centre": [48.24650, -70.18920],
        "zoom": 13,
        "debarcadere": {
            "nom": "Marina de L'Anse-Saint-Jean",
            "coords": [48.24388, -70.19830],
            "info": "Payant / Tous services"
        },
        "spots_cles": [
            {"nom": "Marche des Sébastes (85m)", "coords": [48.24810, -70.18500]}
        ]
    },
    "fleuve_levis": {
        "nom": "Québec / Lévis (Fosse Citadelle)",
        "coords_centre": [46.81250, -71.20520],
        "zoom": 14,
        "debarcadere": {
            "nom": "Rampe du Parc Maritime de Lévis",
            "coords": [46.81520, -71.19880],
            "info": "Municipal / Courant fort"
        },
        "spots_cles": [
            {"nom": "Ressort de la Citadelle", "coords": [46.81180, -71.20850]}
        ]
    },
    "lac_saint_pierre": {
        "nom": "Archipel du Lac Saint-Pierre",
        "coords_centre": [46.19820, -72.92150],
        "zoom": 13,
        "debarcadere": {
            "nom": "Mise à l'eau de la Sablière",
            "coords": [46.20250, -72.93210],
            "info": "Payant / Qualité supérieure"
        },
        "spots_cles": [
            {"nom": "Entrée du Chenal des Corbeaux", "coords": [46.19500, -72.91800]}
        ]
    }
}

# ==========================================
# 3. BARRE LATÉRALE ET OPTIONS
# ==========================================
st.sidebar.header("🗺️ Navigation & Bathymétrie")

secteur_id = st.sidebar.selectbox(
    "📍 Choisir le secteur :",
    options=list(BANQUE_SECTEURS.keys()),
    format_func=lambda x: BANQUE_SECTEURS[x]["nom"]
)

secteur = BANQUE_SECTEURS[secteur_id]

# Lien vers la bathymétrie communautaire Navionics pré-centrée
lat, lon = secteur["coords_centre"]
zoom = secteur["zoom"]
navionics_url = f"https://webapp.navionics.com/?lang=en#boating@11@{lat},{lon}"

st.sidebar.markdown("---")
st.sidebar.subheader("🌊 Bathymétrie Haute Définition")
st.sidebar.write("Pour visualiser les lignes de profondeur au pied près (SonarChart) :")
st.sidebar.markdown(f'[![Ouvrir Navionics HD](https://img.shields.io/badge/Navionics-SonarChart_HD-0284c7?style=for-the-badge)]({navionics_url})')

# ==========================================
# 4. GÉNÉRATION DE LA CARTE BATHYMÉTRIQUE
# ==========================================
m = folium.Map(location=secteur["coords_centre"], zoom_start=secteur["zoom"], control_scale=True)

# Couche 1: Esri Ocean Bathymetry (Fonds marins & reliefs)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Ocean Bathymetry',
    name='🌊 Bathymétrie & Fonds (Esri)',
    overlay=False
).add_to(m)

# Couche 2: OpenTopoMap (Reliefs topographiques)
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap',
    name='⛰️ Topographie',
    overlay=False
).add_to(m)

# Couche 3: Esri Satellite
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite',
    name='🛰️ Satellite HD',
    overlay=False
).add_to(m)

# Superposition : OpenSeaMap (Balises et signaux marins)
folium.TileLayer(
    tiles='https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
    attr='OpenSeaMap',
    name='🚨 Balises marines (OpenSeaMap)',
    overlay=True,
    opacity=0.85
).add_to(m)

# Ajout du repère de débarcadère (Ancre bleue)
if "debarcadere" in secteur:
    deb = secteur["debarcadere"]
    folium.Marker(
        deb["coords"],
        popup=f"<b>⚓ {deb['nom']}</b><br>GPS: {deb['coords'][0]}, {deb['coords'][1]}<br>{deb['info']}",
        tooltip=f"Débarcadère : {deb['nom']}",
        icon=folium.Icon(color="blue", icon="anchor", prefix="fa")
    ).add_to(m)

# Ajout des fosses et structures de pêche (Poisson rouge)
for spot in secteur.get("spots_cles", []):
    folium.Marker(
        spot["coords"],
        popup=f"<b>🎯 {spot['nom']}</b><br>GPS: {spot['coords'][0]}, {spot['coords'][1]}",
        tooltip=f"Structure : {spot['nom']}",
        icon=folium.Icon(color="red", icon="fish", prefix="fa")
    ).add_to(m)

folium.LayerControl(position="topright").add_to(m)

# Affichage de la carte
st_folium(m, width="100%", height=780, returned_objects=[], key=f"map_{secteur_id}")

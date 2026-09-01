import streamlit as st
import folium
from streamlit_folium import st_folium

# =====================================================================
# CONFIGURATION DE LA FENÊTRE
# =====================================================================
st.set_page_config(
    page_title="Pro-Bathymétrie & Analyse Lacustre",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #0284c7;
        margin-bottom: 10px;
    }
    .expert-card {
        background-color: #0f172a;
        color: #f1f5f9;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #0ea5e9;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .bathymetrie-box {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# BASE DE DONNÉES HYDROGRAPHIQUE AVEC PROFONDEURS ET FORMES DE FONDS
# =====================================================================
BASE_LACS_PRO = {
    "lac_saint_jean_centrale": {
        "nom": "Lac Saint-Jean (Secteur Central / SabLIÈRES)",
        "coords_centre": [48.58200, -71.95500],
        "zoom": 12,
        "profondeur_max": "63 mètres (Bassin semi-ouvert)",
        "profil_bathymetrique": "Immenses hauts-fonds sablonneux alternant avec des cuvettes de 10 à 25m. Présence de pointes rocheuses submergées.",
        "zones_cles": [
            {"nom": "Haut-fond de sable (3 à 5m) - Station du Doré", "coords": [48.57500, -71.94000], "type": "Haut-fond"},
            {"nom": "Cassure brusque de 8m à 22m", "coords": [48.59000, -71.97000], "type": "Cassure / Talus"}
        ],
        "conseil_sonar": "Cherchez les transitions nettes sur le SonarChart entre les plateaux de 4m et la pente abrupte du chenal."
    },
    "fjord_saguenay_baie_eternite": {
        "nom": "Fjord du Saguenay — Baie Éternité",
        "coords_centre": [48.29310, -70.30820],
        "zoom": 13,
        "profondeur_max": "Plus de 250 mètres (Fjord encaissé)",
        "profil_bathymetrique": "Tombants verticaux immédiats. Le rebord (la 'marche') se situe souvent entre 15m et 45m avant la grande noirceur des grands fonds.",
        "zones_cles": [
            {"nom": "Le Seuil de la Baie (18m - 30m)", "coords": [48.29800, -70.31500], "type": "Seuil rocheux"},
            {"nom": "Tombant Nord (Sébaste / Omble)", "coords": [48.29000, -70.30000], "type": "Paroi verticale"}
        ],
        "conseil_sonar": "Le SonarChart est critique ici pour repérer les gradins rocheux sous-marins invisibles depuis la surface."
    },
    "lac_st_pierre_chenal": {
        "nom": "Lac Saint-Pierre (Archipel & Chenal)",
        "coords_centre": [46.23000, -72.85000],
        "zoom": 12,
        "profondeur_max": "3 à 10 mètres (Lac fluviatile très peu profond)",
        "profil_bathymetrique": "Labyrinthe d'herbiers, de hernies de glaise et de chenaux creusés par le passage des navires.",
        "zones_cles": [
            {"nom": "Sortie du Chenal Principal (6m)", "coords": [46.22000, -72.87000], "type": "Talus de chenal"},
            {"nom": "Plateau d'herbiers submergés", "coords": [46.24500, -72.83000], "type": "Herbier dense"}
        ],
        "conseil_sonar": "Attention aux hauts-fonds cachés de moins d'un mètre. Le SonarChart évite l'échouage sur les bancs de glaise."
    }
}

# =====================================================================
# INTERFACE UTILISATEUR (SIDEBAR)
# =====================================================================
st.sidebar.markdown("### 🎛️ Paramètres d'Analyse Bathymétrique")
choix_lac = st.sidebar.selectbox(
    "Sélectionnez le plan d'eau à analyser :",
    options=list(BASE_LACS_PRO.keys()),
    format_func=lambda x: BASE_LACS_PRO[x]["nom"]
)

lac_actif = BASE_LACS_PRO[choix_lac]

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Cartographie HD & SonarChart")
lat_l, lon_l = lac_actif["coords_centre"]
# Lien direct vers Navionics SonarChart centré sur les coordonnées exactes du lac
url_navionics_hd = f"https://webapp.navionics.com/?lang=en#boating@13@{lat_l},{lon_l}"
st.sidebar.markdown(f"""
[![Ouvrir SonarChart HD](https://img.shields.io/badge/Navionics-Ouvrir_SonarChart_HD-0284c7?style=for-the-badge&logo=googlemaps)]({url_navionics_hd})
""")
st.sidebar.caption("💡 *Astuce Pro :* Gardez la carte SonarChart ouverte sur un écran secondaire ou mobile pour valider les isobathes exactes de chaque pied/mètre.")

# =====================================================================
# PANNEAU PRINCIPAL D'ANALYSE
# =====================================================================
st.markdown(f'<div class="main-header">📊 Analyse Morphologique & Bathymétrique : {lac_actif["nom"]}</div>', unsafe_allow_html=True)

# Bloc de description des fonds
st.markdown(f"""
<div class="expert-card">
    <h3>🌊 Caractéristiques du Fond & Profondeurs</h3>
    <p><b>Profondeur Maximale du Secteur :</b> {lac_actif['profondeur_max']}</p>
    <p><b>Profil du relief sous-marin :</b> {lac_actif['profil_bathymetrique']}</p>
    <p><b>Conseil de lecture Sonar :</b> {lac_actif['conseil_sonar']}</p>
</div>
""", unsafe_allow_html=True)

# Section d'analyse des zones ciblées par le pro
col_gauche, col_droite = st.columns([1.5, 1])

with col_gauche:
    st.markdown("### 🗺️ Repérage Géographique des Structures")
    
    # Création de la carte Folium orientée bathymétrie
    m = folium.Map(
        location=lac_actif["coords_centre"],
        zoom_start=lac_actif["zoom"],
        control_scale=True,
        tiles=None
    )

    # Couche de bathymétrie mondiale (Esri Ocean)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Ocean Bathymetry',
        name='🌊 Bathymétrie Générale (Esri)',
        overlay=False
    ).add_to(m)

    # Couche Satellite pour repérer les pointes de terre et baies
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite',
        name='🛰️ Satellite HD',
        overlay=False
    ).add_to(m)

    # Couche OpenTopoMap pour les reliefs côtiers
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='⛰️ Topographie',
        overlay=False
    ).add_to(m)

    # Ajout des zones clés (structures du fond)
    for zone in lac_actif["zones_cles"]:
        folium.Marker(
            location=zone["coords"],
            popup=f"<b>Structure : {zone['nom']}</b><br>Type : {zone['type']}",
            tooltip=zone["nom"],
            icon=folium.Icon(color="orange", icon="binoculars", prefix="fa")
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    st_folium(m, width="1005", height=450, returned_objects=[], key="carte_bathymetrie_lac")

with col_droite:
    st.markdown("### 🎯 Points Stratégiques Identifiés")
    for zone in lac_actif["zones_cles"]:
        st.markdown(f"""
        <div class="bathymetrie-box">
            <b>📍 {zone['nom']}</b><br>
            <span style="color: #38bdf8; font-size: 13px;">Type de structure : {zone['type']}</span><br>
            <code style="font-size: 11px;">GPS: {zone['coords'][0]}, {zone['coords'][1]}</code>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
# RÈGLES DE JAUGEAGE D'UN LAC PAR UN PRO
# =====================================================================
st.markdown("---")
st.markdown("### 🧠 Méthodologie Pro : Comment jauger un nouveau lac avec le SonarChart")
st.markdown("""
1. **Identifier les étranglements et les goulets :** Le poisson se déplace souvent là où l'eau est canalisée (accélération du courant, oxygénation).
2. **Repérer les rebords de hauts-fonds isolés (*Mid-lake humps*) :** En plein milieu d'un lac, un monticule qui remonte de 15m à 4m attire systématiquement les prédateurs.
3. **Analyser l'espacement des lignes isobathes :** 
   * Des lignes **serrées** indiquent un mur ou un talus abrupt (idéal pour le poisson de roche et les pélagiques).
   * Des lignes **espacées** indiquent un plateau progressif (favorable pour la traîne à plat et les herbiers).
""")

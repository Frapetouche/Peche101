import streamlit as st
import folium
from streamlit_folium import st_folium

# =====================================================================
# CONFIGURATION DE LA FENÊTRE
# =====================================================================
st.set_page_config(
    page_title="Guide Pro Pêche QC — Satellite & Garmin",
    page_icon="🛰️",
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
    .garmin-btn {
        display: inline-block;
        background-color: #004b87;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-top: 10px;
    }
    .garmin-btn:hover {
        background-color: #003366;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# BASE DE DONNÉES DES SECTEURS CLÉS
# =====================================================================
BASE_SECTEURS = {
    "saguenay_terres_rompues": {
        "nom": "Fjord du Saguenay — Terres-Rompues",
        "coords_centre": [48.45520, -71.05210],
        "zoom": 13,
        "profil": "Tombants verticaux abrupts, failles profondes de 20m à 100m+.",
        "conseil_pro": "Cherchez la cassure principale entre 8m et 38m pour l'omble et les rebords rocheux profonds pour le sébaste.",
        "points": [
            {"nom": "Cassure Principale", "coords": [48.45520, -71.05210]}
        ]
    },
    "lac_saint_jean": {
        "nom": "Lac Saint-Jean — Secteur Central",
        "coords_centre": [48.58200, -71.95500],
        "zoom": 12,
        "profil": "Vastes hauts-fonds sablonneux et cuvettes de 10 à 25m.",
        "conseil_pro": "Ciblez les transitions de sable et les plateaux rocheux submergés avec des présentations lentes.",
        "points": [
            {"nom": "Haut-fond de sable", "coords": [48.57500, -71.94000]}
        ]
    },
    "fleuve_quebec_levis": {
        "nom": "Fleuve Saint-Laurent — Québec / Lévis",
        "coords_centre": [46.81250, -71.20520],
        "zoom": 13,
        "profil": "Fosses profondes creusées et forts courants de marée.",
        "conseil_pro": "Pêchez les contre-courants en aval des structures et utilisez des têtes de jig lourdes (3/4oz à 1.5oz).",
        "points": [
            {"nom": "Fosse de la Citadelle", "coords": [46.81100, -71.20700]}
        ]
    }
}

# =====================================================================
# INTERFACE LATÉRALE (MODE PRO & GARMIN)
# =====================================================================
st.sidebar.markdown("### 🎛️ Sélection du Secteur")
choix = st.sidebar.selectbox(
    "Choisissez votre zone :",
    options=list(BASE_SECTEURS.keys()),
    format_func=lambda x: BASE_SECTEURS[x]["nom"]
)

secteur = BASE_SECTEURS[choix]
lat, lon = secteur["coords_centre"]

# Liens cartographiques Pro (Garmin / Navionics HD)
url_garmin_navionics = f"https://webapp.navionics.com/?lang=en#boating@13@{lat},{lon}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Mode Pro : Cartographie Garmin")
st.sidebar.markdown(f"""
<div style="background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155;">
    <p style="font-size: 13px; color: #cbd5e1;">Accédez aux courbes isobathes ultra-précises de type <b>Garmin / Navionics SonarChart</b> pour analyser les moindres failles du fond.</p>
    <a href="{url_garmin_navionics}" target="_blank" class="garmin-btn">🗺️ Ouvrir la Carte Garmin HD</a>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# PANNEAU PRINCIPAL
# =====================================================================
st.markdown(f'<div class="main-header">🛰️ Vue Satellite & Stratégie Pro : {secteur["nom"]}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="expert-card">
    <h3>🎯 Analyse Tactique du Pro</h3>
    <p><b>Profil du relief :</b> {secteur['profil']}</p>
    <p><b>Stratégie recommandée :</b> {secteur['conseil_pro']}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# CARTE INTERACTIVE SATELLITE HD
# =====================================================================
st.markdown("### 🌍 Carte Satellite Interactive")

m = folium.Map(
    location=[lat, lon],
    zoom_start=secteur["zoom"],
    control_scale=True,
    tiles=None
)

# Uniquement le fond Satellite HD Esri
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite HD',
    name='🛰️ Satellite HD',
    overlay=False
).add_to(m)

# Ajout des points stratégiques
for pt in secteur["points"]:
    folium.Marker(
        location=pt["coords"],
        popup=f"<b>Zone Pro : {pt['nom']}</b>",
        tooltip=pt["nom"],
        icon=folium.Icon(color="red", icon="fish", prefix="fa")
    ).add_to(m)

st_folium(m, width="100%", height=550, returned_objects=[], key=f"carte_satellite_{choix}")

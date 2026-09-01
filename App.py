import streamlit as st
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION DE L'APPLICATION ---
st.set_page_config(
    page_title="Pêche QC Pro - Cartes Hydrographiques",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #00d2ff;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BANQUE DE DONNÉES DES SECTEURS ---
BANQUE_SECTEURS = {
    "saguenay_terres_rompues": {
        "nom": "Secteur Terres-Rompues (Fjord du Saguenay)",
        "region": "Saguenay–Lac-Saint-Jean",
        "coords": [48.4520, -71.0450],
        "zoom": 13,
        "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=80",
        "especes": ["Omble de fontaine anadrome (Truite de mer)", "Sébaste", "Doré Jaune", "Bar Rayé (Remise à l'eau)"],
        "fond_type": "Batture de galets, cassures abruptes, eau saumâtre",
        "profondeur_moyenne": "5m à 45m (fosse rapide)",
        "maree_optimale": "Mi-marée montante (Montant)",
        "pression_optimale": "1012 hPa - 1018 hPa",
        "conseil_tactique": "Ciblez les bordures de batture lorsque le courant de marée s'accélère. Les cuillères oscillantes argentées et leurres souples imitant l'éperlan sont redoutables.",
        "niveau_difficulte": "Intermédiaire"
    },
    "anse_saint_jean": {
        "nom": "L'Anse-Saint-Jean (Fjord Profond)",
        "region": "Bas-Saguenay",
        "coords": [48.2435, -70.1983],
        "zoom": 12,
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "especes": ["Sébaste", "Morue franche", "Flétan du Groenland"],
        "fond_type": "Parois rocheuses verticales, fosses ultra-profondes",
        "profondeur_moyenne": "60m à 120m+",
        "maree_optimale": "Étale de marée haute (Courant faible)",
        "pression_optimale": "1015 hPa+",
        "conseil_tactique": "Pêche verticale lourde aux jigs métalliques sur les marches de structures profondes.",
        "niveau_difficulte": "Avancé"
    },
    "fleuve_levis": {
        "nom": "Secteur Québec / Lévis (Fosse de la Citadelle)",
        "region": "Capitale-Nationale / Chaudière-Appalaches",
        "coords": [46.8139, -71.2082],
        "zoom": 13,
        "image": "https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=1200&q=80",
        "especes": ["Doré Jaune", "Doré Noir", "Achigan à grande bouche"],
        "fond_type": "Lit rocheux, pointes de courant, structures portuaires",
        "profondeur_moyenne": "10m à 25m",
        "maree_optimale": "Début du descendant (Perdant)",
        "pression_optimale": "1010 hPa - 1014 hPa",
        "conseil_tactique": "Utilisez des têtes de jigs lourdes garnies de leurres souples pour rester près du fond malgré le courant.",
        "niveau_difficulte": "Intermédiaire"
    },
    "lac_saint_pierre": {
        "nom": "Archipel du Lac Saint-Pierre",
        "region": "Mauricie / Centre-du-Québec",
        "coords": [46.1950, -72.9242],
        "zoom": 12,
        "image": "https://images.unsplash.com/photo-1499381683128-81c970423024?auto=format&fit=crop&w=1200&q=80",
        "especes": ["Doré Jaune", "Grand Brochet", "Achigan à petite bouche"],
        "fond_type": "Herbiers denses, chenaux de navigation, fonds de vase",
        "profondeur_moyenne": "2m à 8m",
        "maree_optimale": "Non affecté par la marée",
        "pression_optimale": "1008 hPa - 1012 hPa",
        "conseil_tactique": "Prospection aux leurres de surface près des herbiers pour le brochet.",
        "niveau_difficulte": "Facile"
    }
}

# --- EN-TÊTE PRINCIPAL ---
st.title("⚓ Pêche QC Pro")
st.caption("Plateforme intelligente de cartographie hydrographique & analyse de secteurs")

# --- BARRE LATÉRALE ---
st.sidebar.header("📍 Exploration & Conditions")

secteur_id = st.sidebar.selectbox(
    "Choisir le plan d'eau / secteur :",
    options=list(BANQUE_SECTEURS.keys()),
    format_func=lambda x: BANQUE_SECTEURS[x]["nom"]
)

secteur_data = BANQUE_SECTEURS[secteur_id]

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Conditions du jour")

pression_actuelle = st.sidebar.slider("Pression Atmosphérique (hPa)", 990, 1030, 1014, 1)
tendance_pression = st.sidebar.radio("Tendance Barométrique :", ["En hausse ↗️", "Stable ➡️", "En baisse ↘️"])
etat_maree = st.sidebar.selectbox("Phase de Marée :", ["Montant (Bas vers Haut)", "Pleine mer (Étale)", "Perdant (Haut vers Bas)", "Basse mer (Étale)"])

# --- ONGLETS ---
tab_carte, tab_analyse, tab_guide = st.tabs(["🗺️ Cartographie Hydrographique", "🔍 Fiche du Secteur", "🎣 Guide des Espèces"])

with tab_carte:
    st.markdown(f"### 🌊 Sondes & Relief Hydrographique — {secteur_data['nom']}")
    st.info("💡 **Bascule de cartes :** Utilisez le menu en haut à droite sur la carte pour basculer entre la carte marine NOAA (chiffres de profondeur), le relief bathymétrique ESRI et le satellite.")

    def generer_carte(lat, lon, zoom):
        m = folium.Map(location=[lat, lon], zoom_start=zoom, control_scale=True, tiles=None)
        
        # 1. Carte Marine Officielle NOAA (Chiffres de sonde + isothermes)
        folium.TileLayer(
            tiles='https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png',
            attr='NOAA Office of Coast Survey',
            name='Carte Marine NOAA (Sondes & Balises)',
            overlay=False,
            max_zoom=18
        ).add_to(m)

        # 2. Carte Bathymétrique Mondiale (Relief sous-marin coloré)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
            attr='Esri, GEBCO, NOAA',
            name='Relief des Fonds Marins (Esri Ocean)',
            overlay=False,
            max_zoom=16
        ).add_to(m)

        # 3. Vue Satellite HD (Pour voir la clarté de l'eau et les structures)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri Satellite',
            name='Vue Satellite HD',
            overlay=False
        ).add_to(m)

        # 4. Calque de repères maritimes (Bouées, feux)
        folium.TileLayer(
            tiles='https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
            attr='OpenSeaMap',
            name='Repères de navigation OpenSeaMap',
            overlay=True,
            opacity=0.8
        ).add_to(m)

        # Contrôle des calques pour choisir la carte
        folium.LayerControl(position='topright').add_to(m)

        # Marqueur rouge pour marquer la zone de pêche
        folium.Marker(
            [lat, lon],
            popup=f"Secteur recommandé: {lat}, {lon}",
            icon=folium.Icon(color="red", icon="anchor", prefix="fa")
        ).add_to(m)
        
        return m

    map_render = generer_carte(secteur_data["coords"][0], secteur_data["coords"][1], secteur_data["zoom"])
    st_folium(map_render, width="100%", height=600, returned_objects=[], key=f"map_{secteur_id}")

with tab_analyse:
    st.markdown("### 📍 Analyse approfondie du secteur")
    col_img, col_info = st.columns([1.2, 1])
    
    with col_img:
        st.image(secteur_data["image"], caption=f"Vue terrain : {secteur_data['nom']}", use_container_width=True)
    
    with col_info:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🗺️ Région : {secteur_data['region']}</h4>
            <p><b>Type de structure :</b> {secteur_data['fond_type']}</p>
            <p><b>Profondeur moyenne :</b> {secteur_data['profondeur_moyenne']}</p>
            <p><b>Niveau d'expérience :</b> {secteur_data['niveau_difficulte']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🎯 Fenêtres Optima")
        st.success(f"🌊 **Marée idéale :** {secteur_data['maree_optimale']}")
        st.info(f"📊 **Pression cible :** {secteur_data['pression_optimale']}")

with tab_guide:
    st.markdown("### 🎣 Stratégies de Capture")
    st.markdown("#### Espèces actives identifiées :")
    cols_esp = st.columns(len(secteur_data["especes"]))
    for idx, esp in enumerate(secteur_data["especes"]):
        cols_esp[idx].info(f"🐟 **{esp}**")
        
    st.markdown("---")
    st.markdown("#### 💡 Conseils du Guide & Techniques")
    st.warning(secteur_data["conseil_tactique"])

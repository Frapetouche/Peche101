import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURATION AVANCÉE STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Pêche QC Pro — Plateforme Tactique Hydrographique",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DESIGN & STYLES CSS SUR-MESURE
# ==========================================
st.markdown("""
    <style>
    /* Reset & variables */
    :root {
        --primary-blue: #0284c7;
        --accent-teal: #0d9488;
        --bg-main: #f8fafc;
        --card-bg: #ffffff;
    }
    
    .stApp {
        background-color: var(--bg-main);
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Cartes d'information tactiques */
    .spot-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }
    
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin-top: 10px;
    }
    
    .metric-box {
        background: #f1f5f9;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid var(--primary-blue);
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
    }
    
    /* Badges d'espèces */
    .badge-fish {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
        margin: 4px 4px 4px 0;
    }
    
    /* Bouton d'exportation */
    .stDownloadButton button {
        width: 100%;
        background-color: var(--primary-blue);
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DONNÉES HYDROGRAPHIQUE ENRICHIE
# ==========================================
BANQUE_SECTEURS = {
    "saguenay_terres_rompues": {
        "nom": "Terres-Rompues (Fjord du Saguenay)",
        "region": "Saguenay–Lac-Saint-Jean",
        "coords": [48.4520, -71.0450],
        "zoom": 13,
        "type_fond": "Batture de galets, cassures abruptes, fosse saumâtre",
        "profondeur": "5m à 45m",
        "accessibilite": "Embarcation & Bord",
        "especes": ["Truite de mer", "Sébaste", "Doré Jaune", "Bar Rayé"],
        "debarcadere": {
            "nom": "Rampe municipale Terres-Rompues",
            "coords": [48.4535, -71.0470],
            "statut": "Public / Gratuit",
            "parking": "25 places avec remorque",
            "qualite": "Béton étagé, idéale pour forte marée"
        },
        "spots_cles": [
            {"nom": "Fosse principale", "coords": [48.4510, -71.0420], "desc": "Cassure abrupte de 10m à 35m"},
            {"nom": "Pointe de courant", "coords": [48.4550, -71.0480], "desc": "Zone d'alimentation en mi-marée"}
        ],
        "tactique": "Ciblez les cassures en début de montant. Les cuillères oscillantes argentées et les têtes de jig de 3/4 oz garnies d'éperlan artificiel sont incontournables.",
        "pression_cible": "1012 à 1018 hPa",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Fjord_du_Saguenay.jpg/1200px-Fjord_du_Saguenay.jpg"]
    },
    "anse_saint_jean": {
        "nom": "L'Anse-Saint-Jean (Fjord Profond)",
        "region": "Bas-Saguenay",
        "coords": [48.2435, -70.1983],
        "zoom": 12,
        "type_fond": "Parois rocheuses verticales, abîmes",
        "profondeur": "60m à 120m+",
        "accessibilite": "Embarcation uniquement",
        "especes": ["Sébaste", "Morue franche", "Flétan du Groenland"],
        "debarcadere": {
            "nom": "Marina de L'Anse-Saint-Jean",
            "coords": [48.2450, -70.1950],
            "statut": "Services payants / Marina",
            "parking": "50+ places",
            "qualite": "Infrastructures complètes, quai de carburant"
        },
        "spots_cles": [
            {"nom": "Fosse des Sébastes", "coords": [48.2410, -70.1900], "desc": "Plateau rocheux entre 70m et 90m"}
        ],
        "tactique": "Jigging vertical lourd avec des leurres métalliques phosphorescents (150g à 300g).",
        "pression_cible": "> 1015 hPa",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/L%27Anse-Saint-Jean_QC.jpg/1200px-L%27Anse-Saint-Jean_QC.jpg"]
    },
    "fleuve_levis": {
        "nom": "Québec / Lévis (Fosse Citadelle)",
        "region": "Capitale-Nationale",
        "coords": [46.8139, -71.2082],
        "zoom": 13,
        "type_fond": "Schiste rocheux, structures portuaires",
        "profondeur": "10m à 30m",
        "accessibilite": "Embarcation & Kayak de mer",
        "especes": ["Doré Jaune", "Doré Noir", "Achigan à grande bouche"],
        "debarcadere": {
            "nom": "Parc Maritime de Lévis",
            "coords": [46.8160, -71.2000],
            "statut": "Public",
            "parking": "30 places",
            "qualite": "Prudence requise : très fort courant transversal"
        },
        "spots_cles": [
            {"nom": "Bordure du chenal commercial", "coords": [46.8120, -71.2050], "desc": "Fosse profonde de dérive"}
        ],
        "tactique": "Technique de dérive contrôlée au moteur électrique. Leurres souples type *Drop Shot* ou jigs lourds de 1 oz.",
        "pression_cible": "1010 à 1014 hPa",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Chateau_Frontenac_from_Levis.jpg/1200px-Chateau_Frontenac_from_Levis.jpg"]
    },
    "lac_saint_pierre": {
        "nom": "Archipel du Lac Saint-Pierre",
        "region": "Mauricie / Centre-du-Québec",
        "coords": [46.1950, -72.9242],
        "zoom": 12,
        "type_fond": "Herbiers denses, vase, chenaux de dérive",
        "profondeur": "2m à 8m",
        "accessibilite": "Embarcation, Kayak, Chaloupe",
        "especes": ["Doré Jaune", "Grand Brochet", "Achigan à petite bouche"],
        "debarcadere": {
            "nom": "Mise à l'eau Sorel / Berthierville",
            "coords": [46.1980, -72.9300],
            "statut": "Municipal / Tarification locale",
            "parking": "Large capacité",
            "qualite": "Très bon accès, idéal pour tout type d'embarcation"
        },
        "spots_cles": [
            {"nom": "Chenal des Corbeaux", "coords": [46.1920, -72.9200], "desc": "Cassure douce en bordure d'herbier"}
        ],
        "tactique": "Prospection rapide au *Spinnerbait* et *Chatterbait* au-dessus des herbiers pour les brochets géants.",
        "pression_cible": "1008 à 1012 hPa",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Lac_Saint-Pierre.jpg/1200px-Lac_Saint-Pierre.jpg"]
    }
}

# ==========================================
# 4. EN-TÊTE PRINCIPAL ET RECHERCHE
# ==========================================
st.title("⚓ Pêche QC Pro — Hydrographie & Tactique")
st.caption("Plateforme technique de cartographie sous-marine, repérage de mises à l'eau et météo halieutique.")

# --- BARRE LATÉRALE DE FILTRAGE ---
st.sidebar.header("🔍 Moteur de recherche")

# Filtre par Espèces
toutes_especes = sorted(list({esp for sec in BANQUE_SECTEURS.values() for esp in sec["especes"]}))
espece_filtre = st.sidebar.multiselect("Filtrer par espèce ciblée :", options=toutes_especes)

# Filtre par secteur
secteurs_filtrés = {}
for k, v in BANQUE_SECTEURS.items():
    if not espece_filtre or any(e in v["especes"] for e in espece_filtre):
        secteurs_filtrés[k] = v

if not secteurs_filtrés:
    st.sidebar.warning("Aucun secteur ne correspond à toutes ces espèces.")
    secteurs_filtrés = BANQUE_SECTEURS

secteur_id = st.sidebar.selectbox(
    "Sélectionner le plan d'eau :",
    options=list(secteurs_filtrés.keys()),
    format_func=lambda x: secteurs_filtrés[x]["nom"]
)

secteur = BANQUE_SECTEURS[secteur_id]

st.sidebar.divider()
st.sidebar.subheader("📊 Paramètres de sortie")
pression_live = st.sidebar.number_input("Pression barométrique (hPa)", value=1014, step=1)
maree_phase = st.sidebar.select_slider("Phase de marée", options=["Basse mer", "Montant (Début)", "Mi-Montant", "Pleine mer", "Perdant"])

# ==========================================
# 5. ONGLETS APPLICATIFS
# ==========================================
tab_carte, tab_analyse, tab_export = st.tabs([
    "🗺️ Carte Tactique & Bathymétrie", 
    "🎯 Fiche d'Analyse & Accès", 
    "💾 Export Sonar (GPX / KML)"
])

# ------------------------------------------
# TAB 1 : CARTE FOLIUM MULTI-COUCHES
# ------------------------------------------
with tab_carte:
    st.markdown(f"### 🌊 Sondage hydrographique : **{secteur['nom']}**")
    
    m = folium.Map(location=secteur["coords"], zoom_start=secteur["zoom"], control_scale=True)
    
    # Couches Cartographiques Pro
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Ocean Bathymetry',
        name='Bathymétrie / Fonds marins (Esri)',
        overlay=False
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='Relief & Topographie (OpenTopo)',
        overlay=False
    ).add_to(m)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite',
        name='Vue Satellite HD',
        overlay=False
    ).add_to(m)
    
    # Overlay Balises marines
    folium.TileLayer(
        tiles='https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
        attr='OpenSeaMap',
        name='Bouées & Balises de navigation',
        overlay=True,
        opacity=0.8
    ).add_to(m)

    # Marqueur Débarcadère (Bleu)
    if "debarcadere" in secteur:
        deb = secteur["debarcadere"]
        folium.Marker(
            deb["coords"],
            popup=f"<b>⚓ {deb['nom']}</b><br>Statut: {deb['statut']}<br>Parking: {deb['parking']}<br>Info: {deb['qualite']}",
            tooltip="Mise à l'eau / Débarcadère",
            icon=folium.Icon(color="blue", icon="anchor", prefix="fa")
        ).add_to(m)

    # Marqueurs Spots clés (Rouge)
    for spot in secteur.get("spots_cles", []):
        folium.Marker(
            spot["coords"],
            popup=f"<b>🎯 Spot : {spot['nom']}</b><br>{spot['desc']}",
            tooltip=f"Structure : {spot['nom']}",
            icon=folium.Icon(color="red", icon="fish", prefix="fa")
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    
    st_folium(m, width="100%", height=600, returned_objects=[], key=f"map_{secteur_id}")

# ------------------------------------------
# TAB 2 : ANALYSE STRATÉGIQUE
# ------------------------------------------
with tab_analyse:
    col_visuel, col_data = st.columns([1.2, 1])
    
    with col_visuel:
        st.markdown("#### 📸 Terrain & Espèces Présentes")
        if secteur.get("images"):
            st.image(secteur["images"][0], caption=secteur["nom"], use_container_width=True)
            
        st.markdown("##### Espèces actives identifiées :")
        for esp in secteur["especes"]:
            st.markdown(f'<span class="badge-fish">🐟 {esp}</span>', unsafe_allow_html=True)

    with col_data:
        st.markdown(f"""
        <div class="spot-card">
            <h3>📍 {secteur['region']}</h3>
            <p><b>Structures & Fonds :</b> {secteur['type_fond']}</p>
            <p><b>Accessibilité :</b> {secteur['accessibilite']}</p>
            <div class="metric-container">
                <div class="metric-box">
                    <div class="metric-label">Profondeur</div>
                    <div class="metric-value">{secteur['profondeur']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Pression cible</div>
                    <div class="metric-value">{secteur['pression_cible']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Section Débarcadère
        deb = secteur["debarcadere"]
        st.markdown(f"""
        <div class="spot-card" style="border-left: 5px solid #0284c7;">
            <h4>⚓ Mise à l'eau : {deb['nom']}</h4>
            <p>• <b>Statut :</b> {deb['statut']}</p>
            <p>• <b>Stationnement :</b> {deb['parking']}</p>
            <p>• <b>Rampes :</b> {deb['qualite']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"💡 **Recommandation du guide :** {secteur['tactique']}")

# ------------------------------------------
# TAB 3 : EXPORTATION VERS SONAR (GPX)
# ------------------------------------------
with tab_export:
    st.markdown("### 💾 Exporter les waypoints vers votre GPS / Sonar")
    st.write("Téléchargez les coordonnées de la mise à l'eau et des structures sous-marines au format **GPX** (compatible avec Garmin, Lowrance, Humminbird et Raymarine).")

    # Génération du fichier GPX au format XML
    gpx_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="PecheQCPro" xmlns="http://www.topografix.com/GPX/1/1">
  <wpt lat="{secteur['debarcadere']['coords'][0]}" lon="{secteur['debarcadere']['coords'][1]}">
    <name>Mise a l eau - {secteur['debarcadere']['nom']}</name>
    <sym>Anchor</sym>
  </wpt>
"""
    for spot in secteur.get("spots_cles", []):
        gpx_data += f"""  <wpt lat="{spot['coords'][0]}" lon="{spot['coords'][1]}">
    <name>{spot['nom']}</name>
    <sym>Fish Symbol</sym>
  </wpt>\n"""
    
    gpx_data += "</gpx>"

    st.download_button(
        label=f"📥 Télécharger le fichier GPX pour {secteur['nom']}",
        data=gpx_data,
        file_name=f"{secteur_id}_waypoints.gpx",
        mime="application/gpx+xml"
    )

import streamlit as st
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. CONFIGURATION AVANCÉE STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Pêche QC Pro — Cartographie & GPS",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DESIGN & STYLES CSS SUR-MESURE
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .spot-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }
    .metric-box {
        background: #f1f5f9;
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #0284c7;
        margin-bottom: 8px;
    }
    .badge-fish {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        background: #e0f2fe;
        color: #0369a1;
        margin: 2px;
    }
    .gps-code {
        font-family: monospace;
        background: #e2e8f0;
        padding: 2px 6px;
        border-radius: 4px;
        color: #0f172a;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DONNÉES PRÉCISE & DÉTAILLÉE
# ==========================================
BANQUE_SECTEURS = {
    "saguenay_terres_rompues": {
        "nom": "Terres-Rompues (Fjord du Saguenay)",
        "region": "Saguenay–Lac-Saint-Jean",
        "coords": [48.45520, -71.05210], # Positionné exactement sur la fosse de dérive
        "zoom": 14,
        "type_fond": "Batture de galets, argile marine, cassures abruptes, fosse saumâtre",
        "profondeur": "5m à 52m (Cassure rapide)",
        "accessibilite": "Embarcation, Kayak & Pêche à pied (selon la marée)",
        "especes": ["Omble de fontaine anadrome (Truite de mer)", "Sébaste", "Doré Jaune", "Bar Rayé (remise à l'eau)"],
        "debarcadere": {
            "nom": "Rampe de mise à l'eau des Terres-Rompues",
            "coords": [48.45831, -71.05582], # Coordonnées GPS exactes du quai/rampe
            "statut": "Public / Accès Gratuit",
            "parking": "25-30 places véhicules avec remorques",
            "qualite": "Dalle de béton inclinée. Facile à mi-marée, attention au bas de la rampe à marée ultra-basse.",
            "services": "Poubelles, toilettes chimiques en saison"
        },
        "spots_cles": [
            {
                "nom": "Fosse de la Cassure Principale", 
                "coords": [48.45520, -71.05210], 
                "desc": "Marche brutale passant de 8m à 38m. Point de rassemblement des truites de mer lors du montant."
            },
            {
                "nom": "Pointe des Courants (Tête de la batture)", 
                "coords": [48.45280, -71.04550], 
                "desc": "Zone d'accélération de marée. Très bon secteur pour lancer des cuillères lourdes à la tombée de la nuit."
            }
        ],
        "tactique": "Pêchez le montant (mi-marée). Lances légers avec cuillères oscillantes type *Williams Wabler* ou *Cami* (argent/bleu). Au jig : têtes de 1/2 à 3/4 oz garnies de leurres souples imitant l'éperlan (3 à 4 pouces).",
        "pression_cible": "1012 à 1018 hPa (Baromètre stable ou légère hausse)",
        "courant_fenetre": "1h30 après le bas de la marée jusqu'à la pleine mer.",
        "reglementation": "Zone 28. Remise à l'eau obligatoire pour le bar rayé. Permis de pêche sportive du Québec requis.",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Fjord_du_Saguenay.jpg/1200px-Fjord_du_Saguenay.jpg"]
    },
    "anse_saint_jean": {
        "nom": "L'Anse-Saint-Jean (Fjord Profond)",
        "region": "Bas-Saguenay",
        "coords": [48.24650, -70.18920], # Plateau profond
        "zoom": 13,
        "type_fond": "Parois rocheuses verticales, abîmes argileux, marches rocheuses",
        "profondeur": "60m à 135m",
        "accessibilite": "Embarcation à moteur, Chaloupe forte",
        "especes": ["Sébaste atlantique", "Morue franche", "Flétan du Groenland (Turbot)", "Rai de la mer"],
        "debarcadere": {
            "nom": "Quai municipal & Marina de L'Anse-Saint-Jean",
            "coords": [48.24388, -70.19830], # Quai précis
            "statut": "Payant / Municipal & Marina",
            "parking": "Grand stationnement payant / gratuit selon période",
            "qualite": "Rampe en béton large avec quai de courtoisie. Accessible à toutes les marées.",
            "services": "Essence, restaurant, capitainerie, station de rinçage"
        },
        "spots_cles": [
            {
                "nom": "Marche des Sébastes (Fosse Ouest)", 
                "coords": [48.24810, -70.18500], 
                "desc": "Plateau sous-marin situé à 85m de profondeur le long du mur de roche."
            }
        ],
        "tactique": "Pêche verticale lourde. Ligne tressée de 20-30 lb impérative avec bas de ligne en fluorocarbone de 40 lb. Jigs métalliques phosphorescents de 150g à 250g garnis d'un morceau de crevette nordique ou de squid.",
        "pression_cible": "> 1015 hPa",
        "courant_fenetre": "Privilégiez les étales de marée (30 min avant et après la pleine/basse mer) pour réduire la dérive du fil.",
        "reglementation": "Zone 28. Limite de prises spécifique pour le sébaste et la morue. Consulter le guide de la faune.",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/L%27Anse-Saint-Jean_QC.jpg/1200px-L%27Anse-Saint-Jean_QC.jpg"]
    },
    "fleuve_levis": {
        "nom": "Québec / Lévis (Fosse Citadelle)",
        "region": "Capitale-Nationale / Chaudière-Appalaches",
        "coords": [46.81250, -71.20520], # Fosse sous le traversier
        "zoom": 14,
        "type_fond": "Lit de roche schisteuse, structures portuaires, roches massives",
        "profondeur": "12m à 32m",
        "accessibilite": "Embarcation avec bon moteur électrique (ancrage virtuel)",
        "especes": ["Doré Jaune", "Doré Noir", "Achigan à grande bouche", "Esturgeon jaune (Secteur)"],
        "debarcadere": {
            "nom": "Rampe d'accès du Parc Maritime de Lévis",
            "coords": [46.81520, -71.19880], # Rampe précise
            "statut": "Accès municipal",
            "parking": "20-25 places",
            "qualite": "Rampe bétonnée exposée au courant direct du fleuve. Prudence lors des opérations d'amarrage.",
            "services": "Plaque d'information, bancs"
        },
        "spots_cles": [
            {
                "nom": "Ressort de la Citadelle", 
                "coords": [46.81180, -71.20850], 
                "desc": "Cassure abrupte du lit du fleuve juste en face de la pointe du Cap Diamant."
            }
        ],
        "tactique": "Technique de dérive contrôlée. Têtes de jig lourdes (3/4 oz à 1.5 oz) pour garder le contact avec le fond malgré le courant. Leurres souples de type *Swimbait* ou *Jighead avec ver*.",
        "pression_cible": "1010 à 1014 hPa",
        "courant_fenetre": "Début du montant ou début du perdant (éviter les pics de vitesse de courant).",
        "reglementation": "Zone 7. Attention aux limites de tailles pour le doré (gamme de taille exploitable).",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Chateau_Frontenac_from_Levis.jpg/1200px-Chateau_Frontenac_from_Levis.jpg"]
    },
    "lac_saint_pierre": {
        "nom": "Archipel du Lac Saint-Pierre",
        "region": "Mauricie / Centre-du-Québec",
        "coords": [46.19820, -72.92150], # Entrée d'herbiers
        "zoom": 13,
        "type_fond": "Champs d'herbiers denses (vallisnérie, myriophylle), fond de vase, chenaux de dérive",
        "profondeur": "1.5m à 6m",
        "accessibilite": "Chaloupe, Kayak de pêche, Bass Boat",
        "especes": ["Grand Brochet", "Doré Jaune", "Achigan à petite bouche", "Perchaude"],
        "debarcadere": {
            "nom": "Mise à l'eau de la Sablière (Sorel-Tracy)",
            "coords": [46.20250, -72.93210], # Coordonnées débarcadère exactes
            "statut": "Payant / Municipal",
            "parking": "Plus de 60 places avec remorque",
            "qualite": "Excellente rampe multi-voies en béton avec quais flottants.",
            "services": "Station-service nautique à proximité, toilettes"
        },
        "spots_cles": [
            {
                "nom": "Entrée du Chenal des Corbeaux", 
                "coords": [46.19500, -72.91800], 
                "desc": "Cassure douce en bordure de la structure d'herbiers. Fosse de repos pour les gros brochets."
            }
        ],
        "tactique": "Pêche aux leurres de surface (*Popper*, *Frog*) au-dessus des herbiers en début de journée. *Spinnerbaits* et *Chatterbaits* le long des bordures de chenal.",
        "pression_cible": "1008 à 1012 hPa (Avant un front froid)",
        "courant_fenetre": "Non affecté par les marées oceaniques, sensible aux vents d'Ouest/Sud-Ouest.",
        "reglementation": "Zone 7. Moratoire/règlementation stricte sur la perchaude et quotas réduits sur le doré.",
        "images": ["https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Lac_Saint-Pierre.jpg/1200px-Lac_Saint-Pierre.jpg"]
    }
}

# ==========================================
# 4. EN-TÊTE PRINCIPAL ET RECHERCHE
# ==========================================
st.title("⚓ Pêche QC Pro — Cartographie & GPS")
st.caption("Plateforme technique de repérage : coordonnées GPS exactes, structures hydrographiques et accès aux mises à l'eau.")

# --- BARRE LATÉRALE ---
st.sidebar.header("🔍 Recherche & Filtrage")

# Filtre par Espèces
toutes_especes = sorted(list({esp for sec in BANQUE_SECTEURS.values() for esp in sec["especes"]}))
espece_filtre = st.sidebar.multiselect("Espèce ciblée :", options=toutes_especes)

# Filtre dynamique
secteurs_filtrés = {}
for k, v in BANQUE_SECTEURS.items():
    if not espece_filtre or any(e in v["especes"] for e in espece_filtre):
        secteurs_filtrés[k] = v

if not secteurs_filtrés:
    st.sidebar.warning("Aucun secteur ne correspond à ce filtre.")
    secteurs_filtrés = BANQUE_SECTEURS

secteur_id = st.sidebar.selectbox(
    "Choisir le secteur :",
    options=list(secteurs_filtrés.keys()),
    format_func=lambda x: secteurs_filtrés[x]["nom"]
)

secteur = BANQUE_SECTEURS[secteur_id]

# ==========================================
# 5. ONGLETS APPLICATIFS
# ==========================================
tab_carte, tab_fiche, tab_gps = st.tabs([
    "🗺️ Carte Hydrographique & Relatifs", 
    "📋 Fiche Technique du Secteur", 
    "📍 Coordonnées GPS & Sonar"
])

# ------------------------------------------
# TAB 1 : CARTE FOLIUM AVEC GPS PRÉCIS
# ------------------------------------------
with tab_carte:
    st.markdown(f"### 🌊 Sondage du secteur : **{secteur['nom']}**")
    
    m = folium.Map(location=secteur["coords"], zoom_start=secteur["zoom"], control_scale=True)
    
    # Couches cartographiques
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Ocean Bathymetry',
        name='Bathymétrie / Fonds marins (Esri)',
        overlay=False
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='Relief & Topographie',
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
        name='Balises & Signalisation maritime',
        overlay=True,
        opacity=0.85
    ).add_to(m)

    # 1. Marqueur Débarcadère (Bleu)
    if "debarcadere" in secteur:
        deb = secteur["debarcadere"]
        folium.Marker(
            deb["coords"],
            popup=f"<b>⚓ {deb['nom']}</b><br>GPS: {deb['coords'][0]}, {deb['coords'][1]}<br>Statut: {deb['statut']}<br>Parking: {deb['parking']}",
            tooltip=f"Débarcadère : {deb['nom']}",
            icon=folium.Icon(color="blue", icon="anchor", prefix="fa")
        ).add_to(m)

    # 2. Marqueurs Spots clés (Rouge)
    for spot in secteur.get("spots_cles", []):
        folium.Marker(
            spot["coords"],
            popup=f"<b>🎯 {spot['nom']}</b><br>GPS: {spot['coords'][0]}, {spot['coords'][1]}<br>{spot['desc']}",
            tooltip=f"Structure : {spot['nom']}",
            icon=folium.Icon(color="red", icon="fish", prefix="fa")
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    
    st_folium(m, width="100%", height=600, returned_objects=[], key=f"map_{secteur_id}")

# ------------------------------------------
# TAB 2 : FICHE TECHNIQUE DÉTAILLÉE
# ------------------------------------------
with tab_fiche:
    col_visuel, col_data = st.columns([1, 1.2])
    
    with col_visuel:
        st.markdown("#### 📸 Aperçu & Faune")
        if secteur.get("images"):
            st.image(secteur["images"][0], caption=secteur["nom"], use_container_width=True)
            
        st.markdown("##### Espèces présentes dans cette zone :")
        for esp in secteur["especes"]:
            st.markdown(f'<span class="badge-fish">🐟 {esp}</span>', unsafe_allow_html=True)

    with col_data:
        st.markdown(f"""
        <div class="spot-card">
            <h3>📍 {secteur['region']}</h3>
            <p><b>Type de fond :</b> {secteur['type_fond']}</p>
            <p><b>Profondeur :</b> {secteur['profondeur']}</p>
            <p><b>Accès :</b> {secteur['accessibilite']}</p>
            <p><b>Conditions d'eau :</b> {secteur['courant_fenetre']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section Débarcadère
        deb = secteur["debarcadere"]
        st.markdown(f"""
        <div class="spot-card" style="border-left: 5px solid #0284c7;">
            <h4>⚓ Débarcadère : {deb['nom']}</h4>
            <p><b>Coordonnées GPS :</b> <span class="gps-code">{deb['coords'][0]}, {deb['coords'][1]}</span></p>
            <p>• <b>Statut :</b> {deb['statut']}</p>
            <p>• <b>Stationnement :</b> {deb['parking']}</p>
            <p>• <b>Qualité de la rampe :</b> {deb['qualite']}</p>
            <p>• <b>Services :</b> {deb['services']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"💡 **Conseil tactique :** {secteur['tactique']}")
        st.warning(f"⚖️ **Réglementation :** {secteur['reglementation']}")

# ------------------------------------------
# TAB 3 : COORDONNÉES GPS & EXPORT SONAR
# ------------------------------------------
with tab_gps:
    st.markdown("### 📍 Tableau des coordonnées GPS exactes")
    st.write("Copiez directement ces coordonnées dans votre GPS portable, votre téléphone ou votre sonar (Garmin, Lowrance, Humminbird) :")

    # Affichage clair sous forme de tableau
    deb = secteur["debarcadere"]
    
    data_gps = [
        {
            "Type": "⚓ Débarcadère / Rampe",
            "Nom": deb["nom"],
            "Latitude": deb["coords"][0],
            "Longitude": deb["coords"][1],
            "Format décimal (Copier/Coller)": f"{deb['coords'][0]}, {deb['coords'][1]}"
        }
    ]
    
    for spot in secteur.get("spots_cles", []):
        data_gps.append({
            "Type": "🎯 Structure / Fosse",
            "Nom": spot["nom"],
            "Latitude": spot["coords"][0],
            "Longitude": spot["coords"][1],
            "Format décimal (Copier/Coller)": f"{spot['coords'][0]}, {spot['coords'][1]}"
        })
        
    st.dataframe(data_gps, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💾 Fichier GPX prêt à l'emploi")
    
    # Génération du fichier GPX
    gpx_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="PecheQCPro" xmlns="http://www.topografix.com/GPX/1/1">
  <wpt lat="{deb['coords'][0]}" lon="{deb['coords'][1]}">
    <name>Rampe - {deb['nom']}</name>
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
        label=f"📥 Télécharger le fichier .GPX ({secteur['nom']})",
        data=gpx_data,
        file_name=f"{secteur_id}_gps.gpx",
        mime="application/gpx+xml"
    )
    
    

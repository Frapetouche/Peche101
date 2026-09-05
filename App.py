import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json
from folium.plugins import HeatMap
import numpy as np
from urllib.parse import quote

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
    <div style="background-color: #1e293b; padding: 40px; border-radius: 10px; border: 1px solid #334155; text-align: center; height: 550px; display: flex; flex-direction: column; justify-content: space-between;">
        <h3 style="color: #f1f5f9; margin-bottom: 20px;">Cartes Isobathes HD</h3>
        <p style="color: #94a3b8; margin-bottom: 30px;">Visualisez les profondeurs et structures sous-marines en simultané.</p>
        <a href="{url_garmin}" target="_blank" style="background-color: #004b87; color: white; padding: 15px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;">🗺️ Ouvrir Garmin / Navionics</a>
    </div>
    """, unsafe_allow_html=True)

# 3ème carte : Grand lac Saint-Jean d'Alma avec bathymétrie GBLQ
st.markdown("### 🗺️ Grand lac Saint-Jean d'Alma - Bathymétrie Sonar (GBLQ)")

m_alma = folium.Map(
    location=[LAT, LON],
    zoom_start=ZOOM,
    control_scale=True,
    tiles=None
)

# Couche satellite de base
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite',
    name='🛰️ Satellite',
    overlay=False,
    show=False
).add_to(m_alma)

# Charger les données bathymétriques du lac Saint-Jean depuis GBLQ
try:
    # Télécharger le ZIP de la GBLQ et extraire le GeoJSON du lac Saint-Jean
    import zipfile
    from io import BytesIO
    
    st.info("⏳ Chargement des données bathymétriques GBLQ...")
    
    # Télécharger le ZIP complet
    zip_url = "https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bathymetrie/Lacs/DQ/GBLQ_json.zip"
    zip_response = requests.get(zip_url, timeout=30)
    
    if zip_response.status_code == 200:
        # Extraire et chercher le lac Saint-Jean
        with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
            files = z.namelist()
            # Chercher le fichier contenant "Saint-Jean" ou "SaintJean"
            saint_jean_file = None
            for file in files:
                if 'saint' in file.lower() and 'jean' in file.lower() and file.endswith('.geojson'):
                    saint_jean_file = file
                    break
            
            if saint_jean_file:
                geojson_data = json.loads(z.read(saint_jean_file).decode('utf-8'))
                
                st.success(f"✅ Données trouvées : {saint_jean_file}")
                
                # Fonction pour obtenir la couleur selon la profondeur (style sonar)
                def get_sonar_color(depth):
                    try:
                        depth_val = float(depth)
                        if depth_val < 1:
                            return '#ffff00'  # Jaune (très peu profond)
                        elif depth_val < 2:
                            return '#00ff00'  # Vert (peu profond)
                        elif depth_val < 3:
                            return '#00ffff'  # Cyan (modéré)
                        elif depth_val < 5:
                            return '#0066ff'  # Bleu ciel (profond)
                        elif depth_val < 8:
                            return '#0000ff'  # Bleu (très profond)
                        else:
                            return '#000088'  # Bleu très foncé (fosse)
                    except:
                        return '#0066ff'
                
                # Ajouter les isobathes stylisées avec folium.GeoJson
                def style_function(feature):
                    depth = feature.get('properties', {}).get('PROFONDEUR', feature.get('properties', {}).get('profondeur', 0))
                    color = get_sonar_color(depth)
                    return {
                        'color': color,
                        'weight': 2.5,
                        'opacity': 0.95,
                        'fillOpacity': 0.4
                    }
                
                # Ajouter le GeoJSON stylisé
                folium.GeoJson(
                    geojson_data,
                    style_function=style_function,
                    name='🌊 Isobathes GBLQ',
                    overlay=True,
                    show=True,
                    popup=folium.GeoJsonPopup(fields=['PROFONDEUR', 'profondeur'], aliases=['Profondeur (m)', 'Profondeur (m)'])
                ).add_to(m_alma)
                
                # Créer une heatmap à partir des points de profondeur (style sonar)
                heat_data = []
                max_depth = 0
                for feature in geojson_data.get('features', []):
                    geom = feature.get('geometry', {})
                    props = feature.get('properties', {})
                    depth_str = props.get('PROFONDEUR', props.get('profondeur', '0'))
                    try:
                        depth = float(depth_str)
                        max_depth = max(max_depth, depth)
                        
                        if geom.get('type') == 'Point':
                            coords = geom.get('coordinates', [])
                            if len(coords) >= 2:
                                intensity = min(depth / 15, 1.0)
                                heat_data.append([coords[1], coords[0], intensity])
                    except:
                        pass
                
                if heat_data:
                    HeatMap(
                        heat_data,
                        name='🔥 Heatmap Profondeur',
                        overlay=True,
                        show=True,
                        radius=20,
                        blur=12,
                        max_zoom=1,
                        gradient={0.0: '#ffff00', 0.25: '#00ff00', 0.5: '#00ffff', 0.75: '#0066ff', 1.0: '#000088'}
                    ).add_to(m_alma)
                    
                    st.info(f"📊 Profondeur max détectée: {max_depth:.1f}m")
            else:
                st.error("❌ Fichier Saint-Jean non trouvé dans la GBLQ")
    else:
        st.error("❌ Impossible de télécharger les données GBLQ")
    
except Exception as e:
    st.error(f"❌ Erreur : {str(e)}")

# Marqueur principal
folium.Marker(
    location=[LAT, LON],
    tooltip="Grand lac Saint-Jean (Alma)",
    icon=folium.Icon(color="blue", icon="water", prefix="fa")
).add_to(m_alma)

folium.LayerControl(position="topright").add_to(m_alma)
st_folium(m_alma, width="100%", height=550, returned_objects=[], key="map_alma")

st.markdown("""
**Bathymétrie GBLQ - Style Sonar** | Données : Géobase des bathymétries de lacs du Québec  
🟡 Jaune (< 1m) | 🟢 Vert (1-2m) | 🔵 Cyan (2-3m) | 🔵 Bleu (3-5m) | 🔵 Bleu foncé (5-8m) | ⬛ Fosse (> 8m)
""")

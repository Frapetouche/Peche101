import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json
from folium.plugins import HeatMap
import numpy as np

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
    overlay=False
).add_to(m_alma)

# Charger les données bathymétriques du lac Saint-Jean depuis GBLQ
try:
    # URL directe GeoJSON pour lac Saint-Jean depuis la GBLQ
    geojson_url = "https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bathymetrie/Lacs/DQ/LacSaintJean.geojson"
    
    response = requests.get(geojson_url, timeout=5)
    if response.status_code == 200:
        geojson_data = response.json()
        
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
                'weight': 2,
                'opacity': 0.9,
                'fillOpacity': 0.3
            }
        
        def popup_function(feature):
            depth = feature.get('properties', {}).get('PROFONDEUR', feature.get('properties', {}).get('profondeur', 0))
            return folium.Popup(f"<b>Profondeur: {depth}m</b>", max_width=250)
        
        # Ajouter le GeoJSON stylisé
        folium.GeoJson(
            geojson_data,
            style_function=style_function,
            name='🌊 Isobathes (GBLQ)',
            overlay=True,
            popup=folium.GeoJsonPopup(fields=['PROFONDEUR', 'profondeur'], aliases=['Profondeur', 'Profondeur'])
        ).add_to(m_alma)
        
        # Créer une heatmap à partir des points de profondeur (style sonar)
        heat_data = []
        for feature in geojson_data.get('features', []):
            geom = feature.get('geometry', {})
            props = feature.get('properties', {})
            depth = float(props.get('PROFONDEUR', props.get('profondeur', 0)))
            
            if geom.get('type') == 'Point':
                coords = geom.get('coordinates', [])
                if len(coords) >= 2:
                    # Intensité de la heatmap basée sur la profondeur (normalisée)
                    intensity = min(depth / 15, 1.0)  # Normaliser sur 15m max
                    heat_data.append([coords[1], coords[0], intensity])
        
        if heat_data:
            HeatMap(
                heat_data,
                name='🔥 Heatmap Profondeur',
                overlay=True,
                radius=25,
                blur=15,
                max_zoom=1,
                gradient={0.0: '#ffff00', 0.25: '#00ff00', 0.5: '#00ffff', 0.75: '#0066ff', 1.0: '#000088'}
            ).add_to(m_alma)
    
except Exception as e:
    st.warning(f"⚠️ Données bathymétriques non disponibles: {str(e)}")

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

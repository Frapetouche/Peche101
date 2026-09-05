import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json

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
st.markdown("### 🗺️ Grand lac Saint-Jean d'Alma - Bathymétrie (GBLQ)")

m_alma = folium.Map(
    location=[LAT, LON],
    zoom_start=ZOOM,
    control_scale=True,
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite'
)

# Charger les données bathymétriques du lac Saint-Jean depuis GBLQ
try:
    # URL du répertoire GBLQ - chercher le fichier du lac Saint-Jean
    gblq_index_url = "https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bathymetrie/Lacs/DQ/Index_bathymetries_json.zip"
    
    # URL directe GeoJSON pour lac Saint-Jean (à adapter selon la structure GBLQ)
    geojson_url = "https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bathymetrie/Lacs/DQ/LacSaintJean.geojson"
    
    response = requests.get(geojson_url, timeout=5)
    if response.status_code == 200:
        geojson_data = response.json()
        
        # Fonction pour colorer les isobathes selon la profondeur
        def get_color_by_depth(depth):
            try:
                depth_val = float(depth)
                if depth_val < 2:
                    return '#0099ff'  # Bleu clair (peu profond)
                elif depth_val < 5:
                    return '#0055ff'  # Bleu moyen
                elif depth_val < 8:
                    return '#003377'  # Bleu foncé
                else:
                    return '#001144'  # Bleu très foncé (très profond)
            except:
                return '#0055ff'
        
        # Ajouter les isobathes au GeoJSON
        for feature in geojson_data.get('features', []):
            props = feature.get('properties', {})
            depth = props.get('PROFONDEUR', props.get('profondeur', 0))
            color = get_color_by_depth(depth)
            
            if feature.get('geometry', {}).get('type') == 'LineString':
                folium.PolyLine(
                    locations=[(coord[1], coord[0]) for coord in feature['geometry']['coordinates']],
                    color=color,
                    weight=2,
                    opacity=0.8,
                    popup=f"Profondeur: {depth}m"
                ).add_to(m_alma)
            elif feature.get('geometry', {}).get('type') == 'Point':
                folium.CircleMarker(
                    location=[feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]],
                    radius=5,
                    color=color,
                    fill=True,
                    fillOpacity=0.8,
                    popup=f"Fosse: {depth}m"
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
**Bathymétrie GBLQ** | Données : Géobase des bathymétries de lacs du Québec  
🔵 Bleu clair (< 2m) | 🔵 Bleu moyen (2-5m) | 🔵 Bleu foncé (5-8m) | 🔵 Bleu très foncé (> 8m)
""")

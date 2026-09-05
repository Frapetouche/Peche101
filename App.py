import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json
from folium.plugins import HeatMap
import zipfile
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Bathymétrie Lacs Québec", layout="wide", initial_sidebar_state="expanded")

st.title("🗺️ Bathymétrie des Lacs du Québec")
st.markdown("Explorez les profondeurs des lacs du Québec via la GBLQ")

# Fonction pour télécharger et extraire les données GBLQ
@st.cache_resource
def load_gblq_data():
    """Télécharge et traite toutes les données bathymétriques GBLQ"""
    try:
        st.info("⏳ Téléchargement des données GBLQ (50 Mo)...")
        
        zip_url = "https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bathymetrie/Lacs/DQ/GBLQ_json.zip"
        zip_response = requests.get(zip_url, timeout=60)
        
        if zip_response.status_code != 200:
            st.error("❌ Impossible de télécharger la GBLQ")
            return None
        
        # Extraire tous les lacs
        lacs_data = {}
        with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
            files = z.namelist()
            geojson_files = [f for f in files if f.endswith('.geojson')]
            
            st.info(f"📊 Traitement de {len(geojson_files)} fichiers lacs...")
            
            for i, file in enumerate(geojson_files):
                try:
                    geojson_content = json.loads(z.read(file).decode('utf-8'))
                    
                    # Extraire le nom du lac du nom du fichier
                    lac_name = file.replace('.geojson', '').replace('_', ' ').title()
                    
                    # Calculer les stats du lac
                    max_depth = 0
                    all_coords = []
                    feature_count = 0
                    
                    for feature in geojson_content.get('features', []):
                        feature_count += 1
                        props = feature.get('properties', {})
                        depth_str = props.get('PROFONDEUR', props.get('profondeur', '0'))
                        try:
                            depth = float(depth_str)
                            max_depth = max(max_depth, depth)
                        except:
                            pass
                        
                        geom = feature.get('geometry', {})
                        if geom.get('type') == 'Point':
                            coords = geom.get('coordinates', [])
                            if len(coords) >= 2:
                                all_coords.append([coords[1], coords[0]])
                    
                    # Calculer le centre du lac
                    if all_coords:
                        center_lat = sum(c[0] for c in all_coords) / len(all_coords)
                        center_lon = sum(c[1] for c in all_coords) / len(all_coords)
                        
                        lacs_data[lac_name] = {
                            'nom': lac_name,
                            'lat': center_lat,
                            'lon': center_lon,
                            'profondeur_max': max_depth,
                            'nb_points': feature_count,
                            'geojson': geojson_content
                        }
                except Exception as e:
                    pass
        
        st.success(f"✅ {len(lacs_data)} lacs chargés avec succès!")
        return lacs_data
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return None

# Charger les données
lacs_data = load_gblq_data()

if lacs_data:
    # Créer une liste des lacs triée par profondeur max
    lacs_list = sorted(lacs_data.items(), key=lambda x: x[1]['profondeur_max'], reverse=True)
    lacs_names = [lac[0] for lac in lacs_list]
    
    # Sidebar pour sélectionner le lac
    st.sidebar.markdown("### 🎣 Sélectionnez un lac")
    lac_selected = st.sidebar.selectbox(
        "Lacs disponibles",
        lacs_names,
        index=0
    )
    
    # Afficher les stats du lac
    lac_info = lacs_data[lac_selected]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Lac sélectionné", lac_selected)
    with col2:
        st.metric("🌊 Profondeur max", f"{lac_info['profondeur_max']:.1f} m")
    with col3:
        st.metric("📊 Points de données", lac_info['nb_points'])
    
    # Créer la carte
    st.markdown(f"### 🗺️ Bathymétrie - {lac_selected}")
    
    m = folium.Map(
        location=[lac_info['lat'], lac_info['lon']],
        zoom_start=13,
        control_scale=True,
        tiles=None
    )
    
    # Tuile satellite
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite',
        name='🛰️ Satellite',
        overlay=False,
        show=True
    ).add_to(m)
    
    # Fonction pour colorer selon la profondeur (style sonar)
    def get_sonar_color(depth):
        try:
            depth_val = float(depth)
            if depth_val < 1:
                return '#ffff00'
            elif depth_val < 2:
                return '#00ff00'
            elif depth_val < 3:
                return '#00ffff'
            elif depth_val < 5:
                return '#0066ff'
            elif depth_val < 8:
                return '#0000ff'
            else:
                return '#000088'
        except:
            return '#0066ff'
    
    # Ajouter les isobathes
    def style_function(feature):
        depth = feature.get('properties', {}).get('PROFONDEUR', feature.get('properties', {}).get('profondeur', 0))
        color = get_sonar_color(depth)
        return {
            'color': color,
            'weight': 2,
            'opacity': 0.9,
            'fillOpacity': 0.3
        }
    
    folium.GeoJson(
        lac_info['geojson'],
        style_function=style_function,
        name='🌊 Isobathes GBLQ',
        overlay=True,
        show=True,
        popup=folium.GeoJsonPopup(fields=['PROFONDEUR', 'profondeur'], aliases=['Profondeur (m)', 'Profondeur (m)'])
    ).add_to(m)
    
    # Ajouter heatmap
    heat_data = []
    for feature in lac_info['geojson'].get('features', []):
        geom = feature.get('geometry', {})
        props = feature.get('properties', {})
        depth_str = props.get('PROFONDEUR', props.get('profondeur', '0'))
        try:
            depth = float(depth_str)
            if geom.get('type') == 'Point':
                coords = geom.get('coordinates', [])
                if len(coords) >= 2:
                    intensity = min(depth / max(lac_info['profondeur_max'], 15), 1.0)
                    heat_data.append([coords[1], coords[0], intensity])
        except:
            pass
    
    if heat_data:
        HeatMap(
            heat_data,
            name='🔥 Heatmap Profondeur',
            overlay=True,
            show=False,
            radius=20,
            blur=15,
            max_zoom=1,
            gradient={0.0: '#ffff00', 0.25: '#00ff00', 0.5: '#00ffff', 0.75: '#0066ff', 1.0: '#000088'}
        ).add_to(m)
    
    # Marqueur du centre
    folium.Marker(
        location=[lac_info['lat'], lac_info['lon']],
        tooltip=lac_selected,
        icon=folium.Icon(color="blue", icon="water", prefix="fa")
    ).add_to(m)
    
    folium.LayerControl(position="topright").add_to(m)
    st_folium(m, width="100%", height=600, returned_objects=[], key="map_main")
    
    # Légende
    st.markdown("""
    **Profondeurs - Style Sonar GBLQ**
    
    | Couleur | Profondeur | 
    |---------|-----------|
    | 🟡 Jaune | < 1 m |
    | 🟢 Vert | 1-2 m |
    | 🔵 Cyan | 2-3 m |
    | 🔵 Bleu ciel | 3-5 m |
    | 🔵 Bleu | 5-8 m |
    | ⬛ Bleu foncé | > 8 m |
    """)
    
    # Afficher la liste de tous les lacs
    st.markdown("### 📋 Tous les lacs disponibles")
    
    df_lacs = pd.DataFrame([
        {
            'Lac': lac[0],
            'Profondeur max (m)': f"{lac[1]['profondeur_max']:.1f}",
            'Points de données': lac[1]['nb_points']
        }
        for lac in lacs_list
    ])
    
    st.dataframe(df_lacs, use_container_width=True)
    
else:
    st.error("❌ Impossible de charger les données. Vérifiez votre connexion internet.")

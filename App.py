import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Guide Pêche QC", layout="wide", initial_sidebar_state="collapsed")

LAT, LON, ZOOM = 48.45520, -71.05210, 13
url_garmin = f"https://webapp.navionics.com/?lang=en#boating@13@{LAT},{LON}"

# Plein écran : on retire les marges et le padding de Streamlit
st.markdown("""
    <style>
        .stApp { max-width: 100%; padding: 0; margin: 0; }
        .block-container { padding-top: 0; padding-bottom: 0; }
        iframe { border: none; }
        div[data-baseweb="tab-list"] { gap: 0; }
        div[data-baseweb="tab"] { flex: 1; text-align: center; }
    </style>
""", unsafe_allow_html=True)

tab_satellite, tab_garmin = st.tabs(["🛰️ Satellite & Topo", "🧭 Bathymétrie Garmin / Navionics"])

with tab_satellite:
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
    st_folium(m, width="100%", height=800, returned_objects=[], key="map_fixe")

with tab_garmin:
    st.markdown(f"""
    <style>
        .garmin-container {{
            position: relative;
            width: 100%;
            height: 800px;
            background: linear-gradient(135deg, #0c4a6e 0%, #0f172a 100%);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border: 1px solid #1e3a5f;
        }}
        .garmin-container::before {{
            content: '';
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(rgba(56, 189, 248, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(56, 189, 248, 0.08) 1px, transparent 1px);
            background-size: 40px 40px;
            opacity: 0.5;
        }}
        .garmin-content {{
            position: relative;
            z-index: 1;
            text-align: center;
            padding: 40px;
        }}
        .garmin-title {{
            color: #f1f5f9;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .garmin-subtitle {{
            color: #7dd3fc;
            font-size: 1rem;
            margin-bottom: 8px;
        }}
        .garmin-desc {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 30px;
            max-width: 400px;
            line-height: 1.5;
        }}
        .garmin-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #004b87, #0284c7);
            color: white;
            padding: 18px 40px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            box-shadow: 0 4px 20px rgba(2, 132, 199, 0.4);
            transition: transform 0.2s;
        }}
        .garmin-btn:hover {{
            transform: scale(1.05);
        }}
        .garmin-coords {{
            color: #475569;
            font-size: 0.8rem;
            margin-top: 20px;
            font-family: monospace;
        }}
    </style>
    <div class="garmin-container">
        <div class="garmin-content">
            <div class="garmin-title">🗺️ Cartes Isobathes HD</div>
            <div class="garmin-subtitle">Bathymétrie Garmin / Navionics</div>
            <div class="garmin-desc">Visualisez les profondeurs et structures sous-marines en plein écran avec les cartes bathymétriques HD Garmin Navionics.</div>
            <a href="{url_garmin}" target="_blank" class="garmin-btn">🧭 Ouvrir en plein écran</a>
            <div class="garmin-coords">{LAT}°N, {LON}°W — Zoom {ZOOM}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

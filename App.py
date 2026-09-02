import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

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
    components.html(f"""
    <div style="background-color: #1e293b; padding: 40px; border-radius: 10px; border: 1px solid #334155; text-align: center; min-height: 470px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: sans-serif;">
        <h3 style="color: #f1f5f9; margin-bottom: 20px;">Cartes Isobathes HD</h3>
        <p style="color: #94a3b8; margin-bottom: 30px;">Visualisez les profondeurs et structures sous-marines en simultané.</p>
        <a id="garmin-link" href="{url_garmin}" target="_blank" style="background-color: #004b87; color: white; padding: 15px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1rem;">🗺️ Ouvrir Garmin / Navionics</a>
        <p id="garmin-status" style="color: #64748b; font-size: 0.85rem; margin-top: 15px;">📍 Détection de votre position…</p>
    </div>
    <script>
    function updateGarminLink(lat, lon) {{
        var link = document.getElementById('garmin-link');
        var status = document.getElementById('garmin-status');
        if (lat && lon) {{
            link.href = "https://webapp.navionics.com/?lang=en#boating@13@" + lat + "," + lon;
            status.textContent = "📍 Position : " + lat.toFixed(5) + ", " + lon.toFixed(5);
            status.style.color = "#22c55e";
        }}
    }}
    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(
            function(pos) {{
                updateGarminLink(pos.coords.latitude, pos.coords.longitude);
            }},
            function(err) {{
                var status = document.getElementById('garmin-status');
                if (err.code === 1) {{
                    status.textContent = "⚠️ Autorisez la localisation pour ouvrir à votre position";
                }} else {{
                    status.textContent = "📍 Position par défaut (cassure principale)";
                }}
                status.style.color = "#f59e0b";
            }},
            {{enableHighAccuracy: true, timeout: 10000}}
        );
    }} else {{
        document.getElementById('garmin-status').textContent = "📍 Position par défaut (cassure principale)";
    }}
    </script>
    """, height=550)

import json
import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.set_page_config(page_title="Guide Pêche QC", layout="wide", initial_sidebar_state="collapsed")

LAT, LON, ZOOM = 48.45520, -71.05210, 13
url_garmin = f"https://webapp.navionics.com/?lang=en#boating@13@{LAT},{LON}"

# --- Charger les cartes bathymétriques géoréférencées du grand lac Saint-Jean ---
with open("data/lac_saint_jean_overlay.b64", "r") as f:
    _overlay_b64 = f.read()
with open("data/lac_saint_jean_garmin.b64", "r") as f:
    _garmin_b64 = f.read()

# Bounds calculés par géoréférencement des grilles de la carte 1961 (CEHQ)
SJ_BOUNDS = {
    "north": 48.79167,
    "south": 48.41236,
    "west": -72.60181,
    "east": -71.54024,
}
SJ_CENTER_LAT, SJ_CENTER_LON = 48.602, -72.071

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

# ─── Section Bathymétrie multi-lacs ───
st.markdown("---")
st.markdown("## 📐 Bathymétrie — Lacs du Québec")

# Catalogue des lacs disponibles
LACS = {
    "Grand Lac Saint-Jean (Alma)": {
        "center": [48.602, -72.071],
        "zoom": 10,
        "max_depth": 63.1,
        "source": "Carte bathymétrique historique 00602 (1961, CEHQ / MELCCFP)",
        "type": "raster_garmin",
    },
    "Lac Kénogami (Saguenay)": {
        "center": [48.348, -71.383],
        "zoom": 12,
        "max_depth": 103.18,
        "fosse_lat": 48.308438,
        "fosse_lon": -71.323507,
        "source": "GBLQ 00281 (1969, Ministère des Richesses naturelles)",
        "type": "vector",
        "geojson": "data/kenogami_isobathes.geojson",
    },
    "Réservoir La Mothe (Saint-Ambroise, Saguenay)": {
        "center": [48.784, -71.154],
        "zoom": 11,
        "max_depth": None,
        "source": "Réservoir Hydro-Québec (rivière Shipshaw) — données bathymétriques non disponibles dans la GBLQ",
        "type": "satellite",
    },
}

def depth_color(depth):
    """Couleur des isobathes selon la profondeur (gradient bleu)."""
    if depth < 3:
        return "#67e8f9"   # cyan clair (peu profond)
    elif depth < 6:
        return "#22d3ee"   # cyan
    elif depth < 10:
        return "#0ea5e9"   # bleu ciel
    elif depth < 20:
        return "#2563eb"   # bleu
    elif depth < 40:
        return "#1e40af"   # bleu foncé
    elif depth < 60:
        return "#1e3a8a"   # bleu marine
    elif depth < 80:
        return "#172554"   # bleu nuit
    else:
        return "#0f172a"   # presque noir

lac_nom = st.selectbox("Choisir un lac", list(LACS.keys()), index=0)
lac = LACS[lac_nom]

if lac["max_depth"]:
    st.markdown(f"**Profondeur maximale: {lac['max_depth']}m** — {lac['source']}")
else:
    st.markdown(f"**{lac['source']}**")

m_bathy = folium.Map(location=lac["center"], zoom_start=lac["zoom"], control_scale=True, tiles=None)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite', name='🛰️ Satellite', overlay=False
).add_to(m_bathy)

folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap', name='⛰️ Topo', overlay=False
).add_to(m_bathy)

if lac["type"] == "raster_garmin":
    # Grand Lac Saint-Jean: superposition de la carte 1961 colorisée style Garmin
    garmin_url = f"data:image/jpeg;base64,{_garmin_b64}"
    folium.raster_layers.ImageOverlay(
        image=garmin_url,
        bounds=[[SJ_BOUNDS["south"], SJ_BOUNDS["west"]], [SJ_BOUNDS["north"], SJ_BOUNDS["east"]]],
        name="📐 Carte bathymétrique 1961 (couleur Garmin)",
        opacity=0.85,
    ).add_to(m_bathy)
    # Option: couche originale N&B aussi disponible
    overlay_url = f"data:image/jpeg;base64,{_overlay_b64}"
    folium.raster_layers.ImageOverlay(
        image=overlay_url,
        bounds=[[SJ_BOUNDS["south"], SJ_BOUNDS["west"]], [SJ_BOUNDS["north"], SJ_BOUNDS["east"]]],
        name="📐 Carte bathymétrique 1961 (N&B original)",
        opacity=0,
    ).add_to(m_bathy)
elif lac["type"] == "satellite":
    # Lacs sans données bathymétriques: vue satellite uniquement
    folium.Marker(
        location=lac["center"],
        tooltip=lac_nom,
        icon=folium.Icon(color="blue", icon="info-sign", prefix="fa"),
    ).add_to(m_bathy)
else:
    # Lacs vectoriels: isobathes colorées depuis GeoJSON
    with open(lac["geojson"], "r") as f:
        isobathes = json.load(f)

    for feature in isobathes["features"]:
        depth = feature["properties"]["PROFONDEUR_M"]
        color = depth_color(depth)
        geom = feature["geometry"]

        if geom["type"] == "MultiLineString":
            for line in geom["coordinates"]:
                folium.PolyLine(
                    locations=[(pt[1], pt[0]) for pt in line],
                    color=color,
                    weight=2,
                    opacity=0.85,
                    tooltip=f"{depth}m",
                    name=f"Isobathe {depth}m",
                ).add_to(m_bathy)
        elif geom["type"] == "LineString":
            folium.PolyLine(
                locations=[(pt[1], pt[0]) for pt in geom["coordinates"]],
                color=color,
                weight=2,
                opacity=0.85,
                tooltip=f"{depth}m",
                name=f"Isobathe {depth}m",
            ).add_to(m_bathy)

    # Marquer la fosse (point le plus profond)
    if "fosse_lat" in lac:
        folium.Marker(
            location=[lac["fosse_lat"], lac["fosse_lon"]],
            tooltip=f"Fosse: {lac['max_depth']}m",
            icon=folium.Icon(color="red", icon="info-sign", prefix="fa"),
        ).add_to(m_bathy)

folium.LayerControl(position="topright", collapsed=False).add_to(m_bathy)
st_folium(m_bathy, width="100%", height=600, returned_objects=[], key=f"map_bathy_{lac_nom}")

st.caption(f"Source: {lac['source']} — Licence ouverte du gouvernement du Québec (CC-BY 4.0)")

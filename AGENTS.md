# Peche101 — Base44 Dev Notes

## What this is
A Streamlit single-file app (`App.py`) showing a Quebec fishing spot with
folium satellite/topo maps on the left and a Navionics/Garmin bathymetry link
on the right. French UI.

## Stack
- Python 3.12, Streamlit, folium, streamlit-folium
- No database, no external credentials. Map tiles come from public Esri /
  OpenTopoMap endpoints; the right panel links out to Navionics.

## Running
`docker compose -f docker-compose.base44.yml up -d`
- Streamlit listens on container port 8501, mapped to host port 3000.
- Source is bind-mounted; `--server.runOnSave true` reruns the app on edits.
- First boot installs pip deps, so it takes ~20-30s before the page serves.
- Streamlit config lives in `.streamlit/config.toml`. `enableCORS=false` is
  REQUIRED — without it Streamlit rejects the preview's cross-origin WebSocket
  and the app shell loads but never renders content.

## Verify
- `curl -sf -H "Host: external-preview.example.com" http://localhost:3000/`
  returns the Streamlit shell HTML.
- Preview shows two columns: a folium map (left) and a dark Navionics card (right).

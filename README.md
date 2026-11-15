# 🚀 COSMIC TRAIL — Offline Marswalk Planner

**Team CosmiCore · NASA Space Apps 2026**  
Challenge: *Interplanetary Survival Guide: Martian Map*

---

## NASA Data Sources

COSMIC TRAIL uses five official NASA and USGS resources for this challenge
(full details in [DATA_SOURCES.md](DATA_SOURCES.md)):

| Resource | URL | How COSMIC TRAIL Uses It |
|----------|-----|--------------------------|
| Mars Trek | [trek.nasa.gov/mars](https://trek.nasa.gov/mars) | Surface map images for the 3D Mars globe |
| USGS Planetary Mapping | [astrogeology-usgs.hub.arcgis.com](https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars) | Rock and ground type zones for Gale Crater |
| Curiosity Proposed Path | [science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp](https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/) | Real Curiosity rover path shown on the map |
| NASA Worldview | [worldview.earthdata.nasa.gov](https://worldview.earthdata.nasa.gov/) | Dust storm and weather hazard information |
| Perseverance Raw Images | [mars.nasa.gov/mars2020/multimedia/raw-images](https://mars.nasa.gov/mars2020/multimedia/raw-images/) | Real surface photos for science context |

---

## What is COSMIC TRAIL? (Simple Overview)

**COSMIC TRAIL** is an easy-to-use, offline tool that helps you plan safe walking routes on Mars.

Using real NASA satellite height maps of **Gale Crater**, the app calculates and compares two paths between any two points you pick:
1. **Shortest Path:** The most direct line from start to finish (which may cross dangerous, steep hills).
2. **Safest Path (Terrain-Weighted):** A smarter route that goes around steep slopes and rough ground so an astronaut or rover can travel more safely.

You can explore Mars on an interactive 3D globe, switch between ground height and slope views, check water-related mineral spots, and ask the built-in offline **ARIA assistant** simple questions about your route.

> **Note:** This app is built for **learning, education, and demonstration**. It is not certified for real space missions or actual rover navigation.

---

## Demo Scenario (Step-by-Step Walkthrough)

**Scenario: Planning a Safe Astronaut Walk in Gale Crater (Toward Mount Sharp)**

Follow these steps during a live demo to see how COSMIC TRAIL works:

1. **Explore the 3D Mars Globe:**
   Open the app at `http://127.0.0.1:5173`. Rotate the 3D Mars globe and zoom into **Gale Crater** (where NASA's Curiosity rover landed). Adjust the **vertical exaggeration slider (1×–5×)** to clearly see the height of the crater walls and Mount Sharp.
2. **Turn On Map Layers:**
   Switch between the **Elevation**, **Slope**, and **Hillshade** layers to spot flat landing areas versus steep, risky slopes. Toggle on the **Minerals Layer** and **Curiosity Proposed Path** to see real NASA science targets nearby.
3. **Pick Start and End Points:**
   Click on a flat area on the Gale Crater floor to set your **Start Point**, then click higher up near the base of **Mount Sharp** (near a mineral site) to set your **Destination**.
4. **Compare the Two Routes:**
   Watch COSMIC TRAIL draw two paths on the map:
   - The **Shortest Route** cuts straight across steep slopes (exceeding the 10°–15° safety limit).
   - The **Safest Route** curves around the steep hills to keep the climb gentle and safe.
   Check the **Elevation Chart** at the bottom to compare total distance, climb height, and maximum slope angle.
5. **Ask the Offline ARIA Assistant:**
   Click the floating **🤖 ARIA** chat button and ask: *"What is the maximum slope on this route?"* or *"Are there any hazards nearby?"* ARIA immediately replies offline using the loaded NASA data and shows the exact data source.
6. **Save and Export the Mission Plan:**
   Save your route to the local database and click **Export Briefing / GeoJSON** to download a ready-to-share mission summary.

---

## Quick Start

📖 **Full step-by-step guide for Windows, macOS and Linux, with checks and troubleshooting:
[LOCAL_SETUP.md](LOCAL_SETUP.md).**

You need **Git**, **Python 3.11–3.14** and **Node.js 22+**. The code is on GitHub; the
data (about 236 MB) is on [Hugging Face](https://huggingface.co/datasets/irhabatool/cosmic-trail-data)
because it is too large for Git.

```bash
# 1. Code
git clone https://github.com/IB-Mustafa/Cosmic_Trail_A_Mars_Map.git
cd Cosmic_Trail_A_Mars_Map

# 2. Backend packages (activate on Windows: .venv\Scripts\activate)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Data from Hugging Face (~236 MB, checksum-verified)
python scripts/download_data.py

# 4. Frontend packages + backend address
cd frontend
npm ci
echo "VITE_API_BASE=http://127.0.0.1:8000" > .env.local
cd ..
```

Then run the two servers in two terminals:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000   # terminal 1 (repo root, venv active)
cd frontend && npm run dev -- --host 127.0.0.1                # terminal 2
```

and open **http://127.0.0.1:5173**. On Windows, run `$env:PYTHONUTF8 = "1"` (PowerShell) before
the backend; see [LOCAL_SETUP.md](LOCAL_SETUP.md) for the Windows commands and for fixes to
common problems.

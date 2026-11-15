# COSMIC TRAIL — Beginner Setup Guide (Windows)

> ⚠️ **Outdated — use [LOCAL_SETUP.md](LOCAL_SETUP.md) instead.**
> This page describes an older version of the app (OpenLayers page served on port 8000,
> no Node.js). The current app has a React/Vite frontend that needs **Node.js 22+**, runs at
> **http://127.0.0.1:5173**, and downloads its data from Hugging Face with
> `python scripts/download_data.py`. It is kept here for reference only.

This guide walks you through every step from a fresh Windows machine.  
You do **not** need Node.js, npm, or any other tools beyond Python.

---

## Step 1 — Install Python 3.11 or newer

1. Go to https://www.python.org/downloads/
2. Download the **Windows installer** for the latest Python 3.x.
3. Run the installer.  
   ✅ **IMPORTANT:** Check the box **"Add Python to PATH"** before clicking Install.
4. Open **Command Prompt** (`Win + R`, type `cmd`, press Enter).
5. Verify: `python --version` — it should print something like `Python 3.12.x`.

---

## Step 2 — Download COSMIC TRAIL

If you have the ZIP file from the submission:

1. Right-click the ZIP → **Extract All…**
2. Choose a folder (e.g. `C:\Users\YourName\cosmic-trail`)
3. Open that folder in **File Explorer**

If you have git:
```
git clone https://github.com/cosmicgirls/cosmic-trail.git
cd cosmic-trail
```

---

## Step 3 — Open in VS Code (optional but recommended)

1. Open VS Code.
2. File → Open Folder → select the `cosmic-trail` folder.
3. Open the **Terminal** in VS Code: `` Ctrl+` `` (backtick)

---

## Step 4 — Create a virtual environment

In the terminal, type each command and press Enter:

```
python -m venv .venv
.venv\Scripts\activate
```

Your prompt should now start with `(.venv)`.

---

## Step 5 — Install dependencies

```
pip install -r requirements.txt
```

This takes a minute or two. It downloads FastAPI, NumPy, Rasterio, and
OpenLayers is already bundled (no download needed).

---

## Step 6 — Generate the demo terrain

```
python scripts/make_synthetic_demo.py
```

Expected output:
```
Generating synthetic terrain …
✓ metadata.json
✓ analysis.npz   sha256=…
✓ elevation.png  slope.png  hillshade.png  thumbnail.png

⚠️  SYNTHETIC DATA — this dataset is for demonstration only.
   Run scripts/prepare_data.py to work with real NASA data.
slope median: 5.77 p95: 13.89
```

---

## Step 7 — Start the app

```
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Step 8 — Open the app

Open your browser and go to:  
👉 **http://127.0.0.1:8000**

You should see the COSMIC TRAIL interface with the synthetic terrain map.

---

## Step 9 — Try a route (demo)

1. Click **PLAN** tab (already selected).
2. Click the map near the centre to place your **start point**.
3. Click elsewhere on the map to place your **destination**.
4. Click **🗺 Compute Route**.
5. Two routes appear — blue (shortest) and orange (terrain-weighted).

For the full 90-second demo script, see **DEMO_SCRIPT.md**.

---

## Step 10 — Real NASA data (optional, requires internet)

```
python scripts/prepare_data.py
```

This tries to download the HiRISE DTM (444 MB). It needs an internet
connection and may take several minutes.

If it fails (the NASA server may not be reachable), the script prints
manual download instructions. See **DATA_SOURCES.md** for the URLs.

---

## Stopping the app

In the terminal, press `Ctrl + C`.

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `python: command not found` | Reinstall Python and check "Add to PATH" |
| `ModuleNotFoundError: fastapi` | Make sure your venv is active: `.venv\Scripts\activate` |
| `Address already in use` | Another app is on port 8000. Use `--port 8001` |
| Browser shows "Cannot connect" | Make sure uvicorn is still running in the terminal |
| `rasterio` install fails | Try `pip install rasterio --no-binary rasterio` |

---

## Running the tests

```
pytest tests/ -v
```

Expected: **107 passed**.

---

## File locations

| File | What it is |
|------|-----------|
| `data/synthetic_demo/` | Synthetic demo terrain (safe to delete and regenerate) |
| `data/plans.db` | Your saved route plans (SQLite database) |
| `data/hirise_gale/` | Real HiRISE data (created by prepare_data.py) |

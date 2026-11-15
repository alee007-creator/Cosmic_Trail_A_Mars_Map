# Running COSMIC TRAIL locally

This guide takes you from nothing to the full app running on your own computer:
**Windows, macOS or Linux**. Follow the steps in order; each one says how to check that it
worked before you move on.

COSMIC TRAIL has three parts, and you need all three:

| Part | What it is | Where it comes from |
|------|------------|---------------------|
| **Backend** | Python / FastAPI server: terrain, routing, ARIA, map tiles | this GitHub repo (`app/`) |
| **Frontend** | React + Vite + Cesium web app (the 3D globe and panels) | this GitHub repo (`frontend/`) |
| **Data** | HiRISE terrain grid, HiRISE photo mosaic, map layers (~236 MB) | **Hugging Face** (too large for Git) |

When everything runs you have two local servers:

```
 your browser ──► http://127.0.0.1:5173   frontend (Vite dev server)  ── opens this one
                         │
                         └─ API calls ──► http://127.0.0.1:8000   backend (uvicorn) ── reads data/
```

> **Short version** for people who have done this before: clone the repo, then
> `python -m venv .venv` → activate → `pip install -r requirements.txt` →
> `python scripts/download_data.py` → `cd frontend && npm ci` →
> create `frontend/.env.local` with `VITE_API_BASE=http://127.0.0.1:8000` →
> start `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` (repo root) and
> `npm run dev -- --host 127.0.0.1` (frontend/) → open **http://127.0.0.1:5173**.
> Everything below explains each step and what to do when something goes wrong.

---

## Contents

0. [What you need](#0-what-you-need)
1. [Get the code](#1-get-the-code)
2. [Set up Python (backend)](#2-set-up-python-backend)
3. [Download the data from Hugging Face](#3-download-the-data-from-hugging-face)
4. [Set up the frontend](#4-set-up-the-frontend)
5. [Start the app](#5-start-the-app)
6. [Check that everything works](#6-check-that-everything-works)
7. [Stopping and restarting](#7-stopping-and-restarting)
8. [Running the tests](#8-running-the-tests)
9. [Updating to a newer version](#9-updating-to-a-newer-version)
10. [Troubleshooting](#10-troubleshooting)
11. [Advanced: rebuilding the data from the raw NASA files](#11-advanced-rebuilding-the-data-from-the-raw-nasa-files)
12. [Reference: files, folders and ports](#12-reference-files-folders-and-ports)

---

## 0. What you need

| Tool | Version | Check with | Get it from |
|------|---------|------------|-------------|
| **Git** | any recent | `git --version` | https://git-scm.com/downloads |
| **Python** | **3.11 – 3.14**, 64-bit | `python --version` (macOS/Linux: `python3 --version`) | https://www.python.org/downloads/ |
| **Node.js** (includes npm) | **22 or newer** (LTS recommended) | `node --version` and `npm --version` | https://nodejs.org/ |

- **Node.js must be 22+.** The globe library (Cesium 1.146) declares Node 22 as its minimum;
  with older versions `npm ci` warns (`EBADENGINE`) and the app may fail to build or start.
- **Windows:** when installing Python, tick **"Add python.exe to PATH"**. If `python` opens
  the Microsoft Store or isn't found, use the Python launcher `py` instead (e.g. `py -3 -m venv .venv`).
- **macOS:** use `python3` wherever this guide says `python` until the virtual environment
  is active (inside it, `python` works). Homebrew works too: `brew install python node git`.
- **Linux (Debian/Ubuntu):** `sudo apt install git python3 python3-venv python3-pip`, then
  install Node.js 22 from https://nodejs.org/ or NodeSource (distribution packages are often too old).

**Disk space:** about **1.5 GB** in total: Python packages ~420 MB, frontend packages a few hundred MB,
data ~236 MB. (The optional raw source data in section 11 adds ~9.5 GB.)

**Internet:** needed for setup (GitHub, PyPI, npm, Hugging Face). Afterwards the app runs
**offline**, except the coloured Mars basemap on the globe, which is streamed from NASA Mars Trek
(offline the globe shows a plain base colour; the HiRISE terrain and photo layers still work).

**Terminal:** you will type commands in a terminal: **PowerShell** on Windows (or Command Prompt /
Git Bash), **Terminal** on macOS / Linux. Where commands differ by system, both versions are shown.
You will need **two terminal windows** at the end (one per server).

---

## 1. Get the code

Pick a folder for the project, open a terminal there, and run:

```bash
git clone https://github.com/IB-Mustafa/Cosmic_Trail_A_Mars_Map.git
cd Cosmic_Trail_A_Mars_Map
```

All later commands are run **from this folder** (the "repo root") unless a step says
`cd frontend`.

✅ **Check:** `ls` (or `dir` on Windows) shows `app`, `frontend`, `scripts`, `tests`,
`requirements.txt` and this `LOCAL_SETUP.md`. There is **no `data` folder yet**; that comes
from Hugging Face in step 3.

---

## 2. Set up Python (backend)

### 2.1 Create a virtual environment

A virtual environment (`.venv`) keeps this project's Python packages separate from the rest of
your computer. Create it once:

**Windows (PowerShell or Command Prompt):**
```powershell
python -m venv .venv
```
(or `py -3 -m venv .venv` if `python` isn't found)

**macOS / Linux:**
```bash
python3 -m venv .venv
```

### 2.2 Activate it

Do this **in every new terminal** you use for the backend:

| Terminal | Command |
|----------|---------|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |
| Windows Git Bash | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

✅ **Check:** your prompt now starts with `(.venv)`, and `python --version` shows 3.11–3.14.

> **PowerShell says "running scripts is disabled on this system"?** Either use Command Prompt
> instead, or allow scripts for your user once with
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then open a new PowerShell.
> (You can also skip activation entirely and call the venv's Python directly:
> `.venv\Scripts\python.exe -m ...` on Windows, `.venv/bin/python -m ...` on macOS/Linux.)

### 2.3 Install the Python packages

With the venv active, from the repo root:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

| Package | Why |
|---------|-----|
| `fastapi`, `uvicorn[standard]` | the web server |
| `numpy`, `Pillow` | terrain grids and map images |
| `rasterio`, `pyproj` | read the HiRISE photo mosaic (GeoTIFF) for the **HiRISE photo** layer |
| `numba` | compiles the route search to native code; long routes take ~1 s instead of minutes |
| `huggingface_hub` | downloads the data in step 3 |
| `httpx`, `pytest`, `pytest-asyncio` | only for running the tests |

All of these come as ready-made "wheels" for Windows, macOS (Intel and Apple Silicon) and Linux
on Python 3.11–3.14, so **no compiler and no separate GDAL install is needed**. It takes a minute
or two.

✅ **Check:**
```bash
python -c "import fastapi, numpy, rasterio, pyproj, numba, huggingface_hub; print('backend packages OK')"
```

> If `rasterio` (or `pyproj`) refuses to install on an unusual platform, the app still runs:
> only the **HiRISE photo** layer is unavailable. If `numba` is missing, routes still work but
> long routes are much slower (the pure-Python search is used).

---

## 3. Download the data from Hugging Face

The data lives in the public Hugging Face dataset
**[irhabatool/cosmic-trail-data](https://huggingface.co/datasets/irhabatool/cosmic-trail-data)**.
No Hugging Face account or token is needed.

That dataset is about **9.7 GB**, but **9.5 GB of it is raw source files** (original HiRISE
terrain models, USGS and MOLA mosaics) that the app never reads; they are only inputs for
rebuilding the data (section 11). The included script downloads **only what the app uses
(~236 MB)** and checks it.

With the venv active, from the repo root:

```bash
python scripts/download_data.py
```

It lists what it will fetch, downloads it into `data/`, and verifies the terrain grids against
the SHA-256 checksums stored in their `metadata.json`. Expected ending:

```
Verifying ...
  checksum OK       data/hirise_gale/analysis.npz
  checksum OK       data/synthetic_demo/analysis.npz
Done. Start the backend with:  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

You then have:

```
data/
├── hirise_gale/                  ← the REAL terrain (HiRISE, Gale Crater) — the app uses this by default
│   ├── analysis.npz              52 MB   elevation + slope grid (5 m cells) used for routing
│   ├── ortho_mosaic.tif         145 MB   HiRISE photo mosaic → "📷 HiRISE photo" layer
│   ├── elevation.png  slope.png  hillshade.png   draped terrain layers
│   ├── fill_overlay.png  thumbnail.png
│   └── metadata.json                     provenance, checksums
├── synthetic_demo/               ← generated test terrain (fallback; used by tests)
├── terrain_context.npz           10 MB   MOLA heights around Gale for the 3D globe
├── minerals/aqueous_minerals.json        mineral detection sites layer
├── usgs_geologic_units.geojson           geologic units layer
├── hazard_zones.geojson                  dune hazard zones
└── curiosity_official_route.geojson      Curiosity's proposed path
```

`data/` is in `.gitignore`. It is never committed, so every computer downloads it once.
Running the script again only fetches files that are missing or changed. (It also creates a
small `data/.cache/` folder for that bookkeeping; leave it.)

✅ **Check:** `data/hirise_gale/analysis.npz` and `data/hirise_gale/ortho_mosaic.tif` exist.

<details>
<summary><b>Other download options</b> (only if the script doesn't work for you)</summary>

- **Everything, including the 9.5 GB of raw files:** `python scripts/download_data.py --include-raw`
- **By hand / with curl:** every file is at
  `https://huggingface.co/datasets/irhabatool/cosmic-trail-data/resolve/main/<path>`.
  Download each file listed in the tree above (skip `hirise_gale/raw/`) and save it under `data/`
  with the **same relative path**, e.g.
  `curl -fL -o data/hirise_gale/analysis.npz https://huggingface.co/datasets/irhabatool/cosmic-trail-data/resolve/main/hirise_gale/analysis.npz`
  (create the folders first).
- **Behind a proxy or slow network:** the script uses the standard `HTTPS_PROXY` environment
  variable. If Hugging Face rate-limits you, create a free account and set an access token in
  `HF_TOKEN`.
- **No internet at all / synthetic terrain only:** `python scripts/make_synthetic_demo.py`
  generates `data/synthetic_demo/` locally (on Windows, set `PYTHONUTF8=1` first; see
  [Troubleshooting](#10-troubleshooting)). The app then runs on **synthetic** terrain, clearly
  labelled as such, without the real HiRISE layers, minerals, geology or Curiosity path.

</details>

---

## 4. Set up the frontend

### 4.1 Install the JavaScript packages

```bash
cd frontend
npm ci
```

`npm ci` installs the exact versions recorded in `package-lock.json` into
`frontend/node_modules/` (`npm install` also works). It takes one to a few minutes; Cesium is large.

> **Warning "install scripts blocked … esbuild@… (postinstall: node install.js)"?** Newer npm
> versions block package install scripts by default. On its own this warning is **harmless**:
> esbuild (Vite's bundler) gets its program from a separate platform package that npm installs
> anyway. Only if `npm run dev` later fails with an **esbuild** error, run this once inside
> `frontend/` and start again:
> ```bash
> node node_modules/esbuild/install.js
> ```

✅ **Check:** `npx vite --version` prints `vite/6.x`.

### 4.2 Point the frontend at the backend

The frontend needs to know where the backend is. Create a file **`frontend/.env.local`**
containing exactly this one line:

```
VITE_API_BASE=http://127.0.0.1:8000
```

From the `frontend` folder:

**Windows PowerShell:**
```powershell
Set-Content -Path .env.local -Value "VITE_API_BASE=http://127.0.0.1:8000" -Encoding ascii
```
**macOS / Linux / Git Bash:**
```bash
echo "VITE_API_BASE=http://127.0.0.1:8000" > .env.local
```
(or create it in any text editor).

**Why:** without it the frontend calls `http://localhost:8000`. On some systems (often Windows)
`localhost` resolves to the IPv6 address `::1`, while the backend listens on IPv4 `127.0.0.1`,
and then every API call fails silently: the globe loads but there's no terrain, no routes,
no data. Using `127.0.0.1` everywhere avoids this. `.env.local` is ignored by Git, so it stays
on your machine.

Go back to the repo root afterwards:
```bash
cd ..
```

---

## 5. Start the app

You need **two terminals**, both opened in the repo root. Leave both running while you use the app.

### Terminal 1: backend

Activate the venv (step 2.2), then:

**Windows PowerShell:**
```powershell
$env:PYTHONUTF8 = "1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
**Windows Command Prompt:** `set PYTHONUTF8=1` then the same `python -m uvicorn ...` line.

**macOS / Linux:**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

(`PYTHONUTF8=1` makes Python print Unicode safely in the Windows console; macOS and Linux don't need it.)

Wait until you see these lines (the order can vary):
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
[COSMIC TRAIL] Loaded dataset: hirise_gale (kind=real_hirise)
[COSMIC TRAIL] Loaded dataset: synthetic_demo (kind=synthetic_demo)
```

The **first** start takes a little longer: the route search is compiled to native code, and the
result is cached in `app/__pycache__/` so later starts are quicker.

> Port 8000 is the **API only**. Opening http://127.0.0.1:8000 in the browser does not show
> the app (you'll get a blank page); use port 5173 below.
> Developing the backend? Add `--reload` to restart it automatically when you edit Python files.

### Terminal 2: frontend

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Wait for:
```
  VITE v6.x  ready in ... ms
  ➜  Local:   http://127.0.0.1:5173/
```

Vite reloads the page automatically when you edit frontend files.

### Open the app

👉 **http://127.0.0.1:5173**

---

## 6. Check that everything works

In the browser at http://127.0.0.1:5173 you should see:

1. **The 3D Mars globe** at the Gale Crater study area, with the COSMIC TRAIL panel on the left.
2. Under the title, a dataset badge starting with **`DTEEC_018854_1755…`**: the **real HiRISE
   dataset**. If it says *(synthetic)* or shows a synthetic-data warning, the real data is
   missing; go back to step 3.
3. **No "Backend not reachable" error message** in the left panel. If you see one, the backend isn't running or
   `frontend/.env.local` is wrong (section 10).
4. In **Layers**: **HiRISE terrain** is on (shaded relief over the study area). Click
   **📷 HiRISE photo** to show the real HiRISE photo mosaic. If that button is greyed out,
   `ortho_mosaic.tif` or `rasterio` is missing (section 10).

**Try a route:** under *Route planner*, click **Pick** for Start (A) and click the map, then
**Pick** for Destination (B) and click again, then **Find Route**. Two routes appear
(**shortest** and **terrain-safe**) within about a second, and the **elevation profile** fills
the bottom panel. Drag the panel's **top edge**, **right edge** or **top-right corner** to resize
it; double-click an edge to reset. Click the **🤖 ARIA** button to ask questions about the route.

**API checks** (optional; open these in the browser or use `curl`):

| URL | Expect |
|-----|--------|
| http://127.0.0.1:8000/api/health | a small JSON status (HTTP 200) |
| http://127.0.0.1:8000/api/datasets | `hirise_gale` with `"terrain_available": true` |
| http://127.0.0.1:8000/api/datasets/hirise_gale/ortho | `"available": true` |
| http://127.0.0.1:8000/docs | interactive API documentation |

---

## 7. Stopping and restarting

**Stop:** press **Ctrl + C** in each terminal.

**Start again later:** no need to repeat the setup; just open two terminals in the repo root and:

```bash
# Terminal 1 — backend
#   activate the venv (step 2.2); on Windows also set PYTHONUTF8=1 (step 5)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev -- --host 127.0.0.1
```

Then open http://127.0.0.1:5173.

**A server is still running after you closed its terminal?** This happens fairly often with the
frontend on Windows: Vite's `node` process can outlive its terminal. The next start then fails
with "address already in use" / "Port 5173 is already in use" (see section 10). Find and stop
the process holding the port:

| System | Find | Stop |
|--------|------|------|
| Windows | `netstat -ano \| findstr :8000` (or `:5173`); the last column is the PID | `taskkill /PID <PID> /F` |
| macOS / Linux | `lsof -i :8000` (or `:5173`) | `kill <PID>` |

Check the PID belongs to `python`/`uvicorn` (8000) or `node` (5173) before stopping it.

---

## 8. Running the tests

With the venv active, from the repo root:

```bash
python -m pytest tests -q
```

With the data from step 3 in place, all tests should pass (189 at the time of writing). Tests that need the real
HiRISE data are **skipped** (not failed) when `data/hirise_gale/` is missing. The backend does
not need to be running.

Frontend type check (optional):
```bash
cd frontend
npx tsc -b
```
No output means no errors.

---

## 9. Updating to a newer version

From the repo root:

```bash
git pull
# backend packages (venv active)
pip install -r requirements.txt
# data — only downloads what changed
python scripts/download_data.py
# frontend packages
cd frontend
npm ci
cd ..
```

Then restart both servers (section 7).

---

## 10. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `python` not found / opens Microsoft Store (Windows) | Python not on PATH | Reinstall with "Add python.exe to PATH", or use `py -3` |
| `python3: No module named venv` (Linux) | venv package missing | `sudo apt install python3-venv` |
| PowerShell: "running scripts is disabled" (for `Activate.ps1` or `npm.ps1`) | PowerShell execution policy | Use Command Prompt, or `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`; for npm you can also type `npm.cmd` instead of `npm` |
| `ModuleNotFoundError: No module named 'fastapi'` (or another package) | venv not active, or packages not installed | Activate the venv (2.2), then `pip install -r requirements.txt` |
| `UnicodeEncodeError: 'charmap' codec can't encode character` (Windows) | Windows console encoding | Run `$env:PYTHONUTF8 = "1"` (PowerShell) or `set PYTHONUTF8=1` (cmd) first |
| `download_data.py`: connection errors / timeouts | network, proxy or firewall | Retry (it resumes); set `HTTPS_PROXY` if you use a proxy; or download by hand (step 3, *Other download options*) |
| `checksum MISMATCH` | interrupted or corrupted download | Delete that file and run `python scripts/download_data.py` again |
| `npm ci` prints `EBADENGINE` warnings / "Unsupported engine", or the app fails with Cesium errors | Node.js older than 22 | Install Node.js 22+ (`node --version`), delete `frontend/node_modules`, run `npm ci` again |
| `'vite' is not recognized` / `vite: command not found` | frontend packages not installed | `cd frontend` then `npm ci` |
| `npm run dev` fails with an **esbuild** error | npm blocked esbuild's install script (the warning alone is harmless) | In `frontend/`: `node node_modules/esbuild/install.js`, then `npm run dev` again |
| Backend: `[Errno 10048]` (Windows) / `[Errno 48]` (macOS) / `[Errno 98]` (Linux) "address already in use" | port 8000 taken (often an old backend) | Stop the old process (section 7), or use another port, e.g. `--port 8001`, **and** change `frontend/.env.local` to match, then restart the frontend |
| Frontend: `Port 5173 is already in use` | another Vite still running (the app uses a fixed port) | Stop the old `node` process (section 7) |
| "Backend not reachable at localhost:8000" error in the app | backend not running, or frontend can't reach it | Start the backend (Terminal 1); check `frontend/.env.local` contains `VITE_API_BASE=http://127.0.0.1:8000`; **restart the frontend** after creating or editing `.env.local` |
| Globe loads but no terrain, routes or data; nothing in the backend log when you click | frontend calling `localhost` over IPv6 | Create `frontend/.env.local` (step 4.2), restart the frontend, open **http://127.0.0.1:5173** (not `localhost`) |
| Dataset badge says *(synthetic)* / synthetic-data warning | `data/hirise_gale/analysis.npz` missing | Run `python scripts/download_data.py`, restart the backend, refresh the page |
| **📷 HiRISE photo** button greyed out | `ortho_mosaic.tif` missing, or `rasterio`/`pyproj` not installed | Run the download script; `pip install -r requirements.txt`; restart the backend. Its hover text says the exact reason |
| Globe is plain dark/brown, no coloured Mars surface | no internet: the basemap streams from NASA Mars Trek | Expected offline; the HiRISE terrain/photo layers still work |
| Blank page at http://127.0.0.1:8000 | port 8000 is the API, not the app | Open http://127.0.0.1:5173 |
| First route after starting the backend is slow | route search still compiling / loading | Wait for "Application startup complete"; later routes take ~1 s or less |
| Long routes take minutes | `numba` not installed | `pip install -r requirements.txt`, restart the backend |
| Route error "No route exists … disconnected" | the points are separated by slopes above the limit or missing data | Use the suggested reachable point it offers, or pick points on gentler ground |

Still stuck? Copy the **full** error from the terminal (both servers) and the browser console
(F12 → Console) when asking for help.

---

## 11. Advanced: rebuilding the data from the raw NASA files

You **don't need this** to run the app: step 3 already gives you the processed data. It is only
for regenerating `data/` from the original NASA/USGS products (e.g. to change the study window).
It needs ~10 GB of free disk and plenty of time.

1. Download everything, including the raw files (~9.7 GB):
   ```bash
   python scripts/download_data.py --include-raw
   ```
   This places the original HiRISE DTMs (`.IMG`), HiRISE orthoimages (`.JP2`), the USGS Gale DEM
   and the global MOLA DEM in `data/hirise_gale/raw/`.
2. Rebuild with the scripts in `scripts/`. Each script's docstring explains its inputs, outputs
   and options; read it before running:

   | Script | Builds |
   |--------|--------|
   | `prepare_data.py` | `data/hirise_gale/analysis.npz`, layer PNGs and `metadata.json` from the HiRISE DTMs (gaps filled from the USGS DEM). Use `--skip-download` to use the files from step 1 instead of downloading from NASA. |
   | `build_ortho_mosaic.py` | `data/hirise_gale/ortho_mosaic.tif` from the HiRISE orthoimages |
   | `build_terrain_context.py` | `data/terrain_context.npz` from the MOLA DEM |
   | `build_mineral_points.py` | `data/minerals/aqueous_minerals.json` (NASA Mars Trek) |
   | `build_mars_labels.py` | `frontend/src/data/mars_labels.json` (IAU/USGS nomenclature; manual download) |
   | `make_synthetic_demo.py` | `data/synthetic_demo/` (no input data needed) |

See **[DATA_SOURCES.md](DATA_SOURCES.md)** for where each NASA/USGS product comes from and its
credits, and **[SCIENTIFIC_LIMITATIONS.md](SCIENTIFIC_LIMITATIONS.md)** for caveats.

---

## 12. Reference: files, folders and ports

| Path | What |
|------|------|
| `app/` | backend (FastAPI): `main.py` API, `routing.py` route search, `assistant.py` ARIA, `terrain_tiles.py` / `ortho_tiles.py` map tiles |
| `frontend/` | frontend (React + Vite + Cesium); `src/components/` UI pieces |
| `frontend/.env.local` | **your** local setting `VITE_API_BASE` (not in Git) |
| `scripts/download_data.py` | downloads `data/` from Hugging Face |
| `scripts/` (others) | data building scripts (section 11) |
| `data/` | downloaded data (not in Git); `data/plans.db` (saved route plans) is created automatically |
| `tests/` | backend tests (pytest) |
| `.venv/` | your Python virtual environment (not in Git) |
| `requirements.txt` | Python packages |
| `frontend/package.json`, `package-lock.json` | JavaScript packages |

| Port | Server | Started with |
|------|--------|--------------|
| **5173** | frontend (open this in the browser) | `npm run dev -- --host 127.0.0.1` in `frontend/` |
| **8000** | backend API | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` in the repo root |

Related docs: [README.md](README.md) (overview and demo walkthrough) ·
[ARCHITECTURE.md](ARCHITECTURE.md) · [DATA_SOURCES.md](DATA_SOURCES.md) ·
[SCIENTIFIC_LIMITATIONS.md](SCIENTIFIC_LIMITATIONS.md) · [frontend/README.md](frontend/README.md)

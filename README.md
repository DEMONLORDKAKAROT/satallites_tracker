# Satellite Tracker

A real-time 3D satellite tracking web app that displays 24,000+ active satellites orbiting Earth. Built with Python (Flask) on the backend and Globe.gl on the frontend.

![Satellite Tracker](https://i.imgur.com/placeholder.png)

## Features

- **24,000+ satellites** rendered in real-time on an interactive 3D globe
- **Live position updates** — satellite positions are recalculated every 5 seconds using real orbital math
- **Click any satellite** to see its name and details
- **Filter by category** — All, Starlink, ISS, GPS
- **Search by name** — type any satellite name and press Enter

## How It Works

Satellites are tracked using **TLE (Two-Line Element)** data — two lines of numbers that describe an orbit. The backend fetches TLE data from [tle.ivanstanojevic.me](https://tle.ivanstanojevic.me) and uses the **SGP4** algorithm to calculate where each satellite is right now.

### Position Calculation Pipeline

```
TLE data (line1, line2)
        ↓
    SGP4 algorithm
        ↓
  ECI coordinates (x, y, z)  ← Earth-Centered Inertial frame
        ↓
  ECEF coordinates            ← rotate by Earth's current angle (GMST)
        ↓
  Geodetic (lat, lng, alt)    ← what the globe uses
```

### Click to Identify

When you click a satellite, the browser sends the clicked coordinates to the Flask backend, which uses a **KDTree spatial index** to find the nearest satellite in O(log n) time instead of scanning all 24,000.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Orbital math | sgp4 |
| Spatial indexing | scipy KDTree |
| Multithreading | ThreadPoolExecutor |
| TLE data source | tle.ivanstanojevic.me |
| 3D Globe | Globe.gl (Three.js) |
| Frontend | Vanilla HTML/CSS/JS |

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/satellite-tracker.git
cd satellite-tracker/tracker
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Fetch satellite TLE data** (only needed once)

Run this in Python to download TLE data and save it locally:
```python
from satalites import get_sat_data, write_to_txt
data = get_sat_data()
write_to_txt(data, "data.txt")
```

**4. Run the server**
```bash
python app.py
```

**5. Open your browser**
```
http://127.0.0.1:5000
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Serves the frontend |
| `GET /satellites?category=all` | Returns all satellite positions |
| `GET /satellites?category=starlink` | Returns filtered positions |
| `GET /nearest?lat=X&lng=Y&category=all` | Returns nearest satellite to coordinates |

## Requirements

```
flask
requests
sgp4
scipy
numpy
```

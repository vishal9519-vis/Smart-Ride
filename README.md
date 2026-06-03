![CI](https://github.com/vishal9519-vis/Smart-Ride/actions/workflows/ci.yml/badge.svg)
![CI](https://github.com/vishal9519-vis/Smart-Ride/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/vishal9519-vis/Smart-Ride)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

![License](https://img.shields.io/github/license/vishal9519-vis/Smart-Ride)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Repo Size](https://img.shields.io/github/repo-size/vishal9519-vis/Smart-Ride) 
# Smart Ride AI

Road condition analysis, vibration simulation, and adaptive suspension prediction.

Built to understand how systems like Bosch CDC and Audi Predictive Active Suspension work.

---

## What it does

- Detects potholes, cracks, bumps from dashcam video using OpenCV
- Simulates 3-axis accelerometer data with a spring-damper physics model
- Predicts comfort score using a trained Random Forest
- Simulates adaptive suspension response (stiffness and damping)
- Stores dangerous road segments in a JSON memory database
- Generates predictive alerts half a second before rough terrain
- Streamlit dashboard with Plotly charts and heatmaps

---

## Structure

```
smart_ride_ai/
|-- road_analysis/       OpenCV pothole and crack detection
|-- vibration_engine/    3-axis accelerometer simulation
|-- suspension_sim/      Adaptive damping optimizer
|-- road_memory/         Road segment memory database
|-- dashboard/           Streamlit app
|-- data/                CSV outputs + road memory JSON (generated at runtime)
|-- models/              Trained pkl files (generated at runtime)
|-- assets/             Chart images (generated at runtime) / demo video
smart_ride_ai_colab.ipynb   Full pipeline notebook
requirements.txt
```

---

## Quick start

### Option A — Google Colab (recommended)

Open `smart_ride_ai_colab.ipynb` in Google Colab and run cells top to bottom.

### Option B — Local

```bash
git clone https://github.com/vishal/smart-drive
cd smart-drive
pip install -r requirements.txt

# Run the full pipeline first to generate data
python -c "
import subprocess
# Generate data by running notebook cells manually or:
print('Run smart_ride_ai_colab.ipynb first to generate data CSVs')
"

# Then launch the dashboard
streamlit run smart_ride_ai/dashboard/app.py
```

---

## Stack

| What | How |
|------|-----|
| Road vision | OpenCV morphological analysis + Canny edges |
| Vibration | NumPy spring-damper model |
| ML | scikit-learn Random Forest |
| Dashboard | Streamlit + Plotly |
| Storage | CSV + JSON |

---

## Notes from building this

- `morphologyEx CLOSE` before `findContours` is necessary. Without it a single wet
  pothole fragments into 3–4 blobs and inflates the count.
- ISO 2631-1 normally uses frequency-weighted RMS. Unweighted is used here as a simplification.
- Random Forest worked better than linear regression because pothole impacts
  create nonlinear spikes that linear models miss.
- Stiffer suspension is not always better on rough roads. It transmits more
  high-frequency inputs. The control logic keeps stiffness moderate and raises damping instead.

---

## Possible extensions

- Real IMU (MPU-6050) instead of simulated data
- GPS integration with actual map heatmap
- LSTM for 2–3 second road roughness prediction
- Edge deployment on Raspberry Pi or Jetson Nano
- Fleet-level road hazard sharing

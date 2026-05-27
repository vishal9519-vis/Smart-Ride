"""
Alert engine — standalone module extracted from Colab CELL 16.
Import this for non-notebook use.
"""
import pandas as pd

RULES = [
    (lambda r: r['roughness'] > 80,           'ROAD_DMG_CRITICAL',   'CRITICAL'),
    (lambda r: r['roughness'] > 55,           'ROUGH_ROAD_AHEAD',    'WARNING'),
    (lambda r: r['pothole_count'] > 2,        'POTHOLE_MULTI',       'CRITICAL'),
    (lambda r: r['pothole_count'] > 0,        'POTHOLE_ZONE',        'WARNING'),
    (lambda r: r['rms'] > 2.0,                'VIBRATION_HIGH',      'HIGH'),
    (lambda r: r['pred_comfort'] < 25,        'COMFORT_CRITICAL',    'CRITICAL'),
    (lambda r: r['pred_comfort'] < 50,        'COMFORT_DROPPING',    'WARNING'),
    (lambda r: r['mode'] == 'ADAPTIVE_ROUGH', 'SUSPENSION_ADAPTING', 'INFO'),
]

LOOKAHEAD = 15


def generate_alerts(df: pd.DataFrame) -> pd.DataFrame:
    """Generate predictive alerts from a suspension_data DataFrame."""
    alerts = []
    for i in range(len(df)):
        window = df.iloc[i: i + LOOKAHEAD]
        for fn, msg, sev in RULES:
            if window.apply(fn, axis=1).any():
                alerts.append({
                    'frame': int(df.iloc[i]['frame']),
                    'ts':    float(df.iloc[i]['ts']),
                    'alert': msg,
                    'sev':   sev,
                })
                break
    return pd.DataFrame(alerts)

import numpy as np


class VibrationEngine:

    def simulate(self, roughness, frame_idx):
        rng = np.random.default_rng(frame_idx)
        r   = roughness / 100.0

        # Z — vertical, dominant for comfort
        freq_z = 1.5 + r * 4.0
        amp_z  = 0.2 + r * 2.8
        phase  = frame_idx / 30.0 * freq_z * 2 * np.pi
        z = amp_z * np.sin(phase) + float(rng.normal(0, r * 0.4 + 1e-9))

        # random pothole jolt at high roughness
        if r > 0.7 and rng.random() < 0.15:
            z += float(rng.choice([-1, 1])) * float(rng.uniform(2.0, 4.5))

        # X lateral
        x = (0.05 + r * 0.6) * np.sin(phase * 0.7 + 1.2) + float(rng.normal(0, r * 0.15 + 1e-9))

        # Y longitudinal
        y = (0.05 + r * 0.4) * np.cos(phase * 0.5 + 0.8) + float(rng.normal(0, r * 0.1 + 1e-9))

        rms = float(np.sqrt(x**2 + y**2 + z**2))
        stability = max(0, 100 - int(rms * 22))

        return {
            'ax': round(x, 4),
            'ay': round(y, 4),
            'az': round(z, 4),
            'rms': round(rms, 4),
            'stability': stability,
        }

    def iso_class(self, rms):
        if rms < 0.315: return 'not uncomfortable'
        if rms < 0.630: return 'a little uncomfortable'
        if rms < 1.000: return 'fairly uncomfortable'
        if rms < 1.600: return 'uncomfortable'
        if rms < 2.500: return 'very uncomfortable'
        return 'extremely uncomfortable'

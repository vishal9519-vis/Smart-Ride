import numpy as np


class SuspensionSim:

    K_MIN, K_MAX = 15000, 55000
    C_MIN, C_MAX = 1500,  8000
    K_BASE       = 25000

    def compute(self, roughness, rms, pothole_count, pred_comfort):
        r = roughness / 100.0
        v = min(rms / 3.0, 1.0)

        k = self.K_BASE + (r * 0.3 - v * 0.2) * (self.K_MAX - self.K_BASE)
        k = float(np.clip(k, self.K_MIN, self.K_MAX))

        c = self.C_MIN + r * (self.C_MAX - self.C_MIN)
        if pothole_count > 0:
            c = min(self.C_MAX, c * 1.3)
        c = float(c)

        ride_h   = 160 - int(r * 30)
        passive  = max(0.0, float(100 - roughness * 0.6))
        adaptive = float(min(100.0, pred_comfort + (k / self.K_BASE - 1) * 5))
        gain     = max(0.0, adaptive - passive)

        return {
            'stiffness' : round(k),
            'damping'   : round(c),
            'ride_h_mm' : ride_h,
            'passive_c' : round(passive, 1),
            'adaptive_c': round(adaptive, 1),
            'gain'      : round(gain, 1),
            'mode'      : self._mode(k, c),
        }

    def _mode(self, k, c):
        if k < 20000 and c < 3000: return 'COMFORT'
        if k > 45000 or c > 6500:  return 'SPORT'
        if c > 5000:                return 'ADAPTIVE_ROUGH'
        return                              'ADAPTIVE_NORMAL'

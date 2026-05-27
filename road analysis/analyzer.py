import cv2
import numpy as np


class RoadAnalyzer:

    POTHOLE_THRESH = 45
    BUMP_THRESH    = 110
    MIN_PH_AREA    = 400
    MIN_BUMP_WIDTH = 200

    def analyze(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # pothole — dark blob detection
        _, dark = cv2.threshold(gray, self.POTHOLE_THRESH, 255, cv2.THRESH_BINARY_INV)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, k)
        cnts, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        potholes = [c for c in cnts if cv2.contourArea(c) > self.MIN_PH_AREA]

        # bumps — bright wide regions
        _, bright = cv2.threshold(gray, self.BUMP_THRESH, 255, cv2.THRESH_BINARY)
        bcnts, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bumps = []
        for c in bcnts:
            x, y, bw, bh = cv2.boundingRect(c)
            if bw > self.MIN_BUMP_WIDTH and bw > bh * 3:
                bumps.append(c)

        # cracks via edge detector
        edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 30, 90)
        crack_px = int(np.sum(edges > 0))

        # roughness — empirical blend of std, dark ratio, pothole count
        std    = float(np.std(gray))
        dark_r = float(np.sum(dark > 0)) / (h * w)
        roughness = min(100, int(std * 0.8 + dark_r * 200 + len(potholes) * 15))

        return {
            'potholes'     : potholes,
            'bumps'        : bumps,
            'edges'        : edges,
            'pothole_count': len(potholes),
            'bump_count'   : len(bumps),
            'crack_px'     : crack_px,
            'roughness'    : roughness,
            'smoothness'   : max(0, 100 - roughness),
            'std'          : round(std, 2),
            'dark_ratio'   : round(dark_r, 4),
        }

    def road_class(self, r):
        s, p = r['roughness'], r['pothole_count']
        if p >= 3 or s >= 80: return 'CRITICAL', '#ff2222'
        if p >= 1 or s >= 55: return 'WARNING',  '#ff9900'
        if s >= 30:            return 'CAUTION',  '#ffdd00'
        return                        'GOOD',     '#00ff88'

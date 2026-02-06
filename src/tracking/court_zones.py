import numpy as np

COURT_WIDTH = 1920
COURT_HEIGHT = 1080

ZONES = {
    "Paint": ((COURT_WIDTH*0.4, COURT_WIDTH*0.6), (COURT_HEIGHT*0.7, COURT_HEIGHT)),  # bottom middle rectangle
    "Left Wing": ((0, COURT_WIDTH*0.4), (COURT_HEIGHT*0.5, COURT_HEIGHT*0.7)),
    "Right Wing": ((COURT_WIDTH*0.6, COURT_WIDTH), (COURT_HEIGHT*0.5, COURT_HEIGHT*0.7)),
    "Top Key": ((COURT_WIDTH*0.4, COURT_WIDTH*0.6), (COURT_HEIGHT*0.3, COURT_HEIGHT*0.5)),
    "Left Corner 3": ((0, COURT_WIDTH*0.2), (COURT_HEIGHT*0.7, COURT_HEIGHT)),
    "Right Corner 3": ((COURT_WIDTH*0.8, COURT_WIDTH), (COURT_HEIGHT*0.7, COURT_HEIGHT))
}


def get_player_center(x1, y1, x2, y2):
    """Computer cetner coordinates of a bounding box"""
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return cx, cy

def assign_zone(cx, cy):
    """Return the zone name based on center coordinates"""
    for zone_name, ((x_min, x_max), (y_min, y_max)) in ZONES.items():
        if x_min <= cx <= x_max and y_min <= cy <= y_max:
            return zone_name
        
    return "Other"
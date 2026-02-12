from sklearn.cluster import KMeans
import numpy as np

color_samples = []
team_kmeans = None

def get_torso_crop(frame, x1, y1, x2, y2):
    h = y2 - y1
    w = x2 - x1

    if h <= 0 or w <= 0:
        return None
    
    # Focus in on the jersey area
    torso_y1 = int(y1 + 0.25 * h)
    torso_y2 = int(y1 + 0.75 * h)

    # Focus on middle 60% horizontally
    torso_x1 = int(x1 + 0.2 * w)
    torso_x2 = int(x1 + 0.8 * w)
    
    crop = frame[torso_y1:torso_y2, torso_x1:torso_x2]
    if crop.size == 0:
        return None
    
    return crop

def get_dominant_color(image, k=2):
    if image is None or image.size == 0:
        return None
    
    pixels = image.reshape(-1, 3).astype(np.float32)

    brightness = np.mean(pixels, axis=1)
    mask = (brightness > 40) & (brightness < 220)
    pixels = pixels[mask]

    if len(pixels) < 50:
        return None

    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(pixels)

    centers = kmeans.cluster_centers_
    labels = kmeans.labels_

    counts = np.bincount(labels)
    dominant = centers[np.argmax(counts)]

    if np.isnan(dominant).any():
        return None

    return dominant.astype(float)

def get_team_label(color):

    if color is None:
        return None
    
    global team_kmeans
    color = color.reshape(1, -1)

    if team_kmeans is None:
        return "unknown"
    
    team_id = team_kmeans.predict(color)[0]
    return f"TEAM_{team_id}"

def update_team_clusters(color, frame_id):
    global team_kmeans

    if color is None:
        return
    
    if frame_id < 50:
        color_samples.append(color)
        return
    
    if team_kmeans is None and len(color_samples) > 20:
        team_kmeans = KMeans(n_clusters=2, n_init=10)
        team_kmeans.fit(color_samples)
        print("Team color clusters learned!")

    
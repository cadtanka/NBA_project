from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import csv
import numpy as np
from sklearn.cluster import KMeans
import track_teams 
import court_zones

csv_file = open("tracking_data.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["frame", "track_id", "team", "x1", "y1", "x2", "y2", "cx", "cy", "zone"])

# Import our model
model = YOLO("yolo26n.pt")

# Initialize DeepSORT tracker
tracker = DeepSort(
    max_age=30,
    n_init=3,
    max_cosine_distance=0.3
)

VIDEO_PATH = "/Users/cadetanaka/Desktop/Other projects/NBA_game_analyzer/tests/nba_clip.mov"

cap = cv2.VideoCapture(VIDEO_PATH)

frame_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.25)[0]

    detections = []

    if results.boxes is not None:
        for box in results.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Only keep people and the basketball
            if cls in [0, 32]:
                w = x2 - x1
                h = y2 - y1
                detections.append(([x1, y1, w, h], conf, cls))

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = track.to_ltrb()

        torso = track_teams.get_torso_crop(frame, l, t, w, h)
        color = track_teams.get_dominant_color(torso)
        cx, cy = court_zones.get_player_center(l, t, w, h)
        zone = court_zones.assign_zone(cx, cy)

        track_teams.update_team_clusters(color, frame_id)

        team = track_teams.get_team_label(color)

        cv2.rectangle(frame, (int(l), int(t)), (int(w), int(h)), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (int(l), int(t)-10),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
        
        writer.writerow([frame_id, track_id, team, l, t, w, h, cx, cy, zone])

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame_id += 1

cap.release()
cv2.destroyAllWindows()
csv_file.close()
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np
from sklearn.cluster import KMeans
from src.tracking import track_teams
from src.tracking import court_zones
from src.data.schema import create_tables, insert_game, insert_frame, get_or_create_player, insert_player_position
from datetime import date

# Import our model
model = YOLO("yolo26n.pt")
FPS = 30

# Initialize DeepSORT tracker
tracker = DeepSort(
    max_age=30,
    n_init=3,
    max_cosine_distance=0.3
)

VIDEO_PATH = "/Users/cadetanaka/Desktop/Other projects/NBA_game_analyzer/tests/nba_clip.mov"

create_tables()

game_id = insert_game(
    game_date=date.today(),
    home_team="TEAM_A",
    away_team="TEAM_B",
    video_path=VIDEO_PATH
)

print("Tracking game_id:", game_id)

cap = cv2.VideoCapture(VIDEO_PATH)

frame_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id_db = insert_frame(
        game_id=game_id,
        frame_number=frame_id,
        game_clock=frame_id/FPS 
    )

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

        player_id = get_or_create_player(
            assigned_number=track_id,
            team=team,
            jersey_color=str(color) if color is not None else "unknown"
        )

        insert_player_position(
            frame_id=frame_id_db,
            player_id=player_id,
            x1=l,
            y1=t,
            x2=w,
            y2=h,
            cx=cx,
            cy=cy,
            zone=zone,
            confidence=1.0
        )

        cv2.rectangle(frame, (int(l), int(t)), (int(w), int(h)), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {player_id}", (int(l), int(t)-10),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
        

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame_id += 1

cap.release()
cv2.destroyAllWindows()
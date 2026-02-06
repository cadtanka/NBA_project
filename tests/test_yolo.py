# Load our pretrained model for testing
from ultralytics import YOLO

model = YOLO("yolo26n.pt")
"""
results = model.predict(
    source="https://ultralytics.com/images/bus.jpg",
    save=True,
    conf=0.25
)
"""

results = model.predict(
    source="nba_clip.mov",
    conf=0.25,
    stream=False
)

for frame_i, result in enumerate(results):
    boxes=result.boxes

    if boxes is None:
        continue

    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()

        print({
            "frame": frame_i,
            "class": cls,
            "confidence":conf,
            "bbox": xyxy
        })



print("Video Done!")
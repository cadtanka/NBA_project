from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from dataclasses import dataclass

@dataclass
class ProcessingConfig:
    model: YOLO
    tracker: DeepSort
    fps: int = 30

def create_default_config() -> ProcessingConfig:
    model = YOLO("yolo26n.pt")

    tracker = DeepSort(
        max_age = 30,
        n_init = 3,
        max_cosine_distance=0.3
    )

    return ProcessingConfig(
        model=model,
        tracker=tracker,
        fps=30
    )
"""
signature_detector.py

Finds and crop sign region of a full doc image suing YOLOv5 model.
"""

import cv2
import numpy as np
import torch

# Path to pre-trained weights file
WEIGHTS_PATH = "detection/weights/yolov5n.pt"

#only trust detections above this
CONFIDENCE_THRESHOLD = 0.35

#Load model once, reuse for next requests
model = None


def load_model():
    """Load the YOLOv5 model on first use """

    global model
    if model is None:
        model = torch.hub.load(
            "ultralytics/yolov5", 
            "custom", 
            path=WEIGHTS_PATH, 
            source="github"
        )
        model.conf = CONFIDENCE_THRESHOLD

    return model

def load_image(img_source):
    """Load an image in color, from a file path or raw bytes."""

    #if input image is in form of bytes
    if isinstance(img_source, (bytes, bytearray)):
        arr = np.frombuffer(img_source, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    #else if in form of a file path
    else:
        image = cv2.imread(img_source)

    return image


def detect_signature_region(img_source):
    """
    Detect the signature in a document image and return just that cropped region.
    """

    
    detector = load_model()

    image = load_image(img_source)

    if image is None:
        return None

    #YOLOv5 expects RGB images, but OpenCV loads them as BGR
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    #run detection
    results = detector(image_rgb)
    detections = results.pandas().xyxy[0]

    #no signature found
    if len(detections) == 0:
        return None

    #if more than one signature detected, keep the most confident one
    best = detections.sort_values("confidence", ascending=False).iloc[0]
    x1, y1, x2, y2 = int(best.xmin), int(best.ymin), int(best.xmax), int(best.ymax)

    #crop out just the signature region
    cropped_sign = image[y1:y2, x1:x2]
    return cropped_sign
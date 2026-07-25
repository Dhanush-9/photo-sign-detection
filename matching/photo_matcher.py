"""
photo_matcher.py

Photo verification using OpenCV Haar cascade face detection + template matching.
"""

import os
import cv2
import numpy as np

# resize every sign before we compare
MATCH_SIZE = (150, 150)

#if match is 35% we accept
MATCH_THRESHOLD = 0.35

#built-in OpenCV cascade
_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def load_grayscale_image(img_source):
    """Load an image as a grayscale numpy array."""

    #if input image is in form of bytes
    if isinstance(img_source, (bytes, bytearray)):
        arr = np.frombuffer(img_source, dtype=np.uint8)
        grayscale_img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)

    #else if in form of a file path
    else:
        grayscale_img = cv2.imread(img_source, cv2.IMREAD_GRAYSCALE)

    return grayscale_img


def detect_face(grayscale_img):
    """
    Detect the largest face in a grayscale image using OpenCV's Haar cascade.
    """
    faces = _face_cascade.detectMultiScale(
        grayscale_img, scaleFactor=1.1, minNeighbors=5
    )

    if len(faces) == 0:
        return None

    #if multiple faces detected, use the largest (closest to camera)
    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    return grayscale_img[y:y + h, x:x + w]


def preprocess_photo(img_source):
    """Preprocess a photo for comparison:"""

    #load image in grayscale
    grayscale_img = load_grayscale_image(img_source)

    if grayscale_img is None:
        return None

    #detect and crop the face
    face_img = detect_face(grayscale_img)

    if face_img is None:
        return None

    #resize all faces to same dimensions
    resized_face = cv2.resize(face_img, MATCH_SIZE, interpolation=cv2.INTER_AREA)

    #equalize lighting so brightness diff matter less
    processed_face = cv2.equalizeHist(resized_face)

    return processed_face


def compute_similarity(photo1, photo2):
    """Compute a similarity score between two preprocessed face images."""

    similarity_matrix = cv2.matchTemplate(photo1, photo2, cv2.TM_CCOEFF_NORMED)
    similarity_score = float(similarity_matrix[0][0])

    return similarity_score


def find_best_photo_match(uploaded_photo, registered_users, base_dir):
    """
    Compare the query photo against every registered user's photo
    and return whichever one scores highest.
    """

    #preprocess uploaded photo
    uploaded_face = preprocess_photo(uploaded_photo)

    if uploaded_face is None:
        raise ValueError("Could not detect a face in the uploaded photo. Please try a clearer photo.")

    best_user = None
    best_score = -1.0

    #compare uploaded face with every registered face
    for user in registered_users:

        photo_path = os.path.join(base_dir, user["photo_path"])
        registered_face = preprocess_photo(photo_path)

        #skip if stored photo cannot be read or has no detectable face
        if registered_face is None:
            continue

        similarity_score = compute_similarity(uploaded_face, registered_face)

        #update best match
        if similarity_score > best_score:
            best_score = similarity_score
            best_user = user

    #check if similarity is above threshold
    if best_user is not None and best_score >= MATCH_THRESHOLD:
        return best_user, best_score

    return None, best_score
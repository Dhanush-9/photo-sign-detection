"""
signature_matcher.py

Signature verification using OpenCV template matching.
"""

import os
import cv2
import numpy as np

# resize every sign before we compare
MATCH_SIZE = (300, 150)

#gaussian blur amount for better overlapping
BLUR_KSIZE = 31

#if match is 35% we accept
MATCH_THRESHOLD = 0.35


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


def preprocess_signature(img_source):
    """Preprocess a signature image for comparison:"""

    #load image in grayscale
    grayscale_img = load_grayscale_image(img_source)

    if grayscale_img is None:
        return None

    #resize all signs to same dimensions
    resized_img = cv2.resize(grayscale_img, MATCH_SIZE, interpolation=cv2.INTER_AREA)

    #convert image to black & white
    _, binary_img = cv2.threshold(
        resized_img,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    #smooth the sign to reduce small variations in handwriting
    processed_img = cv2.GaussianBlur(binary_img, (BLUR_KSIZE, BLUR_KSIZE), 0)
    return processed_img


def compute_similarity(sign1, sign2):
    """Compute a similarity score between two preprocessed images """

    similarity_matrix = cv2.matchTemplate(sign1, sign2, cv2.TM_CCOEFF_NORMED)
    similarity_score = float(similarity_matrix[0][0])

    return similarity_score


def find_best_match(uploaded_sign, registered_users, base_dir):
    """
    Compare the query signature against every registered user's signature
    and return whichever one scores highest.
    """

    #preprocess uploaded signature
    uploaded_sign = preprocess_signature(uploaded_sign)

    if uploaded_sign is None:
        raise ValueError("Could not read the uploaded signature image.")

    best_user = None
    best_score = -1.0

    #compare uploaded sign with every registered sign
    for user in registered_users:


        sign_path = os.path.join(base_dir, user["sign_path"])
        registered_sign = preprocess_signature(sign_path)

        #skip if stored sign cannot be read
        if registered_sign is None:
            continue

        similarity_score = compute_similarity(uploaded_sign, registered_sign)

        #update best_match
        if similarity_score > best_score:
            best_score = similarity_score
            best_user = user

    #check if similarity is above threshold
    if best_user is not None and best_score >= MATCH_THRESHOLD:
        return best_user, best_score

    return None, best_score

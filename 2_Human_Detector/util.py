import base64
import datetime
import os

import cv2
import numpy as np


# frame轉為base64
def frame_to_base64(frame):
    """
    Convert a frame (image) to a Base64-encoded string.

    :param frame: The image frame from OpenCV.
    :return: Base64-encoded string of the image.
    """
    # Encode the frame as a JPEG image
    _, buffer = cv2.imencode(".jpg", frame)
    # Convert the buffer to a Base64 string
    base64_image = base64.b64encode(buffer).decode("utf-8")
    return base64_image


# frame轉為 jpg
def frame_to_jpg(frame, folder_path, filename):
    """
    Save a frame (image) to specified folder as a JPEG file.

    :param frame: The image frame from OpenCV.
    :param folder_path: The folder where the image will be saved.
    :param filename: The name of the file (with .jpg extension).
    :return: The full path of the saved image.
    """
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Construct the full file path
    file_path = os.path.join(folder_path, filename)

    # Save the frame as a JPEG file
    success = cv2.imwrite(file_path, frame)
    if not success:
        raise IOError(f"Failed to save image to {file_path}")

    return file_path


# 產生時間字串
def get_datetime_string(format="%Y%m%d_%H%M%S_%f"):
    """
    Get the current get_datetime_string in a human-readable format.

    :return: Current datetime as a string.
    """
    return datetime.datetime.now().strftime(format)



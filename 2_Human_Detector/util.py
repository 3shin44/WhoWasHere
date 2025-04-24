import base64
import datetime
import hashlib
import os
import random

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


# 產生時間字串
def get_datetime_string(format="%Y%m%d_%H%M%S_%f"):
    """
    Get the current get_datetime_string in a human-readable format.

    :return: Current datetime as a string.
    """
    return datetime.datetime.now().strftime(format)

import os

import cv2
import numpy as np
from ultralytics import YOLO


class PersonDetectorYOLO8:
    def __init__(
        self, video_source, threshold=0.5, callback=None, model_path="./yolo/yolov8n.pt"
    ):
        """
        Initialize the PersonDetectorYOLO8 object.

        :param video_source: Path to the video file or camera index.
        :param threshold: Confidence threshold for detecting persons.
        :param callback: Function to call when a person is detected.
        :param model_path: Path to the YOLOv8 model file.
        """
        self.video_source = video_source
        self.threshold = threshold
        self.callback = callback

        # Load YOLOv8 model
        self.model = YOLO(model_path)

    def process_video(self, frame_interval=30, debug_mode=False):
        """
        Process the video and detect persons in real-time based on frame interval.

        :param frame_interval: Number of frames to skip before processing the next frame.
        """
        cap = cv2.VideoCapture(self.video_source)

        # Check if video opened successfully
        if not cap.isOpened():
            raise ValueError(f"Cannot open video source: {self.video_source}")

        frame_count = 0  # Initialize frame counter

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Increment frame counter
            frame_count += 1

            # Skip frames until the interval is reached
            if frame_count % frame_interval != 0:
                continue

            # Perform detection using YOLOv8
            results = self.model(frame)

            # Analyze detections
            for result in results:
                for box in result.boxes:
                    if box.conf < self.threshold:
                        continue

                    # Extract bounding box and label
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = result.names[int(box.cls)]
                    confidence = float(box.conf)

                    if label == "person":
                        # Draw bounding box
                        color = (0, 255, 0)  # Green for person
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(
                            frame,
                            f"{label} {confidence:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            color,
                            2,
                        )

                        # Call the callback function if provided
                        if self.callback:
                            self.callback(label, confidence, frame)

            # DEV MODE
            if debug_mode:
                # Display the frame with annotations
                cv2.imshow("Video", frame)

                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()


# Test mode
if __name__ == "__main__":

    def detection_callback(label, confidence, frame):
        print(f"Detected {label} with confidence {confidence:.2f} at {frame}")

    video_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "./test/sample/sample1.mp4"
    )

    # detector_v4 = PersonDetector(video_source=video_path, threshold=0.5, callback=detection_callback)
    # detector_v4.process_video()

    detector_v8 = PersonDetectorYOLO8(
        video_source=video_path, threshold=0.5, callback=detection_callback
    )
    detector_v8.process_video()

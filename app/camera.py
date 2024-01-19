import math

import cv2
from ultralytics import YOLO

from app import settings


class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(settings.camera)
        self.model = YOLO(settings.path_model)

    def gen_frames(self):
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                person_count = 0
                laptop_count = 0
                results = self.model(frame, stream=True)
                for r in results:
                    boxes = r.boxes

                    for box in boxes:
                        # bounding box
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

                        # put box in cam
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                        # confidence
                        confidence = math.ceil((box.conf[0] * 100)) / 100
                        # print("Confidence --->", confidence)

                        # class name
                        cls = int(box.cls[0])
                        if cls == 0:
                            person_count += 1
                        elif cls == 1:
                            laptop_count += 1
                        # print("Class name -->", settings.class_names[cls])

                        # object details
                        org = [x1, y1]
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        fontScale = 1
                        color = (255, 0, 0)
                        thickness = 2

                        print(f'PERSONS: {person_count}, LAPTOPS: {laptop_count}')

                        cv2.putText(frame, settings.class_names[cls], org, font, fontScale, color, thickness)

                ret, buffer = cv2.imencode('.jpg', frame)

                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

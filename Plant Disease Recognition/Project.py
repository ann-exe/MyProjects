from ultralytics import YOLO
import cv2
import cvzone
import math

cap = cv2.VideoCapture("Dane_testujace/r_sucha.mp4")

model = YOLO("model.pt")

class_names = ["lisc_przelany", "lisc_suchy", "lisc_variegata", "roslina_przelana", "roslina_sucha",
               "roslina_variegata", "roslina_zdrowa"]

while True:
    success, img = cap.read()
    results = model(img, stream=True)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            cvzone.cornerRect(img, (x1, y1, w, h))
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            cvzone.putTextRect(img, f"{class_names[cls]} {conf}", (max(0, x1), max(35, y1)),
                               scale=1, thickness=1)
    cv2.imshow("Image", img)
    cv2.waitKey(1)

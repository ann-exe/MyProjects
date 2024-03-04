import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO
import cv2


class PlantDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Wykrywanie chorob roslin")
        self.root.geometry("400x200")

        self.file_path = None
        self.model = YOLO("model.pt")
        self.class_names = ["lisc_przelany", "lisc_suchy", "lisc_variegata", "roslina_przelana", "roslina_sucha",
                            "roslina_variegata", "roslina_zdrowa"]
        self.illnesses = {"lisc_przelany": "przelana", "lisc_suchy": "sucha", "lisc_variegata": "z wariegacja",
                        "roslina_przelana": "przelana", "roslina_sucha": "sucha", "roslina_variegata": "z wariegacja",
                        "roslina_zdrowa": "zdrowa"}

        self.label = tk.Label(root, text="Wybierz plik wideo:")
        self.label.pack()

        self.choose_file_button = tk.Button(root, text="Wybierz plik", command=self.choose_file)
        self.choose_file_button.pack()

        self.analyze_button = tk.Button(root, text="Zbadaj rosline", command=self.analyze_video)
        self.analyze_button.pack()

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])

    def analyze_video(self):
        if self.file_path:
            cap = cv2.VideoCapture(self.file_path)

            best_class = None
            best_confidence = 0

            while True:
                success, img = cap.read()

                if not success:
                    break

                results = self.model(img, stream=True)

                for result in results:
                    for box in result.boxes:
                        conf = box.conf[0]
                        if conf > best_confidence:
                            best_confidence = conf
                            best_class = self.class_names[int(box.cls[0])]

            cap.release()
            cv2.destroyAllWindows()

            if best_class is not None:
                result_text = f"Roslina jest {self.illnesses[best_class]}. Pewność: {best_confidence:.2f}"
                self.result_label.config(text=result_text)
            else:
                self.result_label.config(text="Brak danych do analizy.")


root = tk.Tk()
app = PlantDetector(root)
root.mainloop()

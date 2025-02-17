import tkinter as tk
from tkinter import messagebox
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import cv2
import threading

class QRCodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Camera variables
        self.cap = None
        self.running = False

        # UI elements
        self.video_label = tk.Label(self.root, bg="#000")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.result_label = tk.Label(self.root, text="Detected Data: None", font=("Arial", 14), bg="#f0f0f0")
        self.result_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Camera", command=self.start_camera, bg="#4caf50", fg="white", font=("Arial", 12))
        self.start_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Camera", command=self.stop_camera, bg="#f44336", fg="white", font=("Arial", 12))
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_app, bg="#2196f3", fg="white", font=("Arial", 12))
        self.exit_button.pack(side=tk.RIGHT, padx=20, pady=10)

    def start_camera(self):
        if self.running:
            messagebox.showwarning("Warning", "Camera is already running!")
            return

        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update_frame()

    def stop_camera(self):
        if not self.running:
            messagebox.showwarning("Warning", "Camera is not running!")
            return

        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image="")

    def update_frame(self):
        if not self.running or not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            # Process frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = decode(gray)

            for obj in decoded_objects:
                data = obj.data.decode("utf-8")
                self.result_label.config(text=f"Detected Data: {data}")

                # Draw rectangle
                points = obj.polygon
                if len(points) == 4:
                    for i in range(4):
                        cv2.line(frame, tuple(points[i]), tuple(points[(i + 1) % 4]), (0, 255, 0), 3)

            # Convert frame to ImageTk
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_frame)

    def exit_app(self):
        self.stop_camera()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeScannerApp(root)
    root.mainloop()

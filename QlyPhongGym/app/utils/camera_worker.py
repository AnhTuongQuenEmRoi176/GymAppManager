from PyQt6.QtCore import QThread, pyqtSignal
import cv2
from app.utils.qr_utils import decode_qr_from_frame
import time


class CameraWorker(QThread):
    frame_ready = pyqtSignal(object, list)  # QImage, decoded list

    def __init__(self, camera_index=0, fps=15):
        super().__init__()
        self.camera_index = camera_index
        self.fps = fps
        self._running = False

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return
        self._running = True
        delay = 1.0 / max(1, self.fps)
        while self._running:
            ret, frame = cap.read()
            if not ret:
                break
            decoded = decode_qr_from_frame(frame)
            # Convert frame BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            # Use QImage in caller, pass raw frame
            self.frame_ready.emit(rgb, decoded)
            time.sleep(delay)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()

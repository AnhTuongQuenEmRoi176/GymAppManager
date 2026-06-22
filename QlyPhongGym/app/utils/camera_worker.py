from PyQt6.QtCore import QThread, pyqtSignal
import time


class CameraWorker(QThread):
    frame_ready = pyqtSignal(object, list)

    def __init__(self, camera_index=0, fps=10, decode_every=3):
        super().__init__()
        self.camera_index = camera_index
        self.fps = fps
        self.decode_every = max(1, decode_every)
        self._running = False

    def run(self):
        import cv2
        from app.utils.qr_utils import decode_qr_from_frame

        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return
        self._running = True
        delay = 1.0 / max(1, self.fps)
        frame_index = 0
        last_decoded = []
        while self._running:
            ret, frame = cap.read()
            if not ret:
                break
            frame_index += 1
            if frame_index % self.decode_every == 0:
                last_decoded = decode_qr_from_frame(frame)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_ready.emit(rgb, last_decoded)
            time.sleep(delay)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()

import cv2
from pyzbar import pyzbar


def decode_qr_from_frame(frame):
    # frame: numpy array BGR
    decoded = pyzbar.decode(frame)
    results = []
    for d in decoded:
        results.append({
            'data': d.data.decode('utf-8'),
            'type': d.type,
            'rect': d.rect
        })
    return results

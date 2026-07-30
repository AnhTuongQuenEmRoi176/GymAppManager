"""Tiện ích đọc QR cho camera Windows App.

Bản này giữ pyzbar làm bộ đọc chính và bổ sung:
- nhiều biến thể ảnh để đọc QR dài/dày từ màn hình điện thoại;
- OpenCV QRCodeDetector làm phương án dự phòng;
- đọc nhiều QR cùng khung hình;
- loại bỏ kết quả trùng nhau.
"""
from __future__ import annotations

from typing import Any

import cv2
from pyzbar import pyzbar


def _append_unique(results: list[dict[str, Any]], seen: set[str], data: str, rect=None) -> None:
    value = (data or "").strip()
    if not value or value in seen:
        return
    seen.add(value)
    results.append({"data": value, "type": "QRCODE", "rect": rect})


def _decode_with_pyzbar(image, results: list[dict[str, Any]], seen: set[str]) -> None:
    try:
        decoded_items = pyzbar.decode(image)
    except Exception:
        return

    for item in decoded_items:
        try:
            value = item.data.decode("utf-8")
        except UnicodeDecodeError:
            value = item.data.decode("utf-8", errors="replace")
        _append_unique(results, seen, value, item.rect)


def _decode_with_opencv(frame, results: list[dict[str, Any]], seen: set[str]) -> None:
    detector = cv2.QRCodeDetector()

    # OpenCV mới hỗ trợ nhận diện nhiều mã trong cùng một khung hình.
    try:
        ok, decoded_info, points, _ = detector.detectAndDecodeMulti(frame)
        if ok and decoded_info:
            for value in decoded_info:
                _append_unique(results, seen, value)
    except (AttributeError, cv2.error, ValueError):
        pass

    # Fallback cho OpenCV/driver chỉ nhận diện được một mã.
    try:
        value, points, _ = detector.detectAndDecode(frame)
        _append_unique(results, seen, value)
    except (cv2.error, ValueError):
        pass


def decode_qr_from_frame(frame):
    """Trả về danh sách QR đọc được từ frame BGR của OpenCV."""
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    # 1) Ảnh gốc: nhanh nhất và thường chính xác nhất.
    _decode_with_pyzbar(frame, results, seen)

    # 2) QR JWT từ Flutter dài và nhiều module; grayscale + phóng lớn giúp camera
    # đọc rõ hơn khi mã được hiển thị trên màn hình điện thoại.
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _decode_with_pyzbar(gray, results, seen)

        if len(results) < 2:
            enlarged = cv2.resize(
                gray,
                None,
                fx=1.6,
                fy=1.6,
                interpolation=cv2.INTER_CUBIC,
            )
            _decode_with_pyzbar(enlarged, results, seen)

        if len(results) < 2:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            _decode_with_pyzbar(enhanced, results, seen)
    except cv2.error:
        pass

    # 3) OpenCV fallback, đặc biệt hữu ích với QR hiển thị trên LCD/OLED.
    _decode_with_opencv(frame, results, seen)
    return results

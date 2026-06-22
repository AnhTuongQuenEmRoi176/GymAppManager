from pathlib import Path
import os
import uuid
from datetime import datetime

from app.db import get_session
from app.models import Member, QRDemo

try:
    import qrcode
except Exception as e:
    print('Thư viện qrcode chưa cài. Chạy: pip install qrcode[pil]')
    raise

root = Path(__file__).resolve().parent
resources_dir = root.parent / 'app' / 'resources' / 'qr_demo'
resources_dir.mkdir(parents=True, exist_ok=True)

session = get_session()
try:
    m = session.query(Member).join(Member.user).first()
    if not m:
        print('Không tìm thấy hội viên nào trong DB.')
    else:
        payload = f"member:{m.id}"
        filename = f"member_{m.id}_{uuid.uuid4().hex}.png"
        filepath = resources_dir / filename
        img = qrcode.make(payload)
        img.save(str(filepath))

        q = QRDemo(code=payload, entity_type='member', entity_id=m.id, created_at=datetime.utcnow())
        session.add(q)
        session.commit()
        print('Tạo QR thành công:')
        print('payload=', payload)
        print('file=', filepath)
        print('db id=', q.id)
finally:
    session.close()

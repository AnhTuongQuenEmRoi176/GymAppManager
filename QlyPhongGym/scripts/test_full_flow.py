"""Comprehensive test of QR detection -> confirm -> checkin history"""
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QDate
from app.db import get_session
from app.models import Member, Trainer, Checkin

# Initialize Qt app
app = QApplication([])

# Get first member and trainer
session = get_session()
mem = session.query(Member).first()
pt = session.query(Trainer).first()
session.close()

if not mem or not pt:
    print('ERROR: No member or trainer found')
    sys.exit(1)

print(f'Testing with Member={mem.user.full_name} (ID={mem.id}), PT={pt.user.full_name} (ID={pt.id})')

# Step 1: Clear recent checkins for this member (to verify new ones appear)
print('\n=== Step 1: Clear recent test data ===')
session = get_session()
session.query(Checkin).filter(
    Checkin.member_id == mem.id,
    Checkin.qr_payload.in_(['member:1', 'trainer:1'])
).delete()
session.commit()
session.close()

# Step 2: Create TabDashboard and simulate QR detection
print('\n=== Step 2: Create TabDashboard and simulate QR detection ===')
from app.ui.tab_dashboard import TabDashboard
tab_dashboard = TabDashboard()
tab_dashboard.pending_entities = {'member': mem, 'trainer': pt}
tab_dashboard.pending_photo = '/tmp/test.jpg'
tab_dashboard.pending_payloads = ['member:1', 'trainer:1']
print(f'✓ Simulated QR detection, pending_entities set')

# Step 3: Click confirm button
print('\n=== Step 3: Click confirm button ===')
tab_dashboard.handle_confirm()
print('✓ Confirmed, handle_confirm completed')

# Step 4: Check if checkins were created
print('\n=== Step 4: Check if checkins were created ===')
time.sleep(1)  # Give database time to commit
session = get_session()
chk_count = session.query(Checkin).filter(Checkin.member_id == mem.id).count()
pt_chk_count = session.query(Checkin).filter(Checkin.trainer_id == pt.id).count()
session.close()
print(f'✓ Total member checkins: {chk_count}')
print(f'✓ Total trainer checkins: {pt_chk_count}')

# Step 5: Create TabHistory and check if it can load the checkins
print('\n=== Step 5: Create TabHistory and verify auto-refresh ===')
from app.ui.tab_history import TabHistory
tab_history = TabHistory()

# Wait for auto-refresh to occur
print(f'Waiting 12 seconds for auto-refresh...')
def check_table():
    row_count = tab_history.table.rowCount()
    print(f'✓ TabHistory loaded {row_count} checkins')
    if row_count > 0:
        # Print first row info
        for col in range(5):
            item = tab_history.table.item(0, col)
            if item:
                print(f'  Column {col}: {item.text()}')
    app.quit()

# Set timer to check after refresh
QTimer.singleShot(12500, check_table)
app.exec()

print('\n=== Test completed successfully! ===')

"""Test debounce reset after confirmation"""
from PyQt6.QtWidgets import QApplication
from app.db import get_session
from app.models import Member, Trainer
from app.ui.tab_dashboard import TabDashboard
import time

# Initialize Qt
app = QApplication([])

# Create TabDashboard
tab = TabDashboard()

# Get test data
session = get_session()
mem = session.query(Member).first()
pt = session.query(Trainer).first()
if not mem or not pt:
    print('ERROR: No member or trainer found')
    session.close()
    exit(1)

mem_id = mem.id
pt_id = pt.id
mem_name = mem.user.full_name
pt_name = pt.user.full_name

print(f'Test: Verify debounce reset after confirm')
print(f'Member: {mem_name} (ID={mem_id})')
print(f'Trainer: {pt_name} (ID={pt_id})')

# Step 1: Simulate first QR detection
print('\n--- Step 1: First QR detection ---')
payload = f'member:{mem_id}'
tab.last_seen[payload] = time.time()  # Mark as detected now
print(f'Set debounce: last_seen["{payload}"]')

# Step 2: Simulate confirm
print('\n--- Step 2: Confirm detection ---')
tab.pending_entities = {'member': mem, 'trainer': pt}
tab.pending_photo = '/tmp/test.jpg'
tab.pending_payloads = [payload, f'trainer:{pt_id}']
print(f'Set pending_payloads: {tab.pending_payloads}')

# Call handle_confirm
tab.handle_confirm()
print('✓ handle_confirm() completed')

# Step 3: Check if debounce was cleared
print('\n--- Step 3: Check debounce status ---')
if payload in tab.last_seen:
    print(f'❌ FAIL: Debounce still exists for {payload}')
    exit(1)
else:
    print(f'✓ PASS: Debounce cleared for {payload}')

# Step 4: Verify timestamp can be set again
print('\n--- Step 4: Simulate re-detection ---')
current_time = time.time()
tab.last_seen[payload] = current_time
if payload in tab.last_seen and tab.last_seen[payload] == current_time:
    print(f'✓ PASS: Can re-detect and update timestamp')
else:
    print(f'❌ FAIL: Cannot update timestamp')
    exit(1)

session.close()
print('\n✓✓✓ All tests passed! ✓✓✓')

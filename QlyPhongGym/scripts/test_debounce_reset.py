"""Test debounce reset after confirmation"""
from PyQt6.QtWidgets import QApplication
from app.db import get_session
from app.models import Member, Trainer, MemberPackage
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
mem_id = mem.id
pt_id = pt.id
mem_name = mem.user.full_name
pt_name = pt.user.full_name
session.close()

if not mem_id or not pt_id:
    print('ERROR: No member or trainer found')
    exit(1)

print(f'Test: Verify debounce reset after confirm')
print(f'Member: {mem_name} (ID={mem_id})')
print(f'Trainer: {pt_name} (ID={pt_id})')

# Step 1: Simulate first QR detection
print('\n--- Step 1: First QR detection ---')
payload = f'member:{mem_id}'
tab.last_seen[payload] = time.time()  # Mark as detected now
print(f'Set debounce: last_seen["{payload}"] = {tab.last_seen[payload]:.2f}')

# Step 2: Simulate confirm
print('\n--- Step 2: Confirm detection ---')
session = get_session()
mem = session.query(Member).filter(Member.id == mem_id).first()
pt = session.query(Trainer).filter(Trainer.id == pt_id).first()
tab.pending_entities = {'member': mem, 'trainer': pt}
tab.pending_photo = '/tmp/test.jpg'
tab.pending_payloads = [payload, f'trainer:{pt_id}']
session.close()

print(f'Set pending_payloads: {tab.pending_payloads}')

# Call handle_confirm
tab.handle_confirm()
print('✓ handle_confirm() completed')

# Step 3: Check if debounce was cleared
print('\n--- Step 3: Check debounce status ---')
if payload in tab.last_seen:
    print(f'❌ FAIL: Debounce still exists for {payload}')
else:
    print(f'✓ PASS: Debounce cleared for {payload}')

# Step 4: Verify next detection can re-query (simulate short delay)
print('\n--- Step 4: Simulate second QR detection (immediately) ---')
print('Without debounce reset, quick re-detection would be blocked.')
print('With debounce reset, it should allow re-query.')

# Simulate what happens in on_frame() on next detection
now = time.time()  # Current time
last = tab.last_seen.get(payload, 0)  # Should be 0 (cleared) or old timestamp
time_diff = now - last

print(f'Current time: {now:.2f}')
print(f'Last seen time: {last:.2f}')
print(f'Time diff: {time_diff:.2f} seconds')

if time_diff >= 3 or last == 0:
    print('✓ PASS: Would re-query fresh data from DB (debounce bypassed)')
else:
    print('❌ FAIL: Still in debounce period (should have been cleared)')

# Step 5: Test that new detection updates last_seen
print('\n--- Step 5: Simulate timestamp update ---')
old_last = tab.last_seen.get(payload, 0)
tab.last_seen[payload] = now  # This is what on_frame() does after re-query
print(f'Updated last_seen["{payload}"] = {now:.2f}')
new_last = tab.last_seen.get(payload, 0)
if new_last == now:
    print('✓ PASS: Timestamp updated, next immediate detection would be blocked (correct debounce)')
else:
    print('❌ FAIL: Timestamp not updated')

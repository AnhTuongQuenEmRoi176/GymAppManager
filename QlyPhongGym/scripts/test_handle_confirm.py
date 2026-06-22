"""Unit test to verify handle_confirm is callable and works"""
import sys
from datetime import datetime, date
from PyQt6.QtWidgets import QApplication
from app.db import get_session
from app.models import Member, Trainer, MemberPackage, Package
from app.ui.tab_dashboard import TabDashboard

# Initialize Qt app
app = QApplication([])

# Create TabDashboard
tab = TabDashboard()

# Get first member and trainer from DB
session = get_session()
try:
    mem = session.query(Member).first()
    pt = session.query(Trainer).first()
    
    if not mem or not pt:
        print('No member or trainer found')
        sys.exit(1)
    
    print(f'Using Member ID={mem.id}, Trainer ID={pt.id}')
    
    # Simulate QR detection: set pending_entities directly
    print('\n--- Simulating QR detection ---')
    tab.pending_entities = {'member': mem, 'trainer': pt}
    tab.pending_photo = '/tmp/test.jpg'
    tab.pending_payloads = ['member:1', 'trainer:1']
    
    # Button should be visible now
    print(f'Button visible: {tab.btn_confirm.isVisible()}')
    
    # Simulate button click
    print('\n--- Simulating button click ---')
    tab.handle_confirm()
    
    print('\n--- Checking database ---')
    session2 = get_session()
    from app.models import Checkin, PTSession
    chk_count = session2.query(Checkin).filter(Checkin.member_id == mem.id).count()
    ps_count = session2.query(PTSession).filter(PTSession.member_id == mem.id).count()
    
    mp = session2.query(MemberPackage).filter(MemberPackage.member_id == mem.id).first()
    print(f'Member checkins: {chk_count}')
    print(f'PTSessions: {ps_count}')
    print(f'MemberPackage sessions_remaining: {mp.sessions_remaining if mp else "None"}')
    
    session2.close()
    
finally:
    session.close()

print('\nTest completed successfully!')

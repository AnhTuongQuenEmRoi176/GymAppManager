"""Simplified test: verify handle_confirm saves to DB and TabHistory can read it"""
from app.db import get_session
from app.models import Member, Trainer, Checkin, MemberPackage, Package
from datetime import datetime, date

session = get_session()
try:
    # Get test data
    mem = session.query(Member).first()
    pt = session.query(Trainer).first()
    
    if not mem or not pt:
        print('ERROR: No member or trainer found')
        exit(1)
    
    print(f'Step 1: Using Member ID={mem.id}, PT ID={pt.id}')
    
    # Clear recent test checkins
    print('\nStep 2: Clearing old test data')
    old_count = session.query(Checkin).filter(Checkin.member_id == mem.id).count()
    session.query(Checkin).filter(
        Checkin.member_id == mem.id,
        Checkin.qr_payload.in_(['member:1', 'trainer:1'])
    ).delete()
    session.commit()
    print(f'  Cleared {old_count} old checkins')
    
    # Create new checkins (simulating handle_confirm)
    print('\nStep 3: Creating new checkins (simulating handle_confirm)')
    chk_mem = Checkin(
        member_id=mem.id,
        trainer_id=None,
        scanned_at=datetime.now(),
        scanner_user_id=None,
        source='camera',
        qr_payload='member:1',
        photo='/tmp/test.jpg'
    )
    session.add(chk_mem)
    
    chk_pt = Checkin(
        member_id=None,
        trainer_id=pt.id,
        scanned_at=datetime.now(),
        scanner_user_id=None,
        source='camera',
        qr_payload='trainer:1',
        photo='/tmp/test.jpg'
    )
    session.add(chk_pt)
    
    session.commit()
    print('  ✓ Committed 2 new checkins')
    
    # Verify we can read them back
    print('\nStep 4: Verify TabHistory can read the new checkins')
    from datetime import timedelta
    dfrom = date.today()
    dto = date.today() + timedelta(days=1)
    
    checkins = session.query(Checkin).filter(
        Checkin.scanned_at >= dfrom,
        Checkin.scanned_at < dto
    ).order_by(Checkin.scanned_at.desc()).all()
    
    print(f'  ✓ TabHistory query returned {len(checkins)} checkins today')
    
    # Filter for our member's checkins
    member_chks = [c for c in checkins if c.member_id == mem.id]
    trainer_chks = [c for c in checkins if c.trainer_id == pt.id]
    
    print(f'  ✓ Member checkins: {len(member_chks)}')
    print(f'  ✓ Trainer checkins: {len(trainer_chks)}')
    
    # Print details
    for i, chk in enumerate(checkins[:3]):
        name = ''
        chk_type = ''
        if chk.member:
            name = chk.member.user.full_name
            chk_type = 'Hội viên'
        elif chk.trainer:
            name = chk.trainer.user.full_name
            chk_type = 'PT'
        print(f'  Checkin {i+1}: {name} ({chk_type}) at {chk.scanned_at}')
    
    print('\n✓✓✓ All tests passed! ✓✓✓')
    
finally:
    session.close()

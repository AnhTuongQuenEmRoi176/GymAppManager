"""Test script to verify handle_confirm logic"""
from datetime import datetime, date, timedelta
from app.db import get_session
from app.models import Member, Trainer, MemberPackage, Package, Checkin, PTSession

session = get_session()
try:
    # Get first member and trainer from DB
    mem = session.query(Member).first()
    pt = session.query(Trainer).first()

    if not mem or not pt:
        print('No member or trainer found in DB')
        session.close()
        exit(1)

    print(f'Testing with Member ID={mem.id} ({mem.user.full_name}), Trainer ID={pt.id} ({pt.user.full_name})')

    # Check if member has active package
    mp = session.query(MemberPackage).filter(
        MemberPackage.member_id == mem.id,
        MemberPackage.end_date >= date.today(),
        MemberPackage.sessions_remaining != None
    ).order_by(MemberPackage.created_at.desc()).first()

    if not mp:
        print('Creating test MemberPackage...')
        pkg = session.query(Package).first()
        if not pkg:
            print('No package found')
            session.close()
            exit(1)
        mp = MemberPackage(
            member_id=mem.id,
            package_id=pkg.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            sessions_remaining=5,
            pt_id=pt.id,
            price_paid=pkg.price
        )
        session.add(mp)
        session.commit()
        print(f'Created MemberPackage: sessions_remaining={mp.sessions_remaining}')
    else:
        print(f'Found MemberPackage: sessions_remaining={mp.sessions_remaining}')

    # Test the logic from handle_confirm
    print('\n--- Simulating handle_confirm ---')
    print(f'Before: sessions_remaining={mp.sessions_remaining}')

    # Create checkins
    chk1 = Checkin(
        member_id=mem.id,
        trainer_id=None,
        scanned_at=datetime.now(),
        scanner_user_id=None,
        source='camera',
        qr_payload='member:1',
        photo='/tmp/test.jpg'
    )
    session.add(chk1)
    print('Created member checkin')

    chk2 = Checkin(
        member_id=None,
        trainer_id=pt.id,
        scanned_at=datetime.now(),
        scanner_user_id=None,
        source='camera',
        qr_payload='trainer:1',
        photo='/tmp/test.jpg'
    )
    session.add(chk2)
    print('Created trainer checkin')

    # Create PTSession and decrement
    ps = PTSession(
        trainer_id=pt.id,
        member_id=mem.id,
        session_date=datetime.now(),
        confirmed_by=None
    )
    session.add(ps)
    print('Created PTSession')

    if mp.sessions_remaining and mp.sessions_remaining > 0:
        mp.sessions_remaining = mp.sessions_remaining - 1
        print(f'Decremented sessions_remaining to {mp.sessions_remaining}')

    session.commit()
    print('\nCommitted successfully!')

    # Query back to verify
    session.expire_all()  # Refresh from DB
    mp_check = session.query(MemberPackage).filter(MemberPackage.id == mp.id).first()
    print(f'After commit: sessions_remaining={mp_check.sessions_remaining}')

    chk_count = session.query(Checkin).count()
    print(f'Total checkins in DB: {chk_count}')

    ps_count = session.query(PTSession).count()
    print(f'Total pt_sessions in DB: {ps_count}')

finally:
    session.close()

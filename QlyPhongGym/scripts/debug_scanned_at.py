"""Debug: check scanned_at format in database"""
from app.db import get_session
from app.models import Checkin
from datetime import datetime, date

session = get_session()
try:
    # Get latest checkins
    checkins = session.query(Checkin).order_by(Checkin.id.desc()).limit(5).all()
    
    print('Latest 5 checkins in DB:')
    for chk in checkins:
        print(f'  ID={chk.id}, scanned_at={chk.scanned_at} (type={type(chk.scanned_at).__name__})')
    
    # Test query with today's date
    print(f'\nToday: {date.today()} (type={type(date.today()).__name__})')
    print(f'Now: {datetime.utcnow()} (type={type(datetime.utcnow()).__name__})')
    
    # Try different query approaches
    from datetime import timedelta
    dfrom = date.today()
    dto = date.today() + timedelta(days=1)
    
    print(f'\nQuery range: {dfrom} to {dto}')
    
    # Direct query
    query1 = session.query(Checkin).filter(
        Checkin.scanned_at >= dfrom,
        Checkin.scanned_at < dto
    ).all()
    print(f'Query 1 (date >= and <): {len(query1)} results')
    
    # Try with datetime start of day
    from datetime import datetime as dt
    start_of_day = dt.combine(date.today(), dt.min.time())
    end_of_day = dt.combine(date.today() + timedelta(days=1), dt.min.time())
    
    query2 = session.query(Checkin).filter(
        Checkin.scanned_at >= start_of_day,
        Checkin.scanned_at < end_of_day
    ).all()
    print(f'Query 2 (datetime >= and <): {len(query2)} results')
    
    # Show raw SQL
    print(f'\nRaw checkins (last 10):')
    for chk in session.query(Checkin).order_by(Checkin.id.desc()).limit(10).all():
        print(f'  {chk.id}: {chk.scanned_at}')
    
finally:
    session.close()

"""Script khởi tạo schema và tạo roles + admin mẫu.

Mô tả:
- Đọc cấu hình DB từ .env (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)
- Nếu database chưa tồn tại, tạo database bằng pymysql
- Sau đó dùng SQLAlchemy để tạo bảng và tạo roles + admin mẫu
"""
import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

from app.db import engine, get_session
from app.models import Base, Role, User, Package, Trainer, Member
from app.auth import hash_password


def ensure_database_exists():
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_NAME = os.getenv('DB_NAME', 'gym_db')

    print(f'Kiểm tra database `{DB_NAME}` trên {DB_HOST}:{DB_PORT}...')
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT, autocommit=True)
        try:
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                print(f'Database `{DB_NAME}` đã tồn tại hoặc được tạo thành công.')
        finally:
            conn.close()
    except Exception as e:
        print('Không thể kết nối tới MySQL server để tạo database:', e)
        raise


def create_sample_data():
    """Tạo dữ liệu mẫu (Packages, Trainers, Members)"""
    session = get_session()
    try:
        # Sample Packages
        if not session.query(Package).filter(Package.name == 'Gói 1 Tháng').first():
            packages = [
                Package(name='Gói 1 Tháng', price=500000, duration_days=30, sessions=12),
                Package(name='Gói 3 Tháng', price=1300000, duration_days=90, sessions=36),
                Package(name='Gói 6 Tháng', price=2400000, duration_days=180, sessions=72),
                Package(name='Gói Vĩnh Viễn', price=5000000, duration_days=36500, sessions=1000),
            ]
            for pkg in packages:
                session.add(pkg)
            session.commit()
            print('Tạo 4 gói tập mẫu.')

        # Sample Trainers
        receptionist_role = session.query(Role).filter(Role.name == 'receptionist').first()
        admin_role = session.query(Role).filter(Role.name == 'admin').first()

        if not session.query(User).filter(User.username == 'pt01').first():
            trainers_data = [
                {'username': 'pt01', 'name': 'Nguyễn Văn A', 'phone': '0901234567', 'specialty': 'Thể hình'},
                {'username': 'pt02', 'name': 'Trần Thị B', 'phone': '0902345678', 'specialty': 'Yoga'},
                {'username': 'pt03', 'name': 'Phạm Văn C', 'phone': '0903456789', 'specialty': 'Cơ tim'},
            ]
            for data in trainers_data:
                user = User(
                    username=data['username'],
                    password_hash=hash_password('123456'),
                    full_name=data['name'],
                    phone=data['phone'],
                    role_id=admin_role.id
                )
                session.add(user)
                session.flush()
                trainer = Trainer(
                    user_id=user.id,
                    specialty=data['specialty'],
                    start_date=datetime.now().date(),
                    base_salary=10000000
                )
                session.add(trainer)
            session.commit()
            print('Tạo 3 PT mẫu.')

        # Sample Members
        if not session.query(User).filter(User.username == 'member01').first():
            members_data = [
                {'username': 'member01', 'name': 'Lê Thị D', 'phone': '0904567890', 'dob': '1998-05-15', 'gender': 'Nữ'},
                {'username': 'member02', 'name': 'Hoàng Văn E', 'phone': '0905678901', 'dob': '1995-08-20', 'gender': 'Nam'},
                {'username': 'member03', 'name': 'Đỗ Thị F', 'phone': '0906789012', 'dob': '2000-01-10', 'gender': 'Nữ'},
                {'username': 'member04', 'name': 'Bùi Văn G', 'phone': '0907890123', 'dob': '1999-03-25', 'gender': 'Nam'},
                {'username': 'member05', 'name': 'Vũ Thị H', 'phone': '0908901234', 'dob': '2001-11-30', 'gender': 'Nữ'},
            ]
            for data in members_data:
                user = User(
                    username=data['username'],
                    password_hash=hash_password('123456'),
                    full_name=data['name'],
                    phone=data['phone'],
                    role_id=receptionist_role.id
                )
                session.add(user)
                session.flush()
                member = Member(
                    user_id=user.id,
                    dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
                    gender=data['gender'],
                    address='Hà Nội',
                    joined_at=datetime.now().date(),
                    status='active'
                )
                session.add(member)
            session.commit()
            print('Tạo 5 hội viên mẫu.')

    except Exception as e:
        session.rollback()
        print(f'Lỗi tạo dữ liệu mẫu: {e}')
    finally:
        session.close()


def init_db():
    ensure_database_exists()

    print('Tạo bảng nếu chưa có...')
    Base.metadata.create_all(bind=engine)
    session = get_session()
    try:
        # Tạo roles mặc định
        if not session.query(Role).filter(Role.name == 'admin').first():
            session.add(Role(name='admin'))
        if not session.query(Role).filter(Role.name == 'receptionist').first():
            session.add(Role(name='receptionist'))
        session.commit()

        # Tạo admin mẫu nếu chưa có
        if not session.query(User).filter(User.username == 'admin').first():
            admin_role = session.query(Role).filter(Role.name == 'admin').first()
            pw = hash_password('admin123')
            admin = User(username='admin', password_hash=pw, full_name='Quản trị viên', role_id=admin_role.id)
            session.add(admin)
            session.commit()
            print('Tạo user admin với username=admin và password=admin123 (demo).')
        else:
            print('User admin đã tồn tại.')
    finally:
        session.close()

    # Tạo dữ liệu mẫu
    create_sample_data()


if __name__ == '__main__':
    init_db()

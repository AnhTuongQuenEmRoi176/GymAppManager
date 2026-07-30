"""Chạy file này một lần tại thư mục QlyPhongGym để thêm model và menu lịch.

Lệnh:
    python apply_windows_schedule_patch.py
"""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "app" / "models.py"
MAIN = ROOT / "app" / "main.py"

MODEL_BLOCK = '''\n\nclass TrainingSchedule(Base):\n    __tablename__ = 'training_schedules'\n    id = Column(Integer, primary_key=True)\n    trainer_id = Column(Integer, ForeignKey('trainers.id'), nullable=False)\n    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)\n    member_package_id = Column(Integer, ForeignKey('member_packages.id'), nullable=True)\n    title = Column(String(200), nullable=False)\n    start_at = Column(DateTime, nullable=False)\n    end_at = Column(DateTime, nullable=False)\n    location = Column(String(200), nullable=True)\n    note = Column(Text, nullable=True)\n    status = Column(String(20), nullable=False, default='upcoming')\n    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)\n    cancelled_by = Column(Integer, ForeignKey('users.id'), nullable=True)\n    cancelled_at = Column(DateTime, nullable=True)\n    created_at = Column(DateTime, default=datetime.utcnow)\n    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)\n\n    trainer = relationship('Trainer')\n    member = relationship('Member')\n    member_package = relationship('MemberPackage')\n'''

PAGE_LINE = '            ("Lịch tập & lịch dạy", "app.ui.tab_schedules", "TabSchedules", False),\n'
ANCHOR = '            ("Lịch sử check-in", "app.ui.tab_history", "TabHistory", False),\n'


def backup(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".schedule_backup")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def patch_models() -> None:
    text = MODELS.read_text(encoding="utf-8-sig")
    if "class TrainingSchedule(Base):" in text:
        print("[SKIP] models.py đã có TrainingSchedule")
        return
    backup(MODELS)
    marker = "\nclass Transaction(Base):"
    if marker not in text:
        raise RuntimeError("Không tìm thấy vị trí class Transaction trong app/models.py")
    text = text.replace(marker, MODEL_BLOCK + marker)
    MODELS.write_text(text, encoding="utf-8")
    print("[OK] Đã thêm TrainingSchedule vào app/models.py")


def patch_main() -> None:
    text = MAIN.read_text(encoding="utf-8-sig")
    if "app.ui.tab_schedules" in text:
        print("[SKIP] main.py đã có tab lịch")
        return
    backup(MAIN)
    if ANCHOR not in text:
        raise RuntimeError("Không tìm thấy dòng Lịch sử check-in trong app/main.py")
    text = text.replace(ANCHOR, ANCHOR + PAGE_LINE)
    MAIN.write_text(text, encoding="utf-8")
    print("[OK] Đã thêm tab Lịch tập & lịch dạy vào app/main.py")


if __name__ == "__main__":
    patch_models()
    patch_main()
    print("Hoàn tất. Tiếp theo import migrations/add_training_schedules.sql nếu DB chưa có bảng.")

from datetime import date

from sqlalchemy.orm import Session

from models import Exchange

SEED_DATA = [
    {
        "book_title": "百年孤独",
        "counterpart_nickname": "小林",
        "sent_date": date(2025, 1, 10),
        "received_date": date(2025, 1, 25),
        "is_completed": True,
    },
    {
        "book_title": "挪威的森林",
        "counterpart_nickname": "阿杰",
        "sent_date": date(2025, 2, 5),
        "received_date": None,
        "is_completed": False,
    },
    {
        "book_title": "三体",
        "counterpart_nickname": "书虫",
        "sent_date": date(2025, 3, 1),
        "received_date": date(2025, 3, 18),
        "is_completed": True,
    },
    {
        "book_title": "活着",
        "counterpart_nickname": "小月",
        "sent_date": date(2025, 4, 12),
        "received_date": None,
        "is_completed": False,
    },
    {
        "book_title": "小王子",
        "counterpart_nickname": "星辰",
        "sent_date": date(2025, 5, 8),
        "received_date": date(2025, 5, 20),
        "is_completed": True,
    },
]


def seed_exchanges(db: Session) -> None:
    if db.query(Exchange).count() > 0:
        return
    for item in SEED_DATA:
        db.add(Exchange(**item))
    db.commit()

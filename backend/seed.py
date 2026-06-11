from datetime import date

from sqlalchemy.orm import Session

from models import Contact, Exchange

SEED_DATA = [
    {
        "book_title": "百年孤独",
        "counterpart_nickname": "小林",
        "sent_date": date(2025, 1, 10),
        "received_date": date(2025, 1, 25),
        "is_completed": True,
        "notes": "精装版，书况良好，小林附赠了手写信",
    },
    {
        "book_title": "挪威的森林",
        "counterpart_nickname": "阿杰",
        "sent_date": date(2025, 2, 5),
        "received_date": None,
        "is_completed": False,
        "notes": "阿杰说两周内寄出回寄",
    },
    {
        "book_title": "三体",
        "counterpart_nickname": "书虫",
        "sent_date": date(2025, 3, 1),
        "received_date": date(2025, 3, 18),
        "is_completed": True,
        "notes": None,
    },
    {
        "book_title": "活着",
        "counterpart_nickname": "小月",
        "sent_date": date(2025, 4, 12),
        "received_date": None,
        "is_completed": False,
        "notes": "等小月期末考试结束后再联系",
    },
    {
        "book_title": "小王子",
        "counterpart_nickname": "星辰",
        "sent_date": date(2025, 5, 8),
        "received_date": date(2025, 5, 20),
        "is_completed": True,
        "notes": "中英双语版，约定下次换科幻类",
    },
]


def seed_exchanges(db: Session) -> None:
    if db.query(Exchange).count() == 0:
        for item in SEED_DATA:
            db.add(Exchange(**item))
        db.commit()
        return
    notes_map = {item["book_title"]: item["notes"] for item in SEED_DATA}
    has_notes_column = hasattr(Exchange, "notes")
    if not has_notes_column:
        return
    updated = False
    for exchange in db.query(Exchange).all():
        if exchange.notes is None and exchange.book_title in notes_map:
            exchange.notes = notes_map[exchange.book_title]
            updated = True
    if updated:
        db.commit()


CONTACT_SEED_DATA = [
    {
        "nickname": "小林",
        "contact_info": "微信: xiaolin_reads",
        "notes": "偏好文学类杂志，每月交换一次",
    },
    {
        "nickname": "阿杰",
        "contact_info": "邮箱: ajie@example.com",
        "notes": "喜欢科幻和哲学类刊物",
    },
    {
        "nickname": "书虫",
        "contact_info": "微信: bookworm_99",
        "notes": None,
    },
]


def seed_contacts(db: Session) -> None:
    if db.query(Contact).count() > 0:
        return
    for item in CONTACT_SEED_DATA:
        db.add(Contact(**item))
    db.commit()

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Contact, Exchange
from schemas import ContactCreate, ContactOut, ContactUpdate, ExchangeCreate, ExchangeOut, ExchangeUpdate, StatisticsOut
from seed import seed_contacts, seed_exchanges

Base.metadata.create_all(bind=engine)


def migrate_database():
    inspector = inspect(engine)
    with engine.begin() as conn:
        exchanges_columns = [col["name"] for col in inspector.get_columns("exchanges")]
        if "notes" not in exchanges_columns:
            conn.execute(text("ALTER TABLE exchanges ADD COLUMN notes VARCHAR(500)"))


app = FastAPI(title="Zine Exchange API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5101", "http://127.0.0.1:5101"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    migrate_database()
    db = SessionLocal()
    try:
        seed_exchanges(db)
        seed_contacts(db)
    finally:
        db.close()


@app.get("/api/exchanges", response_model=list[ExchangeOut])
def list_exchanges(db: Session = Depends(get_db)):
    return db.query(Exchange).order_by(Exchange.id.desc()).all()


@app.get("/api/exchanges/{exchange_id}", response_model=ExchangeOut)
def get_exchange(exchange_id: int, db: Session = Depends(get_db)):
    exchange = db.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="记录不存在")
    return exchange


@app.post("/api/exchanges", response_model=ExchangeOut, status_code=201)
def create_exchange(payload: ExchangeCreate, db: Session = Depends(get_db)):
    exchange = Exchange(**payload.model_dump())
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange


@app.put("/api/exchanges/{exchange_id}", response_model=ExchangeOut)
def update_exchange(
    exchange_id: int, payload: ExchangeUpdate, db: Session = Depends(get_db)
):
    exchange = db.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="记录不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(exchange, key, value)
    db.commit()
    db.refresh(exchange)
    return exchange


@app.delete("/api/exchanges/{exchange_id}", status_code=204)
def delete_exchange(exchange_id: int, db: Session = Depends(get_db)):
    exchange = db.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(exchange)
    db.commit()


@app.get("/api/statistics", response_model=StatisticsOut)
def get_statistics(db: Session = Depends(get_db)):
    total_count = db.query(Exchange).count()
    completed_count = db.query(Exchange).filter(Exchange.is_completed == True).count()
    in_progress_count = total_count - completed_count
    return StatisticsOut(
        total_count=total_count,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
    )


@app.get("/api/contacts", response_model=list[ContactOut])
def list_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).order_by(Contact.id.desc()).all()


@app.get("/api/contacts/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    return contact


@app.post("/api/contacts", response_model=ContactOut, status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@app.put("/api/contacts/{contact_id}", response_model=ContactOut)
def update_contact(
    contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)
):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


@app.delete("/api/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    db.delete(contact)
    db.commit()

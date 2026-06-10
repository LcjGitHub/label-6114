from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Exchange
from schemas import ExchangeCreate, ExchangeOut, ExchangeUpdate
from seed import seed_exchanges

Base.metadata.create_all(bind=engine)

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
    db = SessionLocal()
    try:
        seed_exchanges(db)
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

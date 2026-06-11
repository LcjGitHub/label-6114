from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from database import Base, SessionLocal, engine
from seed import seed_contacts, seed_exchanges
from exchanges import router as exchanges_router
from contacts import router as contacts_router
from labels import router as labels_router

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

app.include_router(exchanges_router)
app.include_router(contacts_router)
app.include_router(labels_router)


@app.on_event("startup")
def on_startup():
    migrate_database()
    db = SessionLocal()
    try:
        seed_exchanges(db)
        seed_contacts(db)
    finally:
        db.close()

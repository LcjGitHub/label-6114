import csv
import io

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import Contact
from schemas import ContactCreate, ContactOut, ContactUpdate, PaginatedOut

router = APIRouter(prefix="/api", tags=["contacts"])


@router.get("/contacts", response_model=PaginatedOut[ContactOut])
def list_contacts(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(default=None, description="搜索关键词，模糊匹配昵称或联系方式"),
    db: Session = Depends(get_db),
):
    query = db.query(Contact)
    if keyword:
        query = query.filter(
            or_(
                Contact.nickname.ilike(f"%{keyword}%"),
                Contact.contact_info.ilike(f"%{keyword}%"),
            )
        )
    total = query.count()
    items = query.order_by(Contact.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedOut(items=items, total=total)


@router.get("/contacts/export")
def export_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).order_by(Contact.id.desc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["昵称", "联系方式", "备注说明"])
    for c in contacts:
        writer.writerow([c.nickname, c.contact_info, c.notes or ""])
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"},
    )


@router.get("/contacts/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    return contact


@router.post("/contacts", response_model=ContactOut, status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.put("/contacts/{contact_id}", response_model=ContactOut)
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


@router.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    db.delete(contact)
    db.commit()

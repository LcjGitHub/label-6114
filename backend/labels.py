from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Label
from schemas import LabelCreate, LabelOut, LabelUpdate, PaginatedOut

router = APIRouter(prefix="/api", tags=["labels"])


@router.get("/labels", response_model=PaginatedOut[LabelOut])
def list_labels(
    keyword: str | None = Query(default=None, description="关键词，匹配标签名称"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    query = db.query(Label)
    if keyword:
        query = query.filter(Label.name.ilike(f"%{keyword}%"))
    total = query.count()
    items = query.order_by(Label.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedOut(items=items, total=total)


@router.get("/labels/all", response_model=list[LabelOut])
def list_all_labels(db: Session = Depends(get_db)):
    return db.query(Label).order_by(Label.id.desc()).all()


@router.get("/labels/{label_id}", response_model=LabelOut)
def get_label(label_id: int, db: Session = Depends(get_db)):
    label = db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="标签不存在")
    return label


@router.post("/labels", response_model=LabelOut, status_code=201)
def create_label(payload: LabelCreate, db: Session = Depends(get_db)):
    existing = db.query(Label).filter(Label.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    label = Label(**payload.model_dump())
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


@router.put("/labels/{label_id}", response_model=LabelOut)
def update_label(label_id: int, payload: LabelUpdate, db: Session = Depends(get_db)):
    label = db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="标签不存在")
    if payload.name and payload.name != label.name:
        existing = db.query(Label).filter(Label.name == payload.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="标签名称已存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(label, key, value)
    db.commit()
    db.refresh(label)
    return label


@router.delete("/labels/{label_id}", status_code=204)
def delete_label(label_id: int, db: Session = Depends(get_db)):
    label = db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="标签不存在")
    db.delete(label)
    db.commit()

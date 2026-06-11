import csv
from datetime import date
from io import StringIO

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
from models import Exchange
from schemas import BatchDeleteIn, ExchangeCreate, ExchangeOut, ExchangeUpdate, ImportResultOut, PaginatedOut, StatisticsOut

router = APIRouter(prefix="/api", tags=["exchanges"])


@router.get("/exchanges", response_model=PaginatedOut[ExchangeOut])
def list_exchanges(
    keyword: str | None = Query(default=None, description="关键词，匹配书名或对方昵称"),
    status: str | None = Query(default=None, description="状态：completed-已完成，in_progress-进行中"),
    sent_date_order: str | None = Query(default=None, description="寄出日期排序：asc-升序，desc-降序"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    query = db.query(Exchange)
    if keyword:
        query = query.filter(
            Exchange.book_title.ilike(f"%{keyword}%")
            | Exchange.counterpart_nickname.ilike(f"%{keyword}%")
        )
    if status == "completed":
        query = query.filter(Exchange.is_completed == True)
    elif status == "in_progress":
        query = query.filter(Exchange.is_completed == False)
    total = query.count()
    if sent_date_order == "asc":
        query = query.order_by(Exchange.sent_date.asc().nulls_last(), Exchange.id.desc())
    elif sent_date_order == "desc":
        query = query.order_by(Exchange.sent_date.desc().nulls_last(), Exchange.id.desc())
    else:
        query = query.order_by(Exchange.id.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedOut(items=items, total=total)


def generate_csv(db: Session):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["书名", "对方昵称", "寄出日期", "收到日期", "是否完成"])
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    exchanges = db.query(Exchange).order_by(Exchange.id.desc()).all()
    for exchange in exchanges:
        writer.writerow([
            exchange.book_title,
            exchange.counterpart_nickname,
            exchange.sent_date.isoformat() if exchange.sent_date else "",
            exchange.received_date.isoformat() if exchange.received_date else "",
            "是" if exchange.is_completed else "否",
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


@router.get("/exchanges/export")
def export_exchanges(db: Session = Depends(get_db)):
    return StreamingResponse(
        generate_csv(db),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=交换记录.csv",
        },
    )


@router.get("/exchanges/{exchange_id}", response_model=ExchangeOut)
def get_exchange(exchange_id: int, db: Session = Depends(get_db)):
    exchange = db.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="记录不存在")
    return exchange


@router.post("/exchanges", response_model=ExchangeOut, status_code=201)
def create_exchange(payload: ExchangeCreate, db: Session = Depends(get_db)):
    exchange = Exchange(**payload.model_dump())
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange


@router.put("/exchanges/{exchange_id}", response_model=ExchangeOut)
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


@router.delete("/exchanges/{exchange_id}", status_code=204)
def delete_exchange(exchange_id: int, db: Session = Depends(get_db)):
    exchange = db.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(exchange)
    db.commit()


@router.post("/exchanges/batch-delete", status_code=204)
def batch_delete_exchanges(payload: BatchDeleteIn, db: Session = Depends(get_db)):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="请选择要删除的记录")
    deleted_count = db.query(Exchange).filter(Exchange.id.in_(payload.ids)).delete(synchronize_session=False)
    db.commit()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到要删除的记录")


@router.get("/statistics", response_model=StatisticsOut)
def get_statistics(db: Session = Depends(get_db)):
    total_count = db.query(Exchange).count()
    completed_count = db.query(Exchange).filter(Exchange.is_completed == True).count()
    in_progress_count = total_count - completed_count
    recent_in_progress = (
        db.query(Exchange)
        .filter(Exchange.is_completed == False)
        .order_by(Exchange.id.desc())
        .limit(5)
        .all()
    )
    return StatisticsOut(
        total_count=total_count,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
        recent_in_progress=recent_in_progress,
    )


REQUIRED_HEADERS = ["书名", "对方昵称", "寄出日期", "收到日期", "是否完成"]


def parse_date(date_str: str) -> date | None:
    if not date_str or date_str.strip() == "":
        return None
    date_str = date_str.strip()
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]:
        try:
            return date.fromisoformat(date_str) if fmt == "%Y-%m-%d" else date.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"日期格式不正确: {date_str}")


def parse_is_completed(value: str) -> bool:
    if not value:
        return False
    value = value.strip()
    if value in ["是", "true", "True", "TRUE", "1", "yes", "Yes"]:
        return True
    if value in ["否", "false", "False", "FALSE", "0", "no", "No", ""]:
        return False
    raise ValueError(f"是否完成格式不正确: {value}")


@router.post("/exchanges/import", response_model=ImportResultOut)
def import_exchanges(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="请上传 CSV 文件")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(StringIO(content))

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV 文件为空或格式不正确")

    headers = [h.strip() for h in reader.fieldnames]
    missing_headers = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing_headers:
        raise HTTPException(
            status_code=400,
            detail=f"CSV 表头缺少必要字段: {', '.join(missing_headers)}",
        )

    success_count = 0
    failure_count = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        try:
            book_title = row.get("书名", "").strip()
            counterpart_nickname = row.get("对方昵称", "").strip()

            if not book_title:
                raise ValueError("书名为空")
            if not counterpart_nickname:
                raise ValueError("对方昵称为空")

            sent_date = parse_date(row.get("寄出日期", ""))
            received_date = parse_date(row.get("收到日期", ""))
            is_completed = parse_is_completed(row.get("是否完成", ""))

            exchange = Exchange(
                book_title=book_title,
                counterpart_nickname=counterpart_nickname,
                sent_date=sent_date,
                received_date=received_date,
                is_completed=is_completed,
            )
            db.add(exchange)
            success_count += 1
        except ValueError as e:
            failure_count += 1
            errors.append(f"第 {row_num} 行: {str(e)}")
        except Exception as e:
            failure_count += 1
            errors.append(f"第 {row_num} 行: 未知错误 - {str(e)}")

    db.commit()

    return ImportResultOut(
        success_count=success_count,
        failure_count=failure_count,
        errors=errors,
    )

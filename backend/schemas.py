from datetime import date

from pydantic import BaseModel, ConfigDict


class ExchangeBase(BaseModel):
    book_title: str
    counterpart_nickname: str
    sent_date: date | None = None
    received_date: date | None = None
    is_completed: bool = False


class ExchangeCreate(ExchangeBase):
    pass


class ExchangeUpdate(BaseModel):
    book_title: str | None = None
    counterpart_nickname: str | None = None
    sent_date: date | None = None
    received_date: date | None = None
    is_completed: bool | None = None


class ExchangeOut(ExchangeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

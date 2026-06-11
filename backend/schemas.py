from datetime import date

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class PaginatedOut(BaseModel, Generic[T]):
    items: list[T]
    total: int

    model_config = ConfigDict(from_attributes=True)


class ExchangeBase(BaseModel):
    book_title: str
    counterpart_nickname: str
    sent_date: date | None = None
    received_date: date | None = None
    is_completed: bool = False
    notes: str | None = None


class ExchangeCreate(ExchangeBase):
    pass


class ExchangeUpdate(BaseModel):
    book_title: str | None = None
    counterpart_nickname: str | None = None
    sent_date: date | None = None
    received_date: date | None = None
    is_completed: bool | None = None
    notes: str | None = None


class ExchangeOut(ExchangeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StatisticsOut(BaseModel):
    total_count: int
    completed_count: int
    in_progress_count: int

    model_config = ConfigDict(from_attributes=True)


class ContactBase(BaseModel):
    nickname: str
    contact_info: str
    notes: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    nickname: str | None = None
    contact_info: str | None = None
    notes: str | None = None


class ContactOut(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

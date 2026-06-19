from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, Union


class SpimexTradingResultSchema(BaseModel):
    exchange_product_id: str
    exchange_product_name: Optional[str] = None
    delivery_basis_name: Optional[str] = None
    volume: int
    total: int
    count: int
    oil_id: Optional[str] = None
    delivery_basis_id: Optional[str] = None
    delivery_type_id: Optional[str] = None
    date: datetime


class SpimexTradingResultResponse(SpimexTradingResultSchema):
    """
    Возвращает полную информацию о торгах вместе с id
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


class TradingDateResponse(BaseModel):
    date: datetime

    model_config = ConfigDict(from_attributes=True)


class TradingDynamicsResponse(BaseModel):
    id: int
    exchange_product_id: str
    exchange_product_name: str
    oil_id: Optional[str] = None
    delivery_type_id: Optional[str] = None
    delivery_basis_id: Optional[str] = None
    delivery_basis_name: str
    volume: int
    total: int
    count: int
    date: Union[date, str]

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class SpimexTradingResult(Base):
    __tablename__ = 'spimex_trading_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    exchange_product_id: Mapped[str] = mapped_column(String(50), nullable=False)
    exchange_product_name: Mapped[str] = mapped_column(String(255))
    delivery_basis_name: Mapped[str] = mapped_column(String(150))

    volume: Mapped[float] = mapped_column(Numeric(15, 2))  # объем торгов
    total: Mapped[float] = mapped_column(Numeric(15, 2))  # общая сумма
    count: Mapped[int] = mapped_column(Integer)  # количество сделок

    oil_id: Mapped[str] = mapped_column(String(50))  # идентификатор нефтяного продукта
    delivery_basis_id: Mapped[str] = mapped_column(String(50))  # базис поставки
    delivery_type_id: Mapped[str] = mapped_column(String(50))  # тип поставки

    date: Mapped[datetime] = mapped_column(DateTime)


Index('ix_spimex_product', SpimexTradingResult.exchange_product_id)
Index('ix_date', SpimexTradingResult.date)
Index('ix_delivery_basis_id', SpimexTradingResult.delivery_basis_id)
Index('ix_delivery_type_id', SpimexTradingResult.delivery_type_id)

"""
Функции для реализации:

GET /api/last-trading-dates – Список дат последних торговых дней (фильтрация по кол-ву последних торговых дней)
GET /api/dynamics – Список торгов за заданный период (фильтрация по oil_id, delivery_type_id, delivery_basis_id, start_date, end_date)
GET /api/trading-results – Список последних торгов (фильтрация по oil_id, delivery_type_id, delivery_basis_id)
"""
from typing import Optional, Sequence

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.models import SpimexTradingResult


class TradingRepository:
    """
    Реализация паттерна Repository
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_last_dates(self, last_days: int):
        """
        Получение списка дат последних торгов
        :param last_days: количество дней для показа
        :return:
        """

        query = (select(SpimexTradingResult.date).distinct().order_by(desc(SpimexTradingResult.date)).limit(last_days))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_dynamics(self, start_date: date, end_date: date, oil_id: Optional[str] = None,
                           delivery_type_id: Optional[str] = None, delivery_basis_id: Optional[str] = None):
        """
        :param start_date: Начальная дата периода
        :param end_date: Конечная дата периода
        :param oil_id: Идентификатор нефтяного продукта
        :param delivery_type_id: Тип поставки
        :param delivery_basis_id: Базис поставки
        :return:
        """
        filters = [
            SpimexTradingResult.date >= start_date,
            SpimexTradingResult.date <= end_date
        ]

        if oil_id is not None:
            filters.append(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id is not None:
            filters.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id is not None:
            filters.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        query = (select(SpimexTradingResult).where(and_(*filters)).order_by(SpimexTradingResult.date.desc()))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_results(self, limit: int, oil_id: Optional[str] = None, delivery_type_id: Optional[str] = None,
                          delivery_basis_id: Optional[str] = None):
        query = select(SpimexTradingResult).order_by(SpimexTradingResult.date.desc())

        if oil_id is not None:
            query = query.where(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id is not None:
            query = query.where(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id is not None:
            query = query.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

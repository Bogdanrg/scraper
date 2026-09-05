from typing import Generic, TypeVar, Optional

from dependency_injector.wiring import inject, Provide
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import DBNotFoundException
from core.shared.db_utils import generate_equality_sql_expression
from db import Base, start_session

import sqlalchemy as sa

SchemaType = TypeVar('SchemaType')


class BaseStorage(Generic[SchemaType]):
    model_cls: type(Base) = None
    schema_cls = None

    @inject
    async def create(self, session: AsyncSession = Provide["session"], **kwargs) -> SchemaType:
        new_entity = self.model_cls(**kwargs)

        async with start_session(session):
            session.add(new_entity)
            await session.flush()
            return self.schema_cls.model_validate(new_entity)

    @inject
    async def get_object(self, session: AsyncSession = Provide["session"], **kwargs) -> SchemaType:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.select(self.model_cls).where(where_condition)

        async with (start_session(session)):
            result = (await session.execute(query)).scalar()

            if result is None:
                raise DBNotFoundException(f'{self.model_cls} not found. Filter kwargs: {kwargs}')

            return self.schema_cls.model_validate(result)

    @inject
    async def list_objects(
            self,
            session: AsyncSession = Provide["session"],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            order_by: Optional[str] = None,
            **kwargs
    ) -> list[SchemaType]:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.select(self.model_cls).where(where_condition)

        if order_by is not None:
            query = query.order_by(sa.text(f'{order_by} desc'))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        async with start_session(session):
            result = (await session.execute(query)).scalars().all()
            return parse_obj_as(list[self.schema_cls], result)


from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar
import sqlalchemy as sa
from dependency_injector.wiring import Provide, inject
from pydantic import TypeAdapter
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import DBNotFoundException
from core.shared.db_utils import generate_equality_sql_expression
from db import Base, start_session

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType")


class BaseStorage(Generic[SchemaType]):
    model_cls: Type[Base] = None
    schema_cls: Type[SchemaType] = None

    @inject
    async def create(
            self,
            session: AsyncSession = Provide["session"],
            **kwargs: Any,
    ) -> SchemaType:
        new_entity = self.model_cls(**kwargs)

        async with start_session(session):
            session.add(new_entity)
            await session.flush()
            return self.schema_cls.model_validate(new_entity)

    @inject
    async def get_object(
            self,
            session: AsyncSession = Provide["session"],
            **kwargs: Any,
    ) -> SchemaType:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.select(self.model_cls).where(where_condition)

        async with start_session(session):
            result = (await session.execute(query)).scalar_one_or_none()

            if result is None:
                raise DBNotFoundException(
                    f"{self.model_cls.__name__} not found. Filter kwargs: {kwargs}"
                )

            return self.schema_cls.model_validate(result)

    @inject
    async def get_or_none(
            self,
            session: AsyncSession = Provide["session"],
            **kwargs: Any,
    ) -> Optional[SchemaType]:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.select(self.model_cls).where(where_condition)

        async with start_session(session):
            result = (await session.execute(query)).scalar_one_or_none()
            if result is None:
                return None
            return self.schema_cls.model_validate(result)

    @inject
    async def list_objects(
            self,
            session: AsyncSession = Provide["session"],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            order_by: Optional[str] = None,
            **kwargs: Any,
    ) -> List[SchemaType]:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.select(self.model_cls).where(where_condition)

        if order_by is not None:
            query = query.order_by(sa.text(f"{order_by} desc"))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        async with start_session(session):
            result = (await session.execute(query)).scalars().all()
            adapter = TypeAdapter(List[self.schema_cls])
            return adapter.validate_python(result)

    @inject
    async def count(
            self,
            session: AsyncSession = Provide["session"],
            **kwargs: Any,
    ) -> int:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.select(sa.func.count()).select_from(self.model_cls).where(where_condition)

        async with start_session(session):
            return (await session.execute(query)).scalar() or 0

    @inject
    async def update(
            self,
            session: AsyncSession = Provide["session"],
            filters: Optional[dict[str, Any]] = None,
            **values: Any,
    ) -> SchemaType:
        filters = filters or {}
        where_condition = generate_equality_sql_expression(self.model_cls, filters)

        query = (
            sa.update(self.model_cls)
            .where(where_condition)
            .values(**values)
            .returning(self.model_cls)
        )

        async with start_session(session):
            result = (await session.execute(query)).scalar_one_or_none()
            if result is None:
                raise DBNotFoundException(
                    f"{self.model_cls.__name__} not found for update. Filters: {filters}"
                )
            return self.schema_cls.model_validate(result)

    @inject
    async def delete(
            self,
            session: AsyncSession = Provide["session"],
            **kwargs: Any,
    ) -> None:
        where_condition = generate_equality_sql_expression(self.model_cls, kwargs)
        query = sa.delete(self.model_cls).where(where_condition)

        async with start_session(session):
            result = await session.execute(query)
            if result.rowcount == 0:
                raise DBNotFoundException(
                    f"{self.model_cls.__name__} not found for deletion. Filters: {kwargs}"
                )

    @inject
    async def bulk_create(
            self,
            items: Sequence[dict[str, Any]],
            session: AsyncSession = Provide["session"],
    ) -> List[SchemaType]:
        if not items:
            return []

        async with start_session(session):
            entities = [self.model_cls(**data) for data in items]
            session.add_all(entities)
            await session.flush()
            adapter = TypeAdapter(List[self.schema_cls])
            return adapter.validate_python(entities)

    @inject
    async def upsert(
            self,
            conflict_targets: Sequence[str],
            values: dict[str, Any],
            update_fields: Optional[Sequence[str]] = None,
            session: AsyncSession = Provide["session"],
    ) -> SchemaType:
        stmt = pg_insert(self.model_cls).values(**values)

        if update_fields:
            set_data = {field: getattr(stmt.excluded, field) for field in update_fields}
            stmt = stmt.on_conflict_do_update(
                index_elements=[getattr(self.model_cls, col) for col in conflict_targets],
                set_=set_data,
            )
        else:
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[getattr(self.model_cls, col) for col in conflict_targets]
            )

        stmt = stmt.returning(self.model_cls)

        async with start_session(session):
            result = (await session.execute(stmt)).scalar_one_or_none()
            if result is None:
                # Если сработал do_nothing и строка не вернулась
                return await self.get_object(
                    session=session,
                    **{k: values[k] for k in conflict_targets},
                )
            return self.schema_cls.model_validate(result)

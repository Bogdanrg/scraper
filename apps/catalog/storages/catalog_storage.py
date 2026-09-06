from datetime import datetime, timezone
from typing import Any, List, Optional
import sqlalchemy as sa
from dependency_injector.wiring import Provide, inject
from pydantic import TypeAdapter
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from apps.catalog.enums import ScrapeStatus
from apps.catalog.models import Book, Category, ScrapeRun
from apps.catalog.schemas import BookSchema
from apps.catalog.schemas.category_schema import CategorySchema
from apps.catalog.schemas.scrap_run_schema import ScrapeRunReadSchema

from core.shared.base_storage import BaseStorage
from db import start_session


class CategoryStorage(BaseStorage[CategorySchema]):
    model_cls = Category
    schema_cls = CategorySchema

    @inject
    async def get_or_create_by_name(
            self,
            name: str,
            slug: str,
            session: AsyncSession = Provide["session"],
    ) -> CategorySchema:
        stmt = (
            pg_insert(self.model_cls)
            .values(name=name, slug=slug)
            .on_conflict_do_nothing(index_elements=[self.model_cls.name])
            .returning(self.model_cls)
        )
        async with start_session(session):
            res = (await session.execute(stmt)).scalar_one_or_none()
            if res is not None:
                return self.schema_cls.model_validate(res)

        return await self.get_object(name=name)


class BookStorage(BaseStorage[BookSchema]):
    model_cls = Book
    schema_cls = BookSchema

    # @inject
    # async def filter_books(
    #         self,
    #         params: BookFilterParams,
    #         session: AsyncSession = Provide["session"],
    # ) -> tuple[List[BookRead], int]:
    #     query = sa.select(self.model_cls).options(sa.orm.joinedload(self.model_cls.category))
    #
    #     if params.query:
    #         query = query.where(self.model_cls.title.ilike(f"%{params.query}%"))
    #     if params.category_id:
    #         query = query.where(self.model_cls.category_id == params.category_id)
    #     if params.category_slug:
    #         query = query.join(self.model_cls.category).where(Category.slug == params.category_slug)
    #     if params.min_price is not None:
    #         query = query.where(self.model_cls.price >= params.min_price)
    #     if params.max_price is not None:
    #         query = query.where(self.model_cls.price <= params.max_price)
    #     if params.rating is not None:
    #         query = query.where(self.model_cls.rating == params.rating)
    #     if params.min_rating is not None:
    #         query = query.where(self.model_cls.rating >= params.min_rating)
    #     if params.in_stock_only:
    #         query = query.where(self.model_cls.availability > 0)
    #
    #     count_query = sa.select(sa.func.count()).select_from(query.subquery())
    #
    #     offset = (params.page - 1) * params.page_size
    #     query = query.limit(params.page_size).offset(offset).order_by(self.model_cls.id.desc())
    #
    #     async with start_session(session):
    #         total = (await session.execute(count_query)).scalar() or 0
    #         books = (await session.execute(query)).scalars().all()
    #         adapter = TypeAdapter(List[self.schema_cls])
    #         return adapter.validate_python(books), total

    @inject
    async def bulk_upsert_books(
            self,
            books_data: List[dict[str, Any]],
            session: AsyncSession = Provide["session"],
    ) -> tuple[int, int]:
        if not books_data:
            return 0, 0

        stmt = pg_insert(self.model_cls).values(books_data)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[self.model_cls.upc],
            set_={
                "title": stmt.excluded.title,
                "price": stmt.excluded.price,
                "availability": stmt.excluded.availability,
                "rating": stmt.excluded.rating,
                "description": stmt.excluded.description,
                "page_url": stmt.excluded.page_url,
                "image_url": stmt.excluded.image_url,
                "category_id": stmt.excluded.category_id,
                "updated_at": sa.func.now(),
            },
        ).returning(self.model_cls.id, (self.model_cls.created_at == stmt.excluded.created_at).label("is_created"))

        async with start_session(session):
            rows = (await session.execute(upsert_stmt)).all()
            created = sum(1 for row in rows if row.is_created)
            updated = len(rows) - created
            return created, updated


class ScrapeRunStorage(BaseStorage[ScrapeRunReadSchema]):
    model_cls = ScrapeRun
    schema_cls = ScrapeRunReadSchema

    async def set_status(
            self,
            run_id: int,
            status: ScrapeStatus,
            error_log: Optional[str] = None,
    ) -> ScrapeRunReadSchema:
        values: dict[str, Any] = {"status": status}
        if status in (ScrapeStatus.COMPLETED, ScrapeStatus.FAILED):
            values["finished_at"] = datetime.now(timezone.utc)
        if error_log:
            values["error_log"] = error_log

        return await self.update(filters={"id": run_id}, **values)

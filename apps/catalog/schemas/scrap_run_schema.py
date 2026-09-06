from datetime import datetime
from typing import Optional

from apps.catalog.enums import ScrapeStatus
from core.schemas import ORMSchema


class ScrapeRunBaseSchema(ORMSchema):
    status: ScrapeStatus
    items_processed: Optional[int] = None
    items_created: Optional[int] = None
    items_updated: Optional[int] = None
    items_failed: Optional[int] = None
    error_log: Optional[str] = None


class ScrapeRunReadSchema(ScrapeRunBaseSchema):
    id: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

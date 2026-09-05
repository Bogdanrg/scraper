from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Enum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.catalog.enums import ScrapeStatus
from db.orm import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[ScrapeStatus] = mapped_column(
        Enum(ScrapeStatus),
        default=ScrapeStatus.PENDING,
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    items_processed: Mapped[int] = mapped_column(Integer, nullable=True)
    items_created: Mapped[int] = mapped_column(Integer, nullable=True)
    items_updated: Mapped[int] = mapped_column(Integer, nullable=True)
    items_failed: Mapped[int] = mapped_column(Integer, nullable=True)

    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ScrapeRun id={self.id} status={self.status.value} processed={self.items_processed}>"

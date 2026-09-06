from core.shared.db_mixins import TimestampMixin
from db.orm import Base
from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    books: Mapped[List["Book"]] = relationship(
        back_populates="category",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name}>"

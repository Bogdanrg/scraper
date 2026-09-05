from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int
    offset: int

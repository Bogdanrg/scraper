from core.schemas.pagination_params import PaginationParams


def get_pagination_params(page: int, per_page: int) -> PaginationParams:
    return PaginationParams(limit=per_page, offset=(page - 1) * per_page)

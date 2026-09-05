from pydantic import BaseModel
from typing import Optional


class ErrorDetails(BaseModel):
    # Default Error model for API
    # Type is key for string
    # ctx is values if needed
    # for instance:
    # type: "general.errors.doesnt_exists"
    # ctx: {"field_name": "First name"}
    type: str
    ctx: Optional[dict] = None

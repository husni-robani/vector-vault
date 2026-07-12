from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake
from typing import TypeVar, Optional, Generic, Any

# T represents dynamic data payload
T = TypeVar('T')

# base response configuration
class BaseResponseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        populate_by_name=True,
        from_attributes=True
    )

# JSON response (application/json)
class PaginationMetadata(BaseResponseModel):
    current_page: int
    per_page: int
    total_items: int
    total_pages: int

class SuccessResponse(BaseResponseModel, Generic[T]):
    message: str = "Success"
    data: Optional[T] = None
    pagination: Optional[PaginationMetadata] = None

class ErrorResponse(BaseResponseModel):
    message: str
    errors: Optional[Any] = None
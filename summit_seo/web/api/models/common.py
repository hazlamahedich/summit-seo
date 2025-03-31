from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Dict, List, Any, Optional

# Define a generic type variable
T = TypeVar('T')

class Pagination(BaseModel):
    """
    Pagination metadata model.
    """
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")

class Meta(BaseModel):
    """
    Metadata model for responses.
    """
    pagination: Optional[Pagination] = Field(None, description="Pagination information")

class StandardResponse(BaseModel, Generic[T]):
    """
    Standard API response format.
    """
    status: str = Field(..., description="Response status")
    data: T = Field(..., description="Response data")
    meta: Optional[Meta] = Field(None, description="Response metadata")

class PaginatedResponse(StandardResponse[List[T]], Generic[T]):
    """
    Paginated response format.
    """
    data: List[T] = Field(..., description="Paginated data")
    meta: Meta = Field(..., description="Response metadata with pagination info")

class ErrorDetails(BaseModel):
    """
    Error details model.
    """
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field({}, description="Additional error details")

class ErrorResponse(BaseModel):
    """
    Error response format.
    """
    status: str = Field("error", description="Error status")
    error: ErrorDetails = Field(..., description="Error details") 
"""
Base model classes for database entities.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from .database import Base

class BaseModel(Base):
    """Base model class with common attributes and methods."""
    
    # Make Base an abstract class
    __abstract__ = True
    
    # Common table name convention
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Primary key as UUID
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )
    
    # Creation timestamp
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        index=True
    )
    
    # Last update timestamp
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Soft delete flag
    is_deleted = Column(
        Boolean, 
        default=False, 
        nullable=False,
        index=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """
        Create model instance from dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary with model data.
            
        Returns:
            Any: New model instance.
        """
        return cls(**data)


class TenantModel(BaseModel):
    """Base model class for multi-tenant entities."""
    
    __abstract__ = True
    
    # Tenant identifier
    tenant_id = Column(
        UUID(as_uuid=True), 
        nullable=False, 
        index=True
    ) 
"""
Base service class for database access operations.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from supabase import Client

from ..core.supabase import get_supabase_client, get_supabase_admin_client

T = TypeVar('T')

class BaseService:
    """
    Base service class for database operations using Supabase.
    
    Provides common functionality for database access and manipulation.
    """
    
    def __init__(self, table_name: str, use_rls_bypass: bool = False):
        """
        Initialize the service with a table name.
        
        Args:
            table_name: Name of the table this service operates on
            use_rls_bypass: Whether to use admin client to bypass Row Level Security
        """
        self.table_name = table_name
        self.use_rls_bypass = use_rls_bypass
    
    def get_client(self) -> Client:
        """
        Get the appropriate Supabase client.
        
        Returns:
            Supabase client instance
        """
        if self.use_rls_bypass:
            return get_supabase_admin_client()
        return get_supabase_client()
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by its ID.
        
        Args:
            id: UUID of the record
            
        Returns:
            Record data or None if not found
        """
        client = self.get_client()
        response = client.table(self.table_name).select("*").eq("id", id).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def list(self, 
                  filters: Optional[Dict[str, Any]] = None, 
                  page: int = 1,
                  page_size: int = 10, 
                  order_by: Optional[str] = None,
                  select_columns: str = "*") -> Dict[str, Any]:
        """
        List records with optional filtering and pagination.
        
        Args:
            filters: Dictionary of column-value pairs to filter on
            page: Page number (1-indexed)
            page_size: Number of records per page
            order_by: Column to order by (prefix with - for descending)
            select_columns: Columns to select (comma-separated list or * for all)
            
        Returns:
            Dictionary with data and pagination information
        """
        client = self.get_client()
        query = client.table(self.table_name).select(select_columns)
        
        # Apply filters
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        
        # Apply pagination
        start = (page - 1) * page_size
        query = query.range(start, start + page_size - 1)
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                query = query.order(order_by[1:], desc=True)
            else:
                query = query.order(order_by)
        
        # Execute query
        response = query.execute()
        
        # Get total count for pagination
        count_query = client.table(self.table_name)
        if filters:
            for column, value in filters.items():
                count_query = count_query.eq(column, value)
        
        count_response = count_query.select("count", count="exact").execute()
        total = count_response.count if hasattr(count_response, 'count') else 0
        
        return {
            "data": response.data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            data: Dictionary of column-value pairs
            
        Returns:
            Created record data
        """
        client = self.get_client()
        response = client.table(self.table_name).insert(data).execute()
        
        if not response.data:
            raise Exception(f"Failed to create record in {self.table_name}")
        
        return response.data[0]
    
    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record by ID.
        
        Args:
            id: UUID of the record
            data: Dictionary of column-value pairs to update
            
        Returns:
            Updated record data
        """
        client = self.get_client()
        response = client.table(self.table_name).update(data).eq("id", id).execute()
        
        if not response.data:
            raise Exception(f"Failed to update record with ID {id} in {self.table_name}")
        
        return response.data[0]
    
    async def delete(self, id: str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: UUID of the record
            
        Returns:
            True if successful
        """
        client = self.get_client()
        response = client.table(self.table_name).delete().eq("id", id).execute()
        
        return len(response.data) > 0 
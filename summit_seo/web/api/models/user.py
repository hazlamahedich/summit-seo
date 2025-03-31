"""
User model for authentication and user management.
"""
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, TenantModel

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    BaseModel.__table_args__[0] if hasattr(BaseModel, '__table_args__') and BaseModel.__table_args__ else BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
)

class Role(BaseModel):
    """Role model for authorization."""
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationship with users
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    # Permissions can be expanded upon later
    # permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class User(BaseModel):
    """User model for authentication and profile management."""
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    # Authentication fields
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile picture
    profile_picture_url = Column(String(255), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    # One-to-many relationship with tenants (if the user is an owner)
    tenants = relationship("Tenant", back_populates="owner", cascade="all, delete-orphan")
    
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_admin(self) -> bool:
        """Check if the user has admin role."""
        return any(role.name == "admin" for role in self.roles)


class Tenant(TenantModel):
    """Tenant model for multi-tenant support."""
    
    # Basic tenant information
    name = Column(String(100), nullable=False)
    domain = Column(String(255), nullable=True, unique=True)
    subdomain = Column(String(50), nullable=True, unique=True)
    
    # Owner relationship (foreign key to User)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    owner = relationship("User", back_populates="tenants")
    
    # Customizations
    logo_url = Column(String(255), nullable=True)
    primary_color = Column(String(10), nullable=True)
    secondary_color = Column(String(10), nullable=True)
    
    # Plan and subscription fields can be added later
    # plan_id = Column(UUID(as_uuid=True), ForeignKey('plan.id'), nullable=True)
    # plan = relationship("Plan")
    
    # Billing fields can be added later
    # subscription_id = Column(String(255), nullable=True)
    # billing_email = Column(String(255), nullable=True)
    
    # Relationships
    # One tenant can have many tenant users
    users = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan")
    # One tenant can have many projects
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")


class TenantUser(TenantModel):
    """Association between users and tenants with specific roles in each tenant."""
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    # user = relationship("User")
    
    # Role in this tenant (owner, admin, member, etc.)
    role = Column(String(50), nullable=False, default="member")
    
    # Tenant relationship
    tenant = relationship("Tenant", back_populates="users")
    
    # Additional permissions specific to this tenant
    can_create_projects = Column(Boolean, default=False)
    can_delete_projects = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    
    __table_args__ = (
        # Composite unique constraint to ensure a user has only one record per tenant
        {'unique': ['tenant_id', 'user_id']}
    ) 
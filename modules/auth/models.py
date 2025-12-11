from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # Email 登录专用的密码字段
    # 对于纯 OAuth 用户，此字段为 NULL
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # 关系：一个用户可以绑定多个 OAuth 账号 (Google, GitHub 等)
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # 外键关联到 User 表
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    
    # OAuth 提供商名称 (e.g., "google", "github")
    oauth_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 第三方平台返回的唯一用户 ID (sub/id)
    oauth_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # 存储 Access Token，使用 Text 类型以防 token 过长
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 可选：如果你还想存 Refresh Token 或过期时间，可以在这里添加
    # refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # expires_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # 反向关系
    user: Mapped["User"] = relationship(back_populates="oauth_accounts")
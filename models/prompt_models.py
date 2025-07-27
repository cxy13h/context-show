"""
提示词追踪系统的数据模型
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, JSON, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
import enum

class SessionStatus(str, enum.Enum):
    """会话状态枚举"""
    active = "active"
    completed = "completed"
    error = "error"

class PromptType(str, enum.Enum):
    """提示词类型枚举"""
    init = "init"                # 初始化提示词
    user_input = "user_input"    # 用户输入
    system_marker = "system_marker"  # 系统标记（Start/End）
    llm_output = "llm_output"    # LLM输出

# SQLAlchemy 模型
class SessionModel(Base):
    """会话数据库模型"""
    __tablename__ = "sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    session_id = Column(String(64), nullable=False, unique=True, comment="会话ID")
    initial_prompt = Column(Text, nullable=False, comment="初始提示词模板")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    status = Column(Enum(SessionStatus), default=SessionStatus.active, comment="会话状态")

class PromptModel(Base):
    """提示词记录数据库模型"""
    __tablename__ = "prompts"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    session_id = Column(String(64), nullable=False, comment="会话ID")
    type = Column(Enum(PromptType), nullable=False, comment="提示词类型")
    prompt = Column(Text, nullable=False, comment="完整提示词内容")
    timestamp = Column(DateTime, default=datetime.utcnow, comment="创建时间")

class ToolCallModel(Base):
    """工具调用记录数据库模型"""
    __tablename__ = "tool_calls"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    session_id = Column(String(64), nullable=False, comment="会话ID")
    prompt_id = Column(BigInteger, nullable=False, comment="对应的提示词ID")
    tool_name = Column(String(100), nullable=False, comment="工具名称")
    arguments = Column(JSON, comment="调用参数")
    description = Column(Text, comment="工具描述")

# Pydantic 模型
class SessionCreate(BaseModel):
    """创建会话的请求模型"""
    session_id: str
    initial_prompt: str

class PromptCreate(BaseModel):
    """创建提示词的请求模型"""
    session_id: str
    type: PromptType
    prompt: str

class SessionResponse(BaseModel):
    """会话响应模型"""
    id: int
    session_id: str
    initial_prompt: str
    created_at: datetime
    updated_at: datetime
    status: SessionStatus

    class Config:
        from_attributes = True

class PromptResponse(BaseModel):
    """提示词响应模型"""
    id: int
    session_id: str
    type: PromptType
    prompt: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ToolCallResponse(BaseModel):
    """工具调用响应模型"""
    id: int
    session_id: str
    prompt_id: int
    tool_name: str
    arguments: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

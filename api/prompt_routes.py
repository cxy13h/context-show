"""
提示词追踪系统的API路由 - 重新设计版本
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from database import get_db
from core.prompt_tracker import PromptTracker
from models.prompt_models import (
    SessionModel, PromptModel, ToolCallModel,
    SessionResponse, PromptResponse, ToolCallResponse,
    PromptType
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()
prompt_tracker = PromptTracker()

# 请求模型
class CreateSessionRequest(BaseModel):
    session_id: str
    initial_prompt: Optional[str] = None

class AddUserInputRequest(BaseModel):
    session_id: str
    user_input: str

class AddSystemMarkerRequest(BaseModel):
    session_id: str
    reason: str

class AddLLMOutputRequest(BaseModel):
    session_id: str
    llm_output: str

@router.post("/sessions")
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """
    创建新会话并初始化提示词
    """
    try:
        result = prompt_tracker.create_session(
            session_id=request.session_id,
            initial_prompt=request.initial_prompt,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"创建会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/user-input")
async def add_user_input(
    session_id: str,
    request: AddUserInputRequest,
    db: Session = Depends(get_db)
):
    """
    添加用户输入到提示词
    """
    try:
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="URL中的session_id与请求体中的不一致")
        
        result = prompt_tracker.add_user_input(
            session_id=session_id,
            user_input=request.user_input,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"添加用户输入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/system-marker")
async def add_system_marker(
    session_id: str,
    request: AddSystemMarkerRequest,
    db: Session = Depends(get_db)
):
    """
    添加系统标记到提示词
    """
    try:
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="URL中的session_id与请求体中的不一致")
        
        result = prompt_tracker.add_system_marker(
            session_id=session_id,
            reason=request.reason,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"添加系统标记失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/llm-output")
async def add_llm_output(
    session_id: str,
    request: AddLLMOutputRequest,
    db: Session = Depends(get_db)
):
    """
    添加LLM输出到提示词
    """
    try:
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="URL中的session_id与请求体中的不一致")
        
        result = prompt_tracker.add_llm_output(
            session_id=session_id,
            llm_output=request.llm_output,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"添加LLM输出失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/current-prompt")
async def get_current_prompt(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    获取会话的当前完整提示词
    """
    try:
        current_prompt = prompt_tracker.get_current_prompt(session_id, db)
        
        if current_prompt is None:
            raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
        
        return {
            "session_id": session_id,
            "current_prompt": current_prompt,
            "prompt_length": len(current_prompt)
        }
        
    except Exception as e:
        logger.error(f"获取当前提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    status: Optional[str] = Query(None, description="会话状态过滤"),
    db: Session = Depends(get_db)
):
    """
    获取会话列表
    """
    try:
        query = db.query(SessionModel)
        
        if status:
            query = query.filter(SessionModel.status == status)
        
        sessions = query.order_by(desc(SessionModel.updated_at)).offset(skip).limit(limit).all()
        
        return sessions
        
    except Exception as e:
        logger.error(f"获取会话列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    获取会话详情
    """
    try:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
        
        return session
        
    except Exception as e:
        logger.error(f"获取会话详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/prompts", response_model=List[PromptResponse])
async def get_prompts(
    session_id: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    prompt_type: Optional[str] = Query(None, description="提示词类型过滤"),
    db: Session = Depends(get_db)
):
    """
    获取会话的提示词历史
    """
    try:
        query = db.query(PromptModel).filter(PromptModel.session_id == session_id)
        
        if prompt_type:
            query = query.filter(PromptModel.type == prompt_type)
        
        prompts = query.order_by(PromptModel.id).offset(skip).limit(limit).all()
        
        return prompts
        
    except Exception as e:
        logger.error(f"获取提示词历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/tool-calls", response_model=List[ToolCallResponse])
async def get_tool_calls(
    session_id: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    db: Session = Depends(get_db)
):
    """
    获取会话的工具调用记录
    """
    try:
        tool_calls = db.query(ToolCallModel).filter(
            ToolCallModel.session_id == session_id
        ).order_by(desc(ToolCallModel.id)).offset(skip).limit(limit).all()
        
        return tool_calls
        
    except Exception as e:
        logger.error(f"获取工具调用记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """
    获取系统统计信息
    """
    try:
        # 会话统计
        total_sessions = db.query(func.count(SessionModel.id)).scalar()
        active_sessions = db.query(func.count(SessionModel.id)).filter(
            SessionModel.status == "active"
        ).scalar()
        
        # 提示词统计
        total_prompts = db.query(func.count(PromptModel.id)).scalar()
        
        # 按类型统计
        prompt_type_stats = {}
        for prompt_type in PromptType:
            count = db.query(func.count(PromptModel.id)).filter(
                PromptModel.type == prompt_type
            ).scalar()
            prompt_type_stats[prompt_type.value] = count
        
        # 工具调用统计
        total_tool_calls = db.query(func.count(ToolCallModel.id)).scalar()
        
        return {
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
                "completed": total_sessions - active_sessions
            },
            "prompts": {
                "total": total_prompts,
                "by_type": prompt_type_stats
            },
            "tool_calls": {
                "total": total_tool_calls
            }
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

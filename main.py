#!/usr/bin/env python3
"""
提示词追踪系统 - 主应用
"""
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database import init_database
from api.prompt_routes import router as prompt_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="提示词追踪系统",
    description="透明化的LLM提示词变化管理系统",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(prompt_router, prefix="/api/v1", tags=["提示词追踪"])

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "提示词追踪系统",
        "description": "透明化的LLM提示词变化管理系统",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "prompt-tracker",
        "version": "2.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    try:
        logger.info("正在初始化数据库...")
        init_database()
        logger.info("数据库初始化完成")
        logger.info(f"应用启动成功，监听地址: {settings.API_HOST}:{settings.API_PORT}")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应用正在关闭...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

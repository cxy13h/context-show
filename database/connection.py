"""
数据库连接管理
"""
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy基类
Base = declarative_base()

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            return
        
        try:
            # 创建数据库引擎
            self.engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                echo=settings.API_DEBUG,
                pool_pre_ping=True,  # 连接前检查连接是否有效
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 测试连接
            self.test_connection()
            
            self._initialized = True
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("数据库连接测试成功")
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            raise
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self._initialized:
            self.initialize()
        return self.SessionLocal()
    
    def create_tables(self):
        """创建数据库表"""
        if not self._initialized:
            self.initialize()
        
        try:
            # 读取并执行SQL脚本
            import os
            sql_file = os.path.join(os.path.dirname(__file__), "schema.sql")
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割SQL语句并执行
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with self.engine.connect() as conn:
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                conn.commit()
            
            logger.info("数据库表创建成功")
            
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")

# 全局数据库管理器实例
db_manager = DatabaseManager()

def get_db() -> Session:
    """获取数据库会话的依赖注入函数"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库"""
    db_manager.initialize()
    db_manager.create_tables()

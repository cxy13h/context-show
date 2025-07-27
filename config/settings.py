"""
配置文件
"""
import os
from typing import Optional

class Settings:
    """应用配置类"""
    
    # 数据库配置
    DB_HOST: str = "101.126.145.194"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Ll@2120516678"
    DB_NAME: str = "prompt_tracker"
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        from urllib.parse import quote_plus
        # 对密码进行URL编码，处理特殊字符
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    @classmethod
    def from_env(cls) -> "Settings":
        """从环境变量创建配置"""
        settings = cls()
        
        # 从环境变量覆盖配置
        settings.DB_HOST = os.getenv("DB_HOST", settings.DB_HOST)
        settings.DB_PORT = int(os.getenv("DB_PORT", settings.DB_PORT))
        settings.DB_USER = os.getenv("DB_USER", settings.DB_USER)
        settings.DB_PASSWORD = os.getenv("DB_PASSWORD", settings.DB_PASSWORD)
        settings.DB_NAME = os.getenv("DB_NAME", settings.DB_NAME)
        
        settings.API_HOST = os.getenv("API_HOST", settings.API_HOST)
        settings.API_PORT = int(os.getenv("API_PORT", settings.API_PORT))
        settings.API_DEBUG = os.getenv("API_DEBUG", "true").lower() == "true"
        
        settings.LOG_LEVEL = os.getenv("LOG_LEVEL", settings.LOG_LEVEL)
        
        return settings

# 全局配置实例
settings = Settings.from_env()

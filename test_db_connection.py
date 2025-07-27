#!/usr/bin/env python3
"""
测试数据库连接
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymysql
from config.settings import settings

def test_direct_connection():
    """直接测试数据库连接"""
    print("=" * 60)
    print("测试数据库连接")
    print("=" * 60)
    
    print(f"主机: {settings.DB_HOST}")
    print(f"端口: {settings.DB_PORT}")
    print(f"用户: {settings.DB_USER}")
    print(f"密码: {settings.DB_PASSWORD}")
    print(f"数据库: {settings.DB_NAME}")
    print()
    
    try:
        print("正在连接数据库...")
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4'
        )
        
        print("✅ 数据库连接成功！")
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL版本: {version[0]}")
            
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            db_names = [db[0] for db in databases]
            
            if settings.DB_NAME in db_names:
                print(f"✅ 数据库 '{settings.DB_NAME}' 已存在")
            else:
                print(f"⚠️  数据库 '{settings.DB_NAME}' 不存在，需要创建")
                
                # 创建数据库
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ 数据库 '{settings.DB_NAME}' 创建成功")
        
        connection.close()
        print("✅ 数据库连接测试完成")
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False
    
    return True

def test_sqlalchemy_connection():
    """测试SQLAlchemy连接"""
    print("\n" + "=" * 60)
    print("测试SQLAlchemy连接")
    print("=" * 60)
    
    try:
        from sqlalchemy import create_engine, text
        
        print(f"连接URL: {settings.database_url}")
        
        engine = create_engine(settings.database_url, echo=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ SQLAlchemy连接成功: {result.fetchone()}")
            
    except Exception as e:
        print(f"❌ SQLAlchemy连接失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Context Show - 数据库连接测试")
    print()
    
    # 测试直接连接
    direct_ok = test_direct_connection()
    
    if direct_ok:
        # 测试SQLAlchemy连接
        sqlalchemy_ok = test_sqlalchemy_connection()
        
        if sqlalchemy_ok:
            print("\n🎉 所有数据库连接测试通过！")
        else:
            print("\n⚠️  SQLAlchemy连接测试失败")
    else:
        print("\n❌ 基础数据库连接失败，请检查配置")

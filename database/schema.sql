-- 重新设计的数据库结构 - 提示词追踪系统

-- 创建数据库
CREATE DATABASE IF NOT EXISTS prompt_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE prompt_tracker;

-- 会话表
CREATE TABLE IF NOT EXISTS sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话ID',
    initial_prompt LONGTEXT NOT NULL COMMENT '初始提示词模板',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    status ENUM('active', 'completed', 'error') DEFAULT 'active' COMMENT '会话状态',
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- 提示词记录表
CREATE TABLE IF NOT EXISTS prompts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    type ENUM('init', 'user_input', 'system_marker', 'llm_output') NOT NULL COMMENT '提示词类型',
    prompt LONGTEXT NOT NULL COMMENT '完整提示词内容',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_session_id (session_id),
    INDEX idx_type (type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词记录表';

-- 工具调用记录表
CREATE TABLE IF NOT EXISTS tool_calls (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    prompt_id BIGINT NOT NULL COMMENT '对应的提示词ID',
    tool_name VARCHAR(100) NOT NULL COMMENT '工具名称',
    arguments JSON COMMENT '调用参数',
    description TEXT COMMENT '工具描述',
    INDEX idx_session_id (session_id),
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_tool_name (tool_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工具调用记录表';

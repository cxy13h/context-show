"""
提示词追踪系统核心逻辑 - 重新设计版本
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from models.prompt_models import (
    SessionModel, PromptModel, ToolCallModel,
    SessionCreate, PromptCreate, PromptType
)

logger = logging.getLogger(__name__)

class PromptTracker:
    """提示词追踪器"""
    
    def __init__(self):
        self.default_initial_prompt = """你是一个全能的AI助手，你能做到任何事情，包括编码、文本生成、交流聊天等。同时你也可以使用你所拥有的工具Tool。
你所拥有的Tool工具有:
quark_search: Call this tool to interact with the 夸克搜索 API. What is the 夸克搜索 API useful for? 夸克搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。 Parameters: [{"name": "search_query", "description": "搜索关键词或短语", "required": true, "schema": {"type": "string"}}] Format the arguments as a JSON object.
image_gen: Call this tool to interact with the 通义万相 API. What is the 通义万相 API useful for? 通义万相是一个AI绘画（图像生成）服务，输入文本描述，返回根据文本作画得到的图片的URL Parameters: [{"name": "query", "description": "中文关键词，描述了希望图像具有什么内容", "required": true, "schema": {"type": "string"}}] Format the arguments as a JSON object.

你有以下几个状态:
UserInput:用户的输入内容（只能由用户输入给你，你本身严禁生成）
Thought:深度思考（对用户的输入、Agent客户端的输入做出深度的思考，并决定接下来应该做什么）
UserInteraction:需要用户反馈或补充信息
Action:打算使用的工具
ActionInput:打算使用的工具的入参
Observation:工具的返回结果（由Agent客户端执行工具后输入给你，你本身严禁生成）
FinalAsnwer:经过深思熟虑后的最终回答

每个状态分别按照以下格式输出：
<UserInput>用户的输入</UserInput>
<Thought>深度思考的内容</Thought>
<UserInteraction>需要用户反馈或补充的内容</UserInteraction>
<Action><ToolName>打算调用的工具名称</ToolName><Description>工具的作用</Description></Action>
<ActionInput><ToolName>工具名称</ToolName><Arguments>工具入参</Arguments></ActionInput>
<Observation>工具执行返回的结果</Observation>
<FinalAsnwer>经过深思熟虑后的最终回答</FinalAsnwer>

除此之外，你还有额外的两个状态，分别代表一次输出的开始和结束:
<Start><SessionId>123456</SessionId><Reason>本次输出开始的原因</Reason></Start>
<End><Reason>本次输出结束的原因</Reason></End>
注意:本次输出开始的原因，可能源于有用户有输入，也可能源于Agent客户端有输入,分别对应UserInput和Observation;Start状态是由Agent客户端在识别开始原因后主动输入给你的，你本身严禁生成!
本次输出结束的原因，可能是接下来需要Agent客户端调用工具，或者是需要用户反馈或补充内容，也可能是已经给出最终答案了可以自然结束本次输出，分别对应ActionInput、UserInteaction和FinalAsnwer。
你也可以根据start和end来判断你已经经历了几次对话了。

Begin!!!"""
    
    def create_session(self, session_id: str, initial_prompt: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        """
        创建新会话并初始化提示词
        """
        try:
            # 使用提供的初始提示词或默认模板
            prompt = initial_prompt or self.default_initial_prompt
            
            # 检查会话是否已存在
            existing_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if existing_session:
                return {
                    "success": False,
                    "error": f"会话 {session_id} 已存在"
                }
            
            # 创建会话
            session = SessionModel(
                session_id=session_id,
                initial_prompt=prompt
            )
            db.add(session)
            db.flush()  # 获取session.id
            
            # 记录初始提示词
            initial_prompt_record = PromptModel(
                session_id=session_id,
                type=PromptType.init,
                prompt=prompt
            )
            db.add(initial_prompt_record)
            db.flush()  # 获取prompt.id
            
            db.commit()
            
            logger.info(f"会话 {session_id} 创建成功")
            
            return {
                "success": True,
                "session_id": session_id,
                "session_db_id": session.id,
                "prompt_id": initial_prompt_record.id,
                "initial_prompt_length": len(prompt)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建会话失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_user_input(self, session_id: str, user_input: str, db: Session) -> Dict[str, Any]:
        """
        添加用户输入到提示词
        """
        try:
            # 获取最新的提示词状态
            latest_prompt = db.query(PromptModel).filter(
                PromptModel.session_id == session_id
            ).order_by(PromptModel.id.desc()).first()
            
            if not latest_prompt:
                return {
                    "success": False,
                    "error": "找不到会话的提示词历史"
                }
            
            # 构建新的完整提示词
            new_prompt = latest_prompt.prompt + "\n" + f"<UserInput>{user_input}</UserInput>"
            
            # 记录新的提示词状态
            new_prompt_record = PromptModel(
                session_id=session_id,
                type=PromptType.user_input,
                prompt=new_prompt
            )
            db.add(new_prompt_record)
            db.flush()
            
            db.commit()
            
            logger.info(f"会话 {session_id} 添加用户输入成功")
            
            return {
                "success": True,
                "session_id": session_id,
                "prompt_id": new_prompt_record.id,
                "new_prompt_length": len(new_prompt)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"添加用户输入失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_system_marker(self, session_id: str, reason: str, db: Session) -> Dict[str, Any]:
        """
        添加系统标记（Start/End）到提示词
        """
        try:
            # 获取最新的提示词状态
            latest_prompt = db.query(PromptModel).filter(
                PromptModel.session_id == session_id
            ).order_by(PromptModel.id.desc()).first()
            
            if not latest_prompt:
                return {
                    "success": False,
                    "error": "找不到会话的提示词历史"
                }
            
            # 构建新的完整提示词
            marker = f"<Start><SessionId>{session_id}</SessionId><Reason>{reason}</Reason></Start>"
            new_prompt = latest_prompt.prompt + "\n" + marker
            
            # 记录新的提示词状态
            new_prompt_record = PromptModel(
                session_id=session_id,
                type=PromptType.system_marker,
                prompt=new_prompt
            )
            db.add(new_prompt_record)
            db.flush()
            
            db.commit()
            
            logger.info(f"会话 {session_id} 添加系统标记成功")
            
            return {
                "success": True,
                "session_id": session_id,
                "prompt_id": new_prompt_record.id,
                "new_prompt_length": len(new_prompt)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"添加系统标记失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_llm_output(self, session_id: str, llm_output: str, db: Session) -> Dict[str, Any]:
        """
        添加LLM输出到提示词
        """
        try:
            # 获取最新的提示词状态
            latest_prompt = db.query(PromptModel).filter(
                PromptModel.session_id == session_id
            ).order_by(PromptModel.id.desc()).first()
            
            if not latest_prompt:
                return {
                    "success": False,
                    "error": "找不到会话的提示词历史"
                }
            
            # 构建新的完整提示词
            new_prompt = latest_prompt.prompt + "\n" + llm_output
            
            # 记录新的提示词状态
            new_prompt_record = PromptModel(
                session_id=session_id,
                type=PromptType.llm_output,
                prompt=new_prompt
            )
            db.add(new_prompt_record)
            db.flush()
            
            # 提取工具调用信息
            tool_calls = self._extract_tool_calls(llm_output)
            for tool_call in tool_calls:
                tool_call_record = ToolCallModel(
                    session_id=session_id,
                    prompt_id=new_prompt_record.id,
                    tool_name=tool_call["tool_name"],
                    arguments=tool_call["arguments"],
                    description=tool_call.get("description")
                )
                db.add(tool_call_record)
            
            db.commit()
            
            logger.info(f"会话 {session_id} 添加LLM输出成功")
            
            return {
                "success": True,
                "session_id": session_id,
                "prompt_id": new_prompt_record.id,
                "new_prompt_length": len(new_prompt),
                "tool_calls_extracted": len(tool_calls)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"添加LLM输出失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_prompt(self, session_id: str, db: Session) -> Optional[str]:
        """
        获取会话的当前完整提示词
        """
        try:
            latest_prompt = db.query(PromptModel).filter(
                PromptModel.session_id == session_id
            ).order_by(PromptModel.id.desc()).first()
            
            return latest_prompt.prompt if latest_prompt else None
            
        except Exception as e:
            logger.error(f"获取当前提示词失败: {e}")
            return None
    
    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取工具调用信息"""
        tool_calls = []
        
        # 提取Action信息
        action_pattern = r'<Action><ToolName>(.*?)</ToolName><Description>(.*?)</Description></Action>'
        action_matches = re.findall(action_pattern, text, re.DOTALL)
        
        # 提取ActionInput信息
        action_input_pattern = r'<ActionInput><ToolName>(.*?)</ToolName><Arguments>(.*?)</Arguments></ActionInput>'
        action_input_matches = re.findall(action_input_pattern, text, re.DOTALL)
        
        # 合并Action和ActionInput信息
        for i, (tool_name, description) in enumerate(action_matches):
            tool_call = {
                "tool_name": tool_name.strip(),
                "description": description.strip(),
                "arguments": {}
            }
            
            # 查找对应的ActionInput
            for input_tool_name, arguments_str in action_input_matches:
                if input_tool_name.strip() == tool_name.strip():
                    try:
                        tool_call["arguments"] = json.loads(arguments_str.strip())
                    except json.JSONDecodeError:
                        tool_call["arguments"] = {"raw": arguments_str.strip()}
                    break
            
            tool_calls.append(tool_call)
        
        return tool_calls

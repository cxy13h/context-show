#!/usr/bin/env python3
"""
提示词追踪系统演示

展示如何追踪LLM提示词的动态变化过程
"""
import requests
import json
import time

def print_separator(title=""):
    """打印分隔线"""
    print("=" * 80)
    if title:
        print(f" {title} ".center(80, "="))
        print("=" * 80)

def wait_for_server(base_url="http://localhost:8000", timeout=30):
    """等待服务器启动"""
    print("⏳ 等待服务器启动...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                print("✅ 服务器已启动！")
                return True
        except:
            pass
        time.sleep(1)
    
    print("❌ 服务器启动超时")
    return False

def demo_prompt_tracking():
    """演示提示词追踪功能"""
    
    base_url = "http://localhost:8000"
    import random
    session_id = f"demo_session_{random.randint(1000, 9999)}"
    
    print_separator("提示词追踪系统演示")
    print("展示LLM提示词的动态变化过程")
    print()
    
    # 1. 创建会话并初始化提示词
    print("1️⃣ 创建会话并初始化提示词...")
    try:
        response = requests.post(f"{base_url}/api/v1/sessions", json={
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 会话创建成功！")
            print(f"   🆔 会话ID: {result['session_id']}")
            print(f"   📝 初始提示词长度: {result['initial_prompt_length']} 字符")
            print(f"   🔄 提示词ID: {result['prompt_id']}")
        else:
            print(f"❌ 创建失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 2. 添加用户输入
    print("\n2️⃣ 添加用户输入...")
    user_input = "现在给我画个五彩斑斓的黑"
    try:
        response = requests.post(f"{base_url}/api/v1/sessions/{session_id}/user-input", json={
            "session_id": session_id,
            "user_input": user_input
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 用户输入添加成功！")
            print(f"   📏 新提示词长度: {result['new_prompt_length']} 字符")
            print(f"   🔄 提示词ID: {result['prompt_id']}")
        else:
            print(f"❌ 添加失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 3. 添加系统标记
    print("\n3️⃣ 添加系统标记...")
    try:
        response = requests.post(f"{base_url}/api/v1/sessions/{session_id}/system-marker", json={
            "session_id": session_id,
            "reason": "UserInput"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 系统标记添加成功！")
            print(f"   📏 新提示词长度: {result['new_prompt_length']} 字符")
            print(f"   🔄 提示词ID: {result['prompt_id']}")
        else:
            print(f"❌ 添加失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 4. 添加LLM输出
    print("\n4️⃣ 添加LLM输出...")
    llm_output = """<Thought>用户希望画一个五彩斑斓的黑色，我应该使用通义万相API来生成一张五彩斑斓的黑的图片。</Thought>
<Action><ToolName>image_gen</ToolName><Description>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Description></Action>
<ActionInput><ToolName>image_gen</ToolName><Arguments>{"query": "五彩斑斓的黑"}</Arguments></ActionInput>
<End><Reason>ActionInput</Reason></End>"""
    
    try:
        response = requests.post(f"{base_url}/api/v1/sessions/{session_id}/llm-output", json={
            "session_id": session_id,
            "llm_output": llm_output
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM输出添加成功！")
            print(f"   📏 新提示词长度: {result['new_prompt_length']} 字符")
            print(f"   🔄 提示词ID: {result['prompt_id']}")
            print(f"   🔧 提取的工具调用: {result['tool_calls_extracted']} 个")
        else:
            print(f"❌ 添加失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 5. 查看当前完整提示词
    print("\n5️⃣ 查看当前完整提示词...")
    try:
        response = requests.get(f"{base_url}/api/v1/sessions/{session_id}/current-prompt")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 当前提示词获取成功！")
            print(f"   📏 总长度: {result['prompt_length']} 字符")
            print(f"   📝 提示词预览（前200字符）:")
            print(f"   {result['current_prompt'][:200]}...")
        else:
            print(f"❌ 获取失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 6. 查看提示词变化历史
    print("\n6️⃣ 查看提示词历史...")
    try:
        response = requests.get(f"{base_url}/api/v1/sessions/{session_id}/prompts")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ 提示词历史获取成功！共 {len(prompts)} 条记录:")

            for prompt in prompts:
                print(f"   🔄 ID {prompt['id']}: {prompt['type']}")
                print(f"      ⏰ 时间: {prompt['timestamp']}")
                print(f"      📏 总长度: {len(prompt['prompt'])} 字符")
                print()
        else:
            print(f"❌ 获取失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 7. 查看工具调用记录
    print("7️⃣ 查看工具调用记录...")
    try:
        response = requests.get(f"{base_url}/api/v1/sessions/{session_id}/tool-calls")
        
        if response.status_code == 200:
            tool_calls = response.json()
            print(f"✅ 工具调用记录获取成功！共 {len(tool_calls)} 个:")
            
            for tool_call in tool_calls:
                print(f"   🔧 工具: {tool_call['tool_name']}")
                print(f"      📝 描述: {tool_call['description']}")
                print(f"      ⚙️ 参数: {json.dumps(tool_call['arguments'], ensure_ascii=False)}")
                print(f"      🔄 提示词ID: {tool_call['prompt_id']}")
                print()
        else:
            print(f"❌ 获取失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 8. 查看系统统计
    print("8️⃣ 查看系统统计...")
    try:
        response = requests.get(f"{base_url}/api/v1/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 系统统计:")
            print(f"   📊 总会话数: {stats['sessions']['total']}")
            print(f"   🔄 活跃会话: {stats['sessions']['active']}")
            print(f"   📝 总提示词记录: {stats['prompts']['total']}")
            print(f"   🔧 总工具调用: {stats['tool_calls']['total']}")

            print(f"\n   📈 按提示词类型统计:")
            for prompt_type, count in stats['prompts']['by_type'].items():
                print(f"      {prompt_type}: {count} 次")
        else:
            print(f"❌ 获取失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主函数"""
    
    print("🚀 提示词追踪系统演示")
    print("展示透明化的LLM提示词变化管理")
    print()
    
    if wait_for_server():
        demo_prompt_tracking()
        
        print_separator("演示完成")
        print("🎉 提示词追踪系统演示完成！")
        print()
        print("💡 系统功能总结:")
        print("   ✅ 追踪每次提示词的变化")
        print("   ✅ 记录完整的提示词历史")
        print("   ✅ 自动提取工具调用信息")
        print("   ✅ 分析用户交互模式")
        print("   ✅ 提供详细的统计数据")
        print()
        print("🌐 API文档: http://localhost:8000/docs")
        print("📊 现在您可以完全透明地看到LLM提示词的变化过程！")
    else:
        print("❌ 无法连接到服务器")
        print("   请先启动服务: python main.py")

if __name__ == "__main__":
    main()

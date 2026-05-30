import os,json
from openai import OpenAI

# ---------------- 配置 ----------------
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("请先设置 DEEPSEEK_API_KEY 环境变量")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
####

# ---------------- 基础 API 调用 ----------------
def call_api(user_input,system_prompt=None, model="deepseek-v4-pro", json_format=False, json_schema=None,temperature=None,max_tokens=None):
    """
    普通对话 / JSON 格式调用
    json_format=False -> 普通文本
    json_format=True  -> JSON 对象输出
    返回: dict 包含结果 + token 使用情况
    """
    response_format = None
    if json_schema is not None:
        response_format = {"type": "json_object", "schema": json_schema}
    elif json_format:
        response_format = {"type": "json_object"}
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_input})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "response_format": response_format,
        "max_tokens":max_tokens,
        'reasoning_effort':"high",
        'extra_body':{"thinking": {"type": "enabled"}}
    }
    resp = client.chat.completions.create(**payload)
    msg = resp.choices[0].message
    usage = resp.usage
    tokens = {
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    }
    #result = msg.content if response_format else {"reasoning": getattr(msg, "reasoning_content", None), "answer": msg.content}
    result ={"reasoning": getattr(msg, "reasoning_content", None), "answer": msg.content}
    return {"result": result, "tokens": tokens, 'prompt': (user_input,system_prompt)}

def call_tool(user_input, tools,system_prompt=None,model="deepseek-v4-pro"):
    """
    Tool call 风格接口，返回工具调用信息（JSON） + token 使用
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_input})
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,        # 可动态传入工具列表
        "tool_choice": "auto",
        'reasoning_effort':"high",
        'extra_body':{"thinking": {"type": "enabled"}}
    }

    resp = client.chat.completions.create(**payload)
    msg = resp.choices[0].message
    usage = resp.usage
    tokens = {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens, "total_tokens": usage.total_tokens}
    # 判断是否有工具调用
    if getattr(msg, "tool_calls", None):
        result = [{"name": c.function.name, "arguments": json.loads(c.function.arguments)} for c in msg.tool_calls]
        success = True
    else:
        result = msg.content or "无工具调用，返回对话内容"
        success = False
    return {"success": success, "result": result, "tokens": tokens, 'prompt': (user_input,system_prompt)}

# ---------------- 测试接口 ----------------
if __name__ == "__main__":
    # Tool call
    with open("tools_list.json", "r",encoding="utf-8")as f:
        tools_data = json.load(f)
    print("=== Tool call ===")
    print(call_tool("请生成工具调用，执行 read_file 读取 example.txt",tools =tools_data))
    # 普通对话
    print("=== 普通对话 ===")
    print(call_api("请简单介绍沈阳故宫"))

    # JSON 格式输出
    print("=== JSON 输出 ===")
    print(call_api("生成工具调用 JSON，调用 read_file 读取 example.txt", json_format=True))
    
    # JSON Schema格式输出，不是很灵，这个。
    weather_schema = {
        "type": "object",
        "properties": {"city": {"type": "string"}, "temperature": {"type": "number"}, "condition": {"type": "string"}},
        "required": ["city", "temperature", "condition"]
        }
    print("=== JSON Schema格式输出 ===")
    print(call_api("请以json格式从以下文本提取天气信息：今天杭州天气很好，温度大约25度，湿度适中", json_schema=weather_schema))


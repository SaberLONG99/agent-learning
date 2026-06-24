import json
import os
from datetime import datetime

from openai import OpenAI

# 创建deepseek客户端
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 保留永久记忆文件
CURRENT_DIR = os.path.dirname(__file__)
MEMORY_FILE = os.path.join(CURRENT_DIR, "memory.json")


def get_current_time():
    """获取电脑当前时间"""
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


def calculate(operation, a, b):
    """
    对啊，b进行计算
    :param operation: 计算方式
    :param a: 数字a
    :param b: 数字b
    :return:
    """
    if operation == 'add':
        return a + b

    if operation == 'subtract':
        return a - b

    if operation == 'multiply':
        return a * b

    if operation == 'divide':
        if b == 0:
            return "错误：除数不能为0"

        return a / b

    return f"错误：不支持操作{operation}"


def load_memory():
    """
    读取永久记忆
    :return:
    """
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_memory(key, value):
    """
    保存记忆
    :param key:
    :param value:
    :return:
    """
    memory = load_memory()
    memory[key] = value
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=2)
    return f"已经记住：{key} = {value}"


def read_memory():
    """读取全部长期记忆。"""

    # 返回 Python 字典
    return load_memory()


def execute_tool(function_name, arguments):
    """
    根据工具名称执行相应的 Python 函数。

    :param function_name: 函数名
    :param arguments: 函数入参
    :return:
    """
    if function_name == "get_current_time":
        return get_current_time()

    if function_name == "calculate":
        return calculate(
            operation=arguments["operation"],
            a=arguments["a"],
            b=arguments["b"]
        )

    if function_name == "save_memory":
        return save_memory(
            key=arguments["key"],
            value=arguments["value"]
        )

    if function_name == "read_memory":
        return read_memory()

    return f"错误：找不到工具{function_name}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取用户电脑当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行两个数字之间的加减乘除运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide"
                        ],
                        "description": "需要执行的数学运算"
                    },
                    "a": {
                        "type": "number",
                        "description": "参与计算的第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "参与计算的第二数字"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "当用户要求记住某件信息时，将信息保存到长期记忆。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "记忆的名称，例如：姓名、爱好。"
                    },
                    "value": {
                        "type": "string",
                        "description": "需要保存的具体内容。"
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_memory",
            "description": "读取以前保存的长期记忆",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "你是一位智能助手。"
            "涉及当前日期、时间或数学计算时必须调用工具，不能猜测。"
            "用户明确要求记住信息时，必须调用 save_memory。"
            "用户询问以前保存的信息时，必须调用 read_memory。"
            "不能假装已经保存或读取了信息。"
        )
    }
]

while True:
    user_input = input("\n你：").strip()

    if user_input.lower() in {"exit", "quit"}:
        print("对话结束")
        break

    if not user_input:
        continue

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        if not assistant_message.tool_calls:
            print(f"\n助手：{assistant_message.content}")
            break

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            print(f"\n[调用工具] {function_name}, 参数：{arguments}")

            try:
                tool_result = execute_tool(function_name, arguments)
            except Exception as e:
                tool_result = f"工具执行失败：{e}"

            tool_result = str(tool_result)
            print(f"[工具结果] {tool_result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                }
            )

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from openai import OpenAI

# 创建deepseek客户端
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 保留永久记忆文件
CURRENT_DIR = os.path.dirname(__file__)
MEMORY_FILE = os.path.join(CURRENT_DIR, "memory.json")

# 知识库文件路径
KNOWLEDGE_DIR = os.path.join(CURRENT_DIR, "knowledge")

# Agent日志文件
LOG_FILE = os.path.join(CURRENT_DIR, "agent.log")

# 每次用户提问，Agent 最多行动 5 次
MAX_AGENT_STEPS = 5


def get_current_time():
    """获取电脑当前时间"""
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


def get_time_by_timezone(timezone):
    """
    根据当前时区获取当前时间

    :param timezone: 时区名称，例如 Asia/Shanghai 表示中国时间
    :return: 指定时区的当前时间字符串
    """
    now = datetime.now(ZoneInfo(timezone))
    return now.strftime("%Y年%m月%d日 %H:%M:%S")


def calculate(operation, a, b):
    """
    对a，b进行计算
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


def write_log(message):
    """
    写日志

    :param message:
    :return:
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{now}] {message}\n")


def search_knowledge(query):
    """
    从本地知识库文件knowledge.txt中查询相关内容

    :param query: 用户问题里的关键词
    :return: 搜索到的知识库内容
    """
    if not os.path.exists(KNOWLEDGE_DIR):
        return "知识库文件目录knowledge不存在。"

    query_lower = query.lower()

    keywords = []

    stop_words = ["我的", "有哪些", "是什么", "是啥", "请问", "一下", "帮我", "查询", "搜索"]

    for word in query_lower.split():
        word = word.strip()
        if not word:
            continue

        if word in stop_words:
            continue

        keywords.append(word)

    # 如果用户输入的是中文，很多时候没有空格；
    # 所以这里额外把整句里常见的重要词手动识别出来
    important_words = ["agent", "项目", "方向", "学习", "目标", "deepseek", "python", "知识库", "助手", "日报", "周报", "研究"]
    for word in important_words:
        if word in query_lower and word not in keywords:
            keywords.append(word)

    if not keywords:
        keywords = [query_lower]

    # scored_results 用来保存：每一行命中了多少关键词
    scored_results = []

    for filename in os.listdir(KNOWLEDGE_DIR):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        paragraphs = content.split("\n\n")

        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            paragraph_text = paragraph.strip()

            if not paragraph_text:
                continue

            paragraph_lines = paragraph.splitlines()
            title = paragraph_lines[0].strip()
            body = "".join(paragraph_lines[1:]).strip()
            if not body:
                body = title

            paragraph_lower = paragraph_text.lower()

            score = 0
            for keyword in keywords:
                if keyword in paragraph_lower:
                    score += 1

            # 命中至少 1 个关键词，就保存
            if score > 0:
                scored_results.append(
                    {
                        "score": score,
                        "filename": filename,
                        "paragraph_index": paragraph_index,
                        "title": title,
                        "body": body
                    }
                )

    if not scored_results:
        return "没有在知识库中找到相关内容。"

    scored_results.sort(key=lambda x: x["score"], reverse=True)
    top_results = scored_results[:5]

    # 把文件名、行号、正文都返回，方便知道来源
    result_texts = []

    for item in top_results:
        result_texts.append(
            f"来源：{item['filename']} 第{item['paragraph_index']}段\n"
            f"标题：{item['title']}\n"
            f"内容：{item['body']}"
        )

    return "\n\n".join(result_texts)


def execute_tool(function_name, arguments):
    """
    根据工具名称执行相应的 Python 函数。

    :param function_name: 函数名
    :param arguments: 函数入参
    :return:
    """
    if function_name == "get_current_time":
        return get_current_time()

    if function_name == "get_time_by_timezone":
        return get_time_by_timezone(
            timezone=arguments["timezone"]
        )

    if function_name == "calculate":
        return calculate(
            operation=arguments["operation"],
            a=arguments["a"],
            b=arguments["b"]
        )

    if function_name == "save_memory":
        print(f"\nAgent 想保存记忆："
              f"{arguments['key']} = {arguments['value']}")
        confirmation = input("是否允许？（y/n）：").strip().lower()
        if confirmation == 'y':
            return save_memory(
                key=arguments["key"],
                value=arguments["value"]
            )
        # 告诉模型操作被用户拒绝
        return "用户拒绝保存这条记忆"

    if function_name == "read_memory":
        return read_memory()

    if function_name == "search_knowledge":
        return search_knowledge(query=arguments["query"])

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
    },
    {
        "type": "function",
        "function": {
            "name": "get_time_by_timezone",
            "description": "获取指定时区的当前时间。北京、上海、中国时间都使用 Asia/Shanghai。",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "enum": [
                            "Asia/Shanghai",
                            "Asia/Tokyo",
                            "Europe/London",
                            "America/New_York"
                        ],
                        "description": "IANA 时区名称。北京/上海/中国时间使用 Asia/Shanghai。"
                    }
                },
                "required": ["timezone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "从本地 knowledge 知识库中检索与用户问题相关的信息。如果返回没有找到相关内容，助手必须停止回答，不能自行补充。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用于检索知识库的关键词，例如：学习目标、项目方向、DeepSeek"
                    }
                },
                "required": ["query"]
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
            "如果用户询问某个城市或地区的当前时间，必须调用 get_time_by_timezone。"
            "北京、上海、中国时间对应 Asia/Shanghai。"
            "用户明确要求记住信息时，必须调用 save_memory。"
            "用户询问以前保存的信息时，必须调用 read_memory。"
            "当用户询问本地资料、知识库、项目方向、学习目标等信息时，必须调用 search_knowledge。"
            "回答知识库相关问题时，必须基于 search_knowledge 的工具结果回答。"
            "回答末尾必须写明来源，例如：来源：project_ideas.txt 第2段。"
            "如果 search_knowledge 第一次没有找到内容，你可以换一个更短、更核心的关键词再搜索一次。"
            "如果第二次仍然没有找到，必须停止并告诉用户知识库中没有相关资料。"
            "这种情况下禁止补充自己的常识、禁止介绍其他能力、禁止推荐其他内容。"
            "除非用户明确说'不用知识库'或'根据常识回答'，否则不能脱离知识库回答。"
            "知识库问答要保持可追溯，不能编造来源。"
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

    write_log(f"用户输入：{user_input}")

    step_count = 0
    knowledge_miss_count = 0
    while step_count < MAX_AGENT_STEPS:
        step_count += 1
        print(f"\n[Agent 步骤 {step_count}/{MAX_AGENT_STEPS}]")

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tools
            )
        except Exception as e:
            print(f"\nAPI 请求失败：{e}")
            break

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        should_stop = False
        if not assistant_message.tool_calls:
            print(f"\n助手：{assistant_message.content}")
            write_log(f"助手回答：{assistant_message.content}")
            break

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            print(f"\n[调用工具] {function_name}, 参数：{arguments}")
            write_log(f"[调用工具] {function_name}, 参数：{arguments}")

            try:
                tool_result = execute_tool(function_name, arguments)
            except Exception as e:
                tool_result = f"工具执行失败：{e}"
                write_log(f"[工具执行失败] {function_name}：{e}")

            tool_result = str(tool_result)
            write_log(f"[工具结果] {tool_result}")

            if function_name == "search_knowledge" and "没有在知识库中找到相关内容" in tool_result:
                knowledge_miss_count += 1

                if knowledge_miss_count < 2:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": (
                                "没有在知识库中找到相关内容。"
                                "请换一个更短、更核心的关键词重新调用 search_knowledge。"
                            )
                        }
                    )
                    continue

                # 第二次没找到，也必须先补上 tool 消息
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "没有在知识库中找到相关内容。"
                    }
                )

                print("\n助手：知识库中没有找到相关资料。")
                write_log("助手回答：知识库中没有找到相关资料")
                should_stop = True
                break

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                }
            )

        if should_stop:
            break

# 这里保存所有工具的 JSON Schema。
# 这些 schema 不是 Python 真正执行的函数，
# 而是告诉大模型：有哪些工具、每个工具需要什么参数。

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
                        "description": "参与计算的第二个数字"
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
            "description": (
                "从本地 knowledge 知识库中检索与用户问题相关的信息。"
                "如果返回没有找到相关内容，助手必须停止回答，不能自行补充。"
            ),
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
    },
    {
        "type": "function",
        "function": {
            "name": "make_todo_list",
            "description": "把用户给出的多个任务整理成编号待办清单。",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "任务列表，例如：['学习 Agent', '写日报', '复习 Python']"
                    }
                },
                "required": ["tasks"]
            }
        }
    }
]

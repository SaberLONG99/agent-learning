import json
import os

from config import MEMORY_FILE


def load_memory():
    """
    读取长期记忆。

    :return: 记忆字典，例如 {"姓名": "小明"}
    """

    # 如果 memory.json 还不存在，说明没有保存过记忆
    if not os.path.exists(MEMORY_FILE):
        return {}

    # 读取 JSON 文件，并转成 Python 字典
    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_memory(key, value):
    """
    保存一条长期记忆。

    :param key: 记忆名称，例如 姓名、家乡、爱好
    :param value: 记忆内容
    :return: 给 Agent 的工具结果
    """

    # 先读取旧记忆
    memory = load_memory()

    # 写入或覆盖一条记忆
    memory[key] = value

    # 保存回 memory.json
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=2)

    return f"已经记住：{key} = {value}"


def read_memory():
    """
    读取全部长期记忆。

    :return: 全部记忆字典
    """

    return load_memory()

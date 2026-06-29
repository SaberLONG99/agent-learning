from datetime import datetime
from zoneinfo import ZoneInfo

from knowledge_base import search_knowledge
from memory_store import read_memory, save_memory


def get_current_time():
    """
    获取电脑当前时间。

    :return: 当前时间字符串
    """

    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


def get_time_by_timezone(timezone):
    """
    根据指定时区获取当前时间。

    :param timezone: 时区名称，例如 Asia/Shanghai 表示中国时间
    :return: 指定时区的当前时间字符串
    """

    now = datetime.now(ZoneInfo(timezone))
    return now.strftime("%Y年%m月%d日 %H:%M:%S")


def calculate(operation, a, b):
    """
    对 a、b 进行加减乘除计算。

    :param operation: 计算方式，add/subtract/multiply/divide
    :param a: 第一个数字
    :param b: 第二个数字
    :return: 计算结果
    """

    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            return "错误：除数不能为 0"

        return a / b

    return f"错误：不支持操作 {operation}"


def execute_tool(function_name, arguments):
    """
    根据模型请求的工具名称，执行对应的 Python 函数。

    :param function_name: 工具名称
    :param arguments: 工具参数字典
    :return: 工具执行结果
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
        print(
            f"\nAgent 想保存记忆："
            f"{arguments['key']} = {arguments['value']}"
        )

        confirmation = input("是否允许？（y/n）：").strip().lower()

        if confirmation == "y":
            return save_memory(
                key=arguments["key"],
                value=arguments["value"]
            )

        return "用户拒绝保存这条记忆"

    if function_name == "read_memory":
        return read_memory()

    if function_name == "search_knowledge":
        return search_knowledge(
            query=arguments["query"]
        )

    return f"错误：找不到工具 {function_name}"

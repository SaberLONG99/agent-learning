from datetime import datetime

from config import LOG_FILE


def write_log(message):
    """
    把日志写入 agent.log 文件。

    :param message: 要写入日志文件的一行文本
    :return: None
    """

    # 获取当前时间，方便以后排查问题
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 使用追加模式写入日志；如果文件不存在，Python 会自动创建
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{now}] {message}\n")
